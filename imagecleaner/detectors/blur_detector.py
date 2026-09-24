"""
ImageCleaner Blur Detection.

This module provides a blur detector based on the variance of
the Laplacian operator.

The implementation is designed as a replaceable detector so
more advanced blur-analysis algorithms can be introduced later
without changing the rest of the processing pipeline.
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
class BlurDetectionResult:
    """
    Result produced by the blur detector.

    Attributes:
        image: Original ImageRecord.
        score: Variance of the Laplacian.
        is_blurry: Whether the image is classified as blurry.
        threshold: Threshold used for classification.
    """

    image: ImageRecord
    score: float
    is_blurry: bool
    threshold: float


class BlurDetector:
    """
    Detect image blur using Laplacian variance.

    A lower Laplacian variance generally indicates fewer strong
    edges and therefore a greater possibility of blur.
    """

    def __init__(
        self,
        threshold: float = 100.0,
    ) -> None:
        """
        Initialize the blur detector.

        Args:
            threshold: Minimum Laplacian variance considered sharp.

        Raises:
            ValueError: If threshold is negative.
        """
        if threshold < 0:
            raise ValueError(
                "Blur threshold must not be negative."
            )

        self._threshold = threshold

        logger.debug(
            "BlurDetector initialized with threshold=%s",
            threshold,
        )

    @property
    def threshold(self) -> float:
        """Return the configured blur threshold."""
        return self._threshold

    def detect(
        self,
        image: ImageRecord,
    ) -> BlurDetectionResult:
        """
        Analyze an image for blur.

        Args:
            image: ImageRecord produced by DatasetLoader.

        Returns:
            BlurDetectionResult containing the blur score
            and classification.

        Raises:
            ImageProcessingError: If the image cannot be read
                or processed.
        """
        self._validate_image_record(image)

        image_path = Path(image.path)

        logger.debug(
            "Running blur detection: %s",
            image_path,
        )

        grayscale_image = self._load_grayscale(image_path)

        laplacian = cv2.Laplacian(
            grayscale_image,
            cv2.CV_64F,
        )

        score = float(laplacian.var())

        is_blurry = score < self._threshold

        result = BlurDetectionResult(
            image=image,
            score=score,
            is_blurry=is_blurry,
            threshold=self._threshold,
        )

        logger.debug(
            "Blur detection completed: path=%s, score=%.4f, blurry=%s",
            image_path,
            score,
            is_blurry,
        )

        return result

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
                f"Unable to read image for blur detection: "
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
                "BlurDetector expects an ImageRecord."
            )

        if not image.path:
            raise ImageProcessingError(
                "ImageRecord contains an empty image path."
            )