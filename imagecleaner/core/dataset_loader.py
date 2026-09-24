"""
ImageCleaner Dataset Loader.

This module is responsible for discovering and representing image
files contained within a dataset.

The loader does not perform image-quality analysis. Its responsibility
is limited to dataset discovery, validation, and metadata required
by downstream processing stages.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from imagecleaner.exceptions.custom_exceptions import DatasetEmptyError
from imagecleaner.utils.file_utils import iter_image_files, validate_directory
from imagecleaner.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class ImageRecord:
    """
    Immutable representation of an image discovered in a dataset.

    Attributes:
        path: Absolute path to the image.
        relative_path: Image path relative to the dataset root.
        filename: Name of the image file.
        extension: Lowercase image file extension.
    """

    path: Path
    relative_path: Path
    filename: str
    extension: str


@dataclass(frozen=True, slots=True)
class Dataset:
    """
    Immutable representation of a discovered image dataset.

    Attributes:
        root: Absolute path to the dataset root.
        images: Tuple containing all discovered image records.
    """

    root: Path
    images: tuple[ImageRecord, ...]

    @property
    def image_count(self) -> int:
        """Return the total number of discovered images."""
        return len(self.images)

    def __len__(self) -> int:
        """Return the number of images in the dataset."""
        return self.image_count


class DatasetLoader:
    """
    Discover supported images from a dataset directory.

    The loader is intentionally independent of image-quality
    detection. Detectors will consume the Dataset and ImageRecord
    objects produced here.
    """

    def __init__(
        self,
        dataset_path: str | Path,
        *,
        recursive: bool = True,
    ) -> None:
        """
        Initialize the dataset loader.

        Args:
            dataset_path: Directory containing the image dataset.
            recursive: Whether subdirectories should be searched.

        Raises:
            DatasetNotFoundError: If the dataset directory does
                not exist.
            NotADirectoryError: If the supplied path is not a directory.
        """
        self._dataset_path = validate_directory(dataset_path)
        self._recursive = recursive

        logger.debug(
            "DatasetLoader initialized: path=%s, recursive=%s",
            self._dataset_path,
            self._recursive,
        )

    @property
    def dataset_path(self) -> Path:
        """Return the validated dataset path."""
        return self._dataset_path

    @property
    def recursive(self) -> bool:
        """Return whether recursive scanning is enabled."""
        return self._recursive

    def discover(self) -> Dataset:
        """
        Discover supported images in the configured dataset.

        Returns:
            Dataset containing discovered image records.

        Raises:
            DatasetEmptyError: If no supported images are found.
        """
        logger.info(
            "Starting dataset discovery: %s",
            self._dataset_path,
        )

        image_records: list[ImageRecord] = []

        for image_path in iter_image_files(
            self._dataset_path,
            recursive=self._recursive,
        ):
            record = self._create_image_record(image_path)
            image_records.append(record)

        if not image_records:
            logger.warning(
                "No supported images found: %s",
                self._dataset_path,
            )

            raise DatasetEmptyError(
                str(self._dataset_path)
            )

        dataset = Dataset(
            root=self._dataset_path,
            images=tuple(image_records),
        )

        logger.info(
            "Dataset discovery completed: %d images found",
            dataset.image_count,
        )

        return dataset

    def _create_image_record(
        self,
        image_path: Path,
    ) -> ImageRecord:
        """
        Create an ImageRecord from an image path.

        Args:
            image_path: Absolute path to the discovered image.

        Returns:
            ImageRecord containing normalized image metadata.
        """
        relative_path = image_path.relative_to(
            self._dataset_path
        )

        return ImageRecord(
            path=image_path,
            relative_path=relative_path,
            filename=image_path.name,
            extension=image_path.suffix.lower(),
        )