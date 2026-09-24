"""
ImageCleaner Custom Exceptions.

This module defines the exception hierarchy used throughout
the ImageCleaner library.
"""


class ImageCleanerError(Exception):
    """
    Base exception for all ImageCleaner-specific errors.

    All custom exceptions in the library inherit from this class,
    allowing users to catch every ImageCleaner error with:

        except ImageCleanerError:
            ...
    """


class ConfigurationError(ImageCleanerError):
    """
    Raised when ImageCleaner configuration is invalid.
    """


class DatasetError(ImageCleanerError):
    """
    Base exception for dataset-related errors.
    """


class DatasetNotFoundError(DatasetError):
    """
    Raised when the requested dataset directory does not exist.
    """

    def __init__(self, dataset_path: str) -> None:
        self.dataset_path = dataset_path

        super().__init__(
            f"Dataset directory does not exist: {dataset_path}"
        )


class DatasetEmptyError(DatasetError):
    """
    Raised when a dataset contains no supported images.
    """

    def __init__(self, dataset_path: str) -> None:
        self.dataset_path = dataset_path

        super().__init__(
            f"No supported images were found in dataset: {dataset_path}"
        )


class ImageProcessingError(ImageCleanerError):
    """
    Base exception for image-processing errors.
    """


class ImageReadError(ImageProcessingError):
    """
    Raised when an image cannot be read or decoded.
    """

    def __init__(self, image_path: str) -> None:
        self.image_path = image_path

        super().__init__(
            f"Unable to read image: {image_path}"
        )


class UnsupportedImageFormatError(ImageProcessingError):
    """
    Raised when an image has an unsupported file format.
    """

    def __init__(
        self,
        image_path: str,
        extension: str,
    ) -> None:
        self.image_path = image_path
        self.extension = extension

        super().__init__(
            f"Unsupported image format '{extension}' "
            f"for file: {image_path}"
        )


class ImageValidationError(ImageProcessingError):
    """
    Raised when an image fails validation.
    """


class ReportGenerationError(ImageCleanerError):
    """
    Raised when a dataset report cannot be generated.
    """


class QualityScoreError(ImageCleanerError):
    """
    Raised when the dataset quality score cannot be calculated.
    """
    