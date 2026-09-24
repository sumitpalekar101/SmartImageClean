"""
ImageCleaner Image Metadata.

This module extracts reusable metadata from validated images.
The metadata can be consumed by image-quality detectors,
reports, and other processing components.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from imagecleaner.core.dataset_loader import ImageRecord
from imagecleaner.exceptions.custom_exceptions import ImageValidationError
from imagecleaner.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class ImageMetadata:
    """
    Immutable metadata representation of an image.

    Attributes:
        image: Original ImageRecord.
        width: Image width in pixels.
        height: Image height in pixels.
        file_size_bytes: File size in bytes.
        image_format: Detected image format.
        mode: Image color mode.
        aspect_ratio: Width divided by height.
        megapixels: Total number of pixels expressed in megapixels.
    """

    image: ImageRecord
    width: int
    height: int
    file_size_bytes: int
    image_format: str
    mode: str
    aspect_ratio: float
    megapixels: float

    @property
    def dimensions(self) -> tuple[int, int]:
        """Return image dimensions as width and height."""
        return self.width, self.height


class ImageMetadataExtractor:
    """
    Extract metadata from image files.

    This class does not perform quality analysis. It only extracts
    reusable image information.
    """

    def extract(
        self,
        image: ImageRecord,
    ) -> ImageMetadata:
        """
        Extract metadata from an image.

        Args:
            image: ImageRecord produced by DatasetLoader.

        Returns:
            ImageMetadata containing image properties.

        Raises:
            ImageValidationError: If the supplied image record
                is invalid or the image cannot be read.
        """
        self._validate_image_record(image)

        image_path = Path(image.path)

        logger.debug(
            "Extracting metadata: %s",
            image_path,
        )

        try:
            file_size_bytes = image_path.stat().st_size

            with Image.open(image_path) as opened_image:
                width, height = opened_image.size
                image_format = opened_image.format or image.extension
                mode = opened_image.mode

        except (OSError, ValueError) as error:
            message = (
                f"Unable to extract image metadata "
                f"from '{image_path}': {error}"
            )

            logger.warning(message)

            raise ImageValidationError(message) from error

        if width <= 0 or height <= 0:
            message = (
                f"Image has invalid dimensions: "
                f"{image_path} ({width}x{height})"
            )

            logger.warning(message)

            raise ImageValidationError(message)

        aspect_ratio = width / height
        megapixels = (width * height) / 1_000_000

        metadata = ImageMetadata(
            image=image,
            width=width,
            height=height,
            file_size_bytes=file_size_bytes,
            image_format=image_format,
            mode=mode,
            aspect_ratio=aspect_ratio,
            megapixels=megapixels,
        )

        logger.debug(
            "Metadata extracted: %s (%dx%d, %.2f MP)",
            image_path,
            width,
            height,
            megapixels,
        )

        return metadata

    @staticmethod
    def _validate_image_record(
        image: ImageRecord,
    ) -> None:
        """
        Validate the supplied ImageRecord.

        Args:
            image: ImageRecord to validate.

        Raises:
            ImageValidationError: If the object is invalid.
        """
        if not isinstance(image, ImageRecord):
            raise ImageValidationError(
                "ImageMetadataExtractor expects an ImageRecord."
            )

        if not image.path:
            raise ImageValidationError(
                "ImageRecord contains an empty image path."
            )