"""
ImageCleaner File-System Utilities.

This module contains reusable helpers for validating paths,
discovering image files, checking supported image formats,
and creating directories used by the ImageCleaner library.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from imagecleaner.config.constants import SUPPORTED_IMAGE_FORMATS
from imagecleaner.exceptions.custom_exceptions import (
    DatasetNotFoundError,
    UnsupportedImageFormatError,
)


def normalize_path(path: str | Path) -> Path:
    """
    Convert a path-like value into a normalized Path object.

    Args:
        path: File-system path supplied by the caller.

    Returns:
        Normalized Path object.

    Raises:
        ValueError: If the supplied path is empty.
    """
    if isinstance(path, str) and not path.strip():
        raise ValueError("Path must not be empty.")

    normalized_path = Path(path).expanduser()

    return normalized_path.resolve()


def validate_directory(directory: str | Path) -> Path:
    """
    Validate that a directory exists.

    Args:
        directory: Directory path to validate.

    Returns:
        Resolved directory path.

    Raises:
        DatasetNotFoundError: If the directory does not exist.
        NotADirectoryError: If the path exists but is not a directory.
    """
    directory_path = normalize_path(directory)

    if not directory_path.exists():
        raise DatasetNotFoundError(str(directory_path))

    if not directory_path.is_dir():
        raise NotADirectoryError(
            f"Expected a directory but received: {directory_path}"
        )

    return directory_path


def get_file_extension(file_path: str | Path) -> str:
    """
    Return a file extension in lowercase.

    Args:
        file_path: Path to a file.

    Returns:
        Lowercase file extension including the leading dot.

    Example:
        ``photo.JPG`` returns ``".jpg"``.
    """
    return Path(file_path).suffix.lower()


def is_supported_image(file_path: str | Path) -> bool:
    """
    Determine whether a file has a supported image extension.

    Args:
        file_path: Path to the file.

    Returns:
        True if the extension is supported, otherwise False.
    """
    extension = get_file_extension(file_path)

    return extension in SUPPORTED_IMAGE_FORMATS


def validate_image_format(file_path: str | Path) -> Path:
    """
    Validate that a file uses a supported image format.

    Args:
        file_path: Image file path.

    Returns:
        Resolved image path.

    Raises:
        FileNotFoundError: If the file does not exist.
        IsADirectoryError: If the path points to a directory.
        UnsupportedImageFormatError: If the file format is unsupported.
    """
    image_path = normalize_path(file_path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"File does not exist: {image_path}"
        )

    if not image_path.is_file():
        raise IsADirectoryError(
            f"Expected a file but received: {image_path}"
        )

    extension = get_file_extension(image_path)

    if extension not in SUPPORTED_IMAGE_FORMATS:
        raise UnsupportedImageFormatError(
            str(image_path),
            extension,
        )

    return image_path


def iter_image_files(
    directory: str | Path,
    *,
    recursive: bool = True,
) -> Iterator[Path]:
    """
    Iterate over supported image files in a directory.

    Args:
        directory: Directory containing images.
        recursive: If True, search all subdirectories.

    Yields:
        Resolved paths to supported image files.

    Raises:
        DatasetNotFoundError: If the directory does not exist.
        NotADirectoryError: If the path is not a directory.
    """
    directory_path = validate_directory(directory)

    pattern = "**/*" if recursive else "*"

    for file_path in directory_path.glob(pattern):
        if file_path.is_file() and is_supported_image(file_path):
            yield file_path.resolve()


def create_directory(directory: str | Path) -> Path:
    """
    Create a directory if it does not already exist.

    Args:
        directory: Directory to create.

    Returns:
        Resolved directory path.
    """
    directory_path = normalize_path(directory)

    directory_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    return directory_path