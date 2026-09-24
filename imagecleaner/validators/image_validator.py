"""
ImageCleaner Image Validation.

This module validates image files before they are passed to
image-quality detectors or other processing components.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from imagecleaner.core.dataset_loader import ImageRecord
from imagecleaner.exceptions.custom_exceptions import (
    ImageValidationError,
)
from imagecleaner.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class ImageValidationResult:
    """
    Result produced after validating an image.

    Attributes:
        image: Original image record.
        is_valid: Whether the image passed validation.
        width: Image width in pixels, if readable.
        height: Image height in pixels, if readable.
        image_format: Detected image format, if readable.
        mode: Pillow image mode, if readable.
        error: Validation error message, if validation failed.
    """

    image: ImageRecord
    is_valid: bool
    width: int | None = None
    height: int | None = None
    image_format: str | None = None
    mode: str | None = None
    error: str | None = None


class ImageValidator:
    """
    Validate image files using Pillow.

    The validator checks whether an image exists, can be opened,
    can be verified, and can be fully decoded.
    """

    def validate(
        self,
        image: ImageRecord,
    ) -> ImageValidationResult:
        """
        Validate a single image.

        Args:
            image: ImageRecord produced by DatasetLoader.

        Returns:
            ImageValidationResult containing validation details.

        Raises:
            ImageValidationError: If the supplied image record is invalid.
        """
        self._validate_image_record(image)

        logger.debug(
            "Validating image: %s",
            image.path,
        )

        try:
            return self._validate_image(image)

        except (
            FileNotFoundError,
            PermissionError,
            OSError,
            UnidentifiedImageError,
        ) as error:
            message = (
                f"Unable to validate image "
                f"'{image.path}': {error}"
            )

            logger.warning(message)

            return ImageValidationResult(
                image=image,
                is_valid=False,
                error=message,
            )

    def _validate_image(
        self,
        image: ImageRecord,
    ) -> ImageValidationResult:
        """
        Perform the actual Pillow-based image validation.

        Args:
            image: ImageRecord to validate.

        Returns:
            Validation result.
        """
        image_path = Path(image.path)

        if not image_path.exists():
            return ImageValidationResult(
                image=image,
                is_valid=False,
                error=f"File does not exist: {image_path}",
            )

        if not image_path.is_file():
            return ImageValidationResult(
                image=image,
                is_valid=False,
                error=f"Path is not a file: {image_path}",
            )

        try:
            with Image.open(image_path) as opened_image:
                image_format = opened_image.format
                width, height = opened_image.size
                mode = opened_image.mode

                opened_image.verify()

            with Image.open(image_path) as decoded_image:
                decoded_image.load()

                width, height = decoded_image.size
                image_format = decoded_image.format
                mode = decoded_image.mode

        except (
            UnidentifiedImageError,
            OSError,
        ) as error:
            message = (
                f"Image is corrupted or unreadable: "
                f"{image_path} ({error})"
            )

            logger.warning(message)

            return ImageValidationResult(
                image=image,
                is_valid=False,
                error=message,
            )

        if width <= 0 or height <= 0:
            message = (
                f"Image has invalid dimensions: "
                f"{image_path} ({width}x{height})"
            )

            logger.warning(message)

            return ImageValidationResult(
                image=image,
                is_valid=False,
                width=width,
                height=height,
                image_format=image_format,
                mode=mode,
                error=message,
            )

        logger.debug(
            "Image validation successful: %s (%dx%d, %s)",
            image_path,
            width,
            height,
            image_format,
        )

        return ImageValidationResult(
            image=image,
            is_valid=True,
            width=width,
            height=height,
            image_format=image_format,
            mode=mode,
        )

    @staticmethod
    def _validate_image_record(
        image: ImageRecord,
    ) -> None:
        """
        Validate the ImageRecord supplied to the validator.

        Args:
            image: ImageRecord to validate.

        Raises:
            ImageValidationError: If the record is invalid.
        """
        if not isinstance(image, ImageRecord):
            raise ImageValidationError(
                "ImageValidator expects an ImageRecord."
            )

        if not image.path:
            raise ImageValidationError(
                "ImageRecord contains an empty image path."
            )