"""
ImageCleaner Brightness Detection.

This module detects whether an image is underexposed, normally
exposed, or overexposed using mean grayscale intensity.

The detector is designed as a configurable baseline that can be
improved with more advanced exposure-analysis techniques later.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from imagecleaner.core.dataset_loader import ImageRecord
from imagecleaner.exceptions.custom_exceptions import ImageProcessingError
from imagecleaner.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class BrightnessDetectionResult:
    """
    Result produced by the brightness detector.

    Attributes:
        image: Original ImageRecord.
        score: Mean grayscale intensity from 0 to 255.
        status: Brightness classification.
        lower_threshold: Lower acceptable brightness boundary.
        upper_threshold: Upper acceptable brightness boundary.
    """

    image: ImageRecord
    score: float
    status: str
    lower_threshold: float
    upper_threshold: float

    @property
    def is_underexposed(self) -> bool:
        """Return whether the image is classified as underexposed."""
        return self.status == "underexposed"

    @property
    def is_overexposed(self) -> bool:
        """Return whether the image is classified as overexposed."""
        return self.status == "overexposed"

    @property
    def is_normal(self) -> bool:
        """Return whether the image has normal brightness."""
        return self.status == "normal"


class BrightnessDetector:
    """
    Detect image exposure using mean grayscale intensity.

    Pixel intensity generally ranges from 0 to 255:

        0   → black
        255 → white

    The default Foundation Edition thresholds are:

        < 50  → underexposed
        50-200 → normal
        > 200 → overexposed

    These are baseline values and should be experimentally tuned
    for the target datasets.
    """

    def __init__(
        self,
        lower_threshold: float = 50.0,
        upper_threshold: float = 200.0,
    ) -> None:
        """
        Initialize the brightness detector.

        Args:
            lower_threshold: Boundary below which an image is
                considered underexposed.
            upper_threshold: Boundary above which an image is
                considered overexposed.

        Raises:
            ValueError: If thresholds are outside the valid
                intensity range or incorrectly ordered.
        """
        if not 0 <= lower_threshold <= 255:
            raise ValueError(
                "lower_threshold must be between 0 and 255."
            )

        if not 0 <= upper_threshold <= 255:
            raise ValueError(
                "upper_threshold must be between 0 and 255."
            )

        if lower_threshold >= upper_threshold:
            raise ValueError(
                "lower_threshold must be less than "
                "upper_threshold."
            )

        self._lower_threshold = lower_threshold
        self._upper_threshold = upper_threshold

        logger.debug(
            "BrightnessDetector initialized: "
            "lower=%s, upper=%s",
            lower_threshold,
            upper_threshold,
        )

    @property
    def lower_threshold(self) -> float:
        """Return the lower brightness threshold."""
        return self._lower_threshold

    @property
    def upper_threshold(self) -> float:
        """Return the upper brightness threshold."""
        return self._upper_threshold

    def detect(
        self,
        image: ImageRecord,
    ) -> BrightnessDetectionResult:
        """
        Analyze an image for brightness problems.

        Args:
            image: ImageRecord produced by DatasetLoader.

        Returns:
            BrightnessDetectionResult containing the brightness
            score and classification.

        Raises:
            ImageProcessingError: If the image cannot be read
                or processed.
        """
        self._validate_image_record(image)

        image_path = Path(image.path)

        logger.debug(
            "Running brightness detection: %s",
            image_path,
        )

        grayscale_image = self._load_grayscale(image_path)

        score = float(np.mean(grayscale_image))

        status = self._classify(score)

        result = BrightnessDetectionResult(
            image=image,
            score=score,
            status=status,
            lower_threshold=self._lower_threshold,
            upper_threshold=self._upper_threshold,
        )

        logger.debug(
            "Brightness detection completed: "
            "path=%s, score=%.4f, status=%s",
            image_path,
            score,
            status,
        )

        return result

    def _classify(
        self,
        score: float,
    ) -> str:
        """
        Classify an image based on its brightness score.

        Args:
            score: Mean grayscale intensity.

        Returns:
            One of:
                - underexposed
                - normal
                - overexposed
        """
        if score < self._lower_threshold:
            return "underexposed"

        if score > self._upper_threshold:
            return "overexposed"

        return "normal"

    @staticmethod
    def _load_grayscale(
        image_path: Path,
    ) -> np.ndarray:
        """
        Load an image as a grayscale NumPy array.

        Args:
            image_path: Path to the image.

        Returns:
            Grayscale image represented as a NumPy array.

        Raises:
            ImageProcessingError: If the image cannot be read.
        """
        image = cv2.imread(
            str(image_path),
            cv2.IMREAD_GRAYSCALE,
        )

        if image is None:
            message = (
                "Unable to read image for brightness detection: "
                f"{image_path}"
            )

            logger.warning(message)

            raise ImageProcessingError(message)

        return image

    @staticmethod
    def _validate_image_record(
        image: ImageRecord,
    ) -> None:
        """
        Validate the ImageRecord supplied to the detector.

        Args:
            image: ImageRecord to validate.

        Raises:
            ImageProcessingError: If the supplied object is invalid.
        """
        if not isinstance(image, ImageRecord):
            raise ImageProcessingError(
                "BrightnessDetector expects an ImageRecord."
            )

        if not image.path:
            raise ImageProcessingError(
                "ImageRecord contains an empty image path."
            )