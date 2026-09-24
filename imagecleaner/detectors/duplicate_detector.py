"""
ImageCleaner Duplicate Detection.

This module detects exact and visually similar duplicate images.

The Foundation Edition uses:
    1. SHA-256 hashing for exact file-content duplicates.
    2. Perceptual hashing for visual similarity analysis.

The detector is designed so more advanced similarity techniques
can be introduced later without changing the public result model.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Final

import imagehash
from PIL import Image

from imagecleaner.core.dataset_loader import ImageRecord
from imagecleaner.exceptions.custom_exceptions import ImageProcessingError
from imagecleaner.utils.logger import get_logger

logger = get_logger(__name__)


DEFAULT_HASH_SIZE: Final[int] = 8
DEFAULT_SIMILARITY_THRESHOLD: Final[int] = 5


@dataclass(frozen=True, slots=True)
class ImageHashResult:
    """
    Hash information generated for an image.

    Attributes:
        image: Original ImageRecord.
        file_hash: SHA-256 hash of the complete file content.
        perceptual_hash: Perceptual hash representing visual content.
    """

    image: ImageRecord
    file_hash: str
    perceptual_hash: str


@dataclass(frozen=True, slots=True)
class DuplicatePair:
    """
    Represents a pair of visually similar images.

    Attributes:
        first: First image in the pair.
        second: Second image in the pair.
        distance: Hamming distance between perceptual hashes.
    """

    first: ImageRecord
    second: ImageRecord
    distance: int

    @property
    def is_exact_match(self) -> bool:
        """Return whether the perceptual hashes are identical."""
        return self.distance == 0


@dataclass(frozen=True, slots=True)
class DuplicateDetectionResult:
    """
    Result produced by duplicate analysis.

    Attributes:
        images: Images that were analyzed.
        exact_duplicate_groups: Groups containing exact file duplicates.
        similar_pairs: Pairs of visually similar images.
        similarity_threshold: Maximum perceptual-hash distance
            considered visually similar.
    """

    images: tuple[ImageRecord, ...]
    exact_duplicate_groups: tuple[tuple[ImageRecord, ...], ...]
    similar_pairs: tuple[DuplicatePair, ...]
    similarity_threshold: int

    @property
    def exact_duplicate_count(self) -> int:
        """Return the number of images belonging to exact duplicates."""
        return sum(
            len(group)
            for group in self.exact_duplicate_groups
        )

    @property
    def exact_duplicate_group_count(self) -> int:
        """Return the number of exact duplicate groups."""
        return len(self.exact_duplicate_groups)

    @property
    def similar_pair_count(self) -> int:
        """Return the number of visually similar pairs."""
        return len(self.similar_pairs)


class DuplicateDetector:
    """
    Detect exact and visually similar duplicate images.

    Exact duplicates are identified using SHA-256 file hashes.

    Visual similarity is estimated using perceptual hashes and
    Hamming distance.
    """

    def __init__(
        self,
        *,
        hash_size: int = DEFAULT_HASH_SIZE,
        similarity_threshold: int = DEFAULT_SIMILARITY_THRESHOLD,
    ) -> None:
        """
        Initialize the duplicate detector.

        Args:
            hash_size: Size used by the perceptual hash algorithm.
            similarity_threshold: Maximum Hamming distance between
                perceptual hashes considered visually similar.

        Raises:
            ValueError: If configuration values are invalid.
        """
        if hash_size <= 0:
            raise ValueError(
                "hash_size must be greater than zero."
            )

        if similarity_threshold < 0:
            raise ValueError(
                "similarity_threshold must not be negative."
            )

        self._hash_size = hash_size
        self._similarity_threshold = similarity_threshold

        logger.debug(
            "DuplicateDetector initialized: "
            "hash_size=%d, similarity_threshold=%d",
            hash_size,
            similarity_threshold,
        )

    @property
    def hash_size(self) -> int:
        """Return the perceptual hash size."""
        return self._hash_size

    @property
    def similarity_threshold(self) -> int:
        """Return the configured similarity threshold."""
        return self._similarity_threshold

    def analyze(
        self,
        images: tuple[ImageRecord, ...],
    ) -> DuplicateDetectionResult:
        """
        Analyze a collection of images for duplicates.

        Args:
            images: Image records to analyze.

        Returns:
            DuplicateDetectionResult containing exact duplicate
            groups and visually similar pairs.

        Raises:
            ImageProcessingError: If the supplied image collection
                is invalid.
        """
        self._validate_images(images)

        logger.info(
            "Starting duplicate analysis for %d images",
            len(images),
        )

        hash_results = self._calculate_hashes(images)

        exact_duplicate_groups = self._find_exact_duplicates(
            hash_results
        )

        similar_pairs = self._find_similar_pairs(
            hash_results
        )

        result = DuplicateDetectionResult(
            images=images,
            exact_duplicate_groups=exact_duplicate_groups,
            similar_pairs=similar_pairs,
            similarity_threshold=self._similarity_threshold,
        )

        logger.info(
            "Duplicate analysis completed: "
            "exact_groups=%d, similar_pairs=%d",
            result.exact_duplicate_group_count,
            result.similar_pair_count,
        )

        return result

    def _calculate_hashes(
        self,
        images: tuple[ImageRecord, ...],
    ) -> tuple[ImageHashResult, ...]:
        """
        Calculate file and perceptual hashes for all images.

        Args:
            images: Images to hash.

        Returns:
            Tuple containing hash results.
        """
        results: list[ImageHashResult] = []

        for image in images:
            file_hash = self._calculate_file_hash(image.path)
            perceptual_hash = self._calculate_perceptual_hash(
                image.path
            )

            results.append(
                ImageHashResult(
                    image=image,
                    file_hash=file_hash,
                    perceptual_hash=perceptual_hash,
                )
            )

        return tuple(results)

    @staticmethod
    def _calculate_file_hash(
        image_path: Path,
    ) -> str:
        """
        Calculate a SHA-256 hash for a file.

        Args:
            image_path: Path to the image.

        Returns:
            SHA-256 hexadecimal digest.

        Raises:
            ImageProcessingError: If the file cannot be read.
        """
        import hashlib

        hasher = hashlib.sha256()

        try:
            with image_path.open("rb") as image_file:
                while chunk := image_file.read(1024 * 1024):
                    hasher.update(chunk)

        except OSError as error:
            message = (
                f"Unable to calculate file hash: "
                f"{image_path}: {error}"
            )

            logger.warning(message)

            raise ImageProcessingError(message) from error

        return hasher.hexdigest()

    def _calculate_perceptual_hash(
        self,
        image_path: Path,
    ) -> str:
        """
        Calculate a perceptual hash for an image.

        Args:
            image_path: Path to the image.

        Returns:
            Perceptual hash as a hexadecimal string.

        Raises:
            ImageProcessingError: If the image cannot be opened.
        """
        try:
            with Image.open(image_path) as opened_image:
                perceptual_hash = imagehash.phash(
                    opened_image,
                    hash_size=self._hash_size,
                )

        except (OSError, ValueError) as error:
            message = (
                f"Unable to calculate perceptual hash: "
                f"{image_path}: {error}"
            )

            logger.warning(message)

            raise ImageProcessingError(message) from error

        return str(perceptual_hash)

    @staticmethod
    def _find_exact_duplicates(
        hash_results: tuple[ImageHashResult, ...],
    ) -> tuple[tuple[ImageRecord, ...], ...]:
        """
        Group images having identical SHA-256 hashes.

        Args:
            hash_results: Calculated image hashes.

        Returns:
            Tuple of exact duplicate groups.
        """
        groups: defaultdict[
            str,
            list[ImageRecord],
        ] = defaultdict(list)

        for result in hash_results:
            groups[result.file_hash].append(
                result.image
            )

        duplicate_groups = [
            tuple(images)
            for images in groups.values()
            if len(images) > 1
        ]

        return tuple(duplicate_groups)

    def _find_similar_pairs(
        self,
        hash_results: tuple[ImageHashResult, ...],
    ) -> tuple[DuplicatePair, ...]:
        """
        Find pairs with similar perceptual hashes.

        Args:
            hash_results: Calculated image hashes.

        Returns:
            Tuple of visually similar image pairs.
        """
        pairs: list[DuplicatePair] = []

        for index, first in enumerate(hash_results):
            first_hash = imagehash.hex_to_hash(
                first.perceptual_hash
            )

            for second in hash_results[index + 1:]:
                second_hash = imagehash.hex_to_hash(
                    second.perceptual_hash
                )

                distance = first_hash - second_hash

                if distance <= self._similarity_threshold:
                    pairs.append(
                        DuplicatePair(
                            first=first.image,
                            second=second.image,
                            distance=distance,
                        )
                    )

        return tuple(pairs)

    @staticmethod
    def _validate_images(
        images: tuple[ImageRecord, ...],
    ) -> None:
        """
        Validate the supplied image collection.

        Args:
            images: Image collection to validate.

        Raises:
            ImageProcessingError: If the collection is invalid.
        """
        if not isinstance(images, tuple):
            raise ImageProcessingError(
                "DuplicateDetector expects a tuple of ImageRecord objects."
            )

        if any(
            not isinstance(image, ImageRecord)
            for image in images
        ):
            raise ImageProcessingError(
                "DuplicateDetector received an invalid ImageRecord."
            )