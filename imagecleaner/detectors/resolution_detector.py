"""
ImageCleaner Resolution Detection.

This module evaluates image resolution using reusable image
metadata. It determines whether an image meets configured
minimum width, height, and megapixel requirements.
"""

from __future__ import annotations

from dataclasses import dataclass

from imagecleaner.core.image_metadata import ImageMetadata
from imagecleaner.exceptions.custom_exceptions import ImageProcessingError
from imagecleaner.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class ResolutionDetectionResult:
    """
    Result produced by the resolution detector.

    Attributes:
        image: Metadata associated with the analyzed image.
        is_low_resolution: Whether the image fails the configured
            resolution requirements.
        width: Image width in pixels.
        height: Image height in pixels.
        megapixels: Total image resolution in megapixels.
        minimum_width: Minimum accepted width.
        minimum_height: Minimum accepted height.
        minimum_megapixels: Minimum accepted megapixels.
    """

    image: ImageMetadata
    is_low_resolution: bool
    width: int
    height: int
    megapixels: float
    minimum_width: int
    minimum_height: int
    minimum_megapixels: float

    @property
    def meets_width_requirement(self) -> bool:
        """Return whether the image meets the width requirement."""
        return self.width >= self.minimum_width

    @property
    def meets_height_requirement(self) -> bool:
        """Return whether the image meets the height requirement."""
        return self.height >= self.minimum_height

    @property
    def meets_megapixel_requirement(self) -> bool:
        """Return whether the image meets the megapixel requirement."""
        return self.megapixels >= self.minimum_megapixels

    @property
    def meets_requirements(self) -> bool:
        """Return whether all configured requirements are satisfied."""
        return not self.is_low_resolution


class ResolutionDetector:
    """
    Detect insufficient image resolution.

    An image is considered low resolution when it fails at least
    one of the configured minimum requirements.
    """

    def __init__(
        self,
        minimum_width: int = 640,
        minimum_height: int = 480,
        minimum_megapixels: float = 0.3,
    ) -> None:
        """
        Initialize the resolution detector.

        Args:
            minimum_width: Minimum accepted image width in pixels.
            minimum_height: Minimum accepted image height in pixels.
            minimum_megapixels: Minimum accepted image resolution
                in megapixels.

        Raises:
            ValueError: If any requirement is invalid.
        """
        if minimum_width <= 0:
            raise ValueError(
                "minimum_width must be greater than zero."
            )

        if minimum_height <= 0:
            raise ValueError(
                "minimum_height must be greater than zero."
            )

        if minimum_megapixels <= 0:
            raise ValueError(
                "minimum_megapixels must be greater than zero."
            )

        self._minimum_width = minimum_width
        self._minimum_height = minimum_height
        self._minimum_megapixels = minimum_megapixels

        logger.debug(
            "ResolutionDetector initialized: "
            "width=%d, height=%d, megapixels=%.2f",
            minimum_width,
            minimum_height,
            minimum_megapixels,
        )

    @property
    def minimum_width(self) -> int:
        """Return the minimum accepted width."""
        return self._minimum_width

    @property
    def minimum_height(self) -> int:
        """Return the minimum accepted height."""
        return self._minimum_height

    @property
    def minimum_megapixels(self) -> float:
        """Return the minimum accepted megapixel value."""
        return self._minimum_megapixels

    def detect(
        self,
        metadata: ImageMetadata,
    ) -> ResolutionDetectionResult:
        """
        Analyze image resolution using existing metadata.

        Args:
            metadata: ImageMetadata produced by
                ImageMetadataExtractor.

        Returns:
            ResolutionDetectionResult containing the resolution
            assessment.

        Raises:
            ImageProcessingError: If the metadata object is invalid.
        """
        self._validate_metadata(metadata)

        is_low_resolution = (
            metadata.width < self._minimum_width
            or metadata.height < self._minimum_height
            or metadata.megapixels < self._minimum_megapixels
        )

        result = ResolutionDetectionResult(
            image=metadata,
            is_low_resolution=is_low_resolution,
            width=metadata.width,
            height=metadata.height,
            megapixels=metadata.megapixels,
            minimum_width=self._minimum_width,
            minimum_height=self._minimum_height,
            minimum_megapixels=self._minimum_megapixels,
        )

        logger.debug(
            "Resolution detection completed: "
            "path=%s, size=%dx%d, megapixels=%.2f, low_resolution=%s",
            metadata.image.path,
            metadata.width,
            metadata.height,
            metadata.megapixels,
            is_low_resolution,
        )

        return result

    @staticmethod
    def _validate_metadata(
        metadata: ImageMetadata,
    ) -> None:
        """
        Validate the metadata supplied to the detector.

        Args:
            metadata: ImageMetadata to validate.

        Raises:
            ImageProcessingError: If the metadata is invalid.
        """
        if not isinstance(metadata, ImageMetadata):
            raise ImageProcessingError(
                "ResolutionDetector expects an ImageMetadata object."
            )