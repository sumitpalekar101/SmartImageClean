
from pathlib import Path

import pytest
from PIL import Image

from imagecleaner.core.dataset_loader import ImageRecord
from imagecleaner.exceptions.custom_exceptions import ImageValidationError
from imagecleaner.validators.image_validator import ImageValidator


def create_test_image(
    tmp_path: Path,
    *,
    filename: str = "test_image.jpg",
    mode: str = "RGB",
    size: tuple[int, int] = (100, 100),
) -> ImageRecord:
    image_path = tmp_path / filename
    image = Image.new(mode, size, color=0 if mode == "L" else "white")
    image.save(image_path)

    return ImageRecord(
        path=str(image_path),
        relative_path=filename,
        filename=filename,
        extension=image_path.suffix,
    )


def test_valid_image(tmp_path: Path) -> None:
    record = create_test_image(tmp_path)

    result = ImageValidator().validate(record)

    assert result.is_valid is True
    assert result.width == 100
    assert result.height == 100
    assert result.image_format == "JPEG"
    assert result.mode == "RGB"
    assert result.error is None


def test_invalid_image_path(tmp_path: Path) -> None:
    image_path = tmp_path / "missing.jpg"
    record = ImageRecord(
        path=str(image_path),
        relative_path="missing.jpg",
        filename="missing.jpg",
        extension=".jpg",
    )

    result = ImageValidator().validate(record)

    assert result.is_valid is False
    assert "does not exist" in result.error


def test_directory_path_is_rejected(tmp_path: Path) -> None:
    directory = tmp_path / "image_folder"
    directory.mkdir()

    record = ImageRecord(
        path=str(directory),
        relative_path="image_folder",
        filename="image_folder",
        extension="",
    )

    result = ImageValidator().validate(record)

    assert result.is_valid is False
    assert "not a file" in result.error


def test_corrupted_image_is_rejected(tmp_path: Path) -> None:
    image_path = tmp_path / "corrupted.jpg"
    image_path.write_bytes(b"this is not a valid image")

    record = ImageRecord(
        path=str(image_path),
        relative_path=image_path.name,
        filename=image_path.name,
        extension=".jpg",
    )

    result = ImageValidator().validate(record)

    assert result.is_valid is False
    assert result.error is not None


def test_empty_image_path_raises_error() -> None:
    record = ImageRecord(
        path="",
        relative_path="empty.jpg",
        filename="empty.jpg",
        extension=".jpg",
    )

    with pytest.raises(ImageValidationError):
        ImageValidator().validate(record)


def test_wrong_record_type_raises_error() -> None:
    with pytest.raises(ImageValidationError):
        ImageValidator().validate("not an image record")


@pytest.mark.parametrize(
    ("mode", "filename", "expected_mode", "expected_format"),
    [
        ("L", "grayscale.png", "L", "PNG"),
        ("RGBA", "transparent.png", "RGBA", "PNG"),
    ],
)
def test_supported_image_modes(
    tmp_path: Path,
    mode: str,
    filename: str,
    expected_mode: str,
    expected_format: str,
) -> None:
    record = create_test_image(
        tmp_path,
        filename=filename,
        mode=mode,
    )

    result = ImageValidator().validate(record)

    assert result.is_valid is True
    assert result.mode == expected_mode
    assert result.image_format == expected_format
