from pathlib import Path

from PIL import Image

from imagecleaner.core.dataset_loader import ImageRecord
from imagecleaner.validators.image_validator import ImageValidator


def create_test_image(tmp_path: Path) -> ImageRecord:
    image_path = tmp_path / "test_image.jpg"

    image = Image.new("RGB", (100, 100), color="white")
    image.save(image_path)

    return ImageRecord(
        path=str(image_path),
        relative_path="test_image.jpg",
        filename="test_image.jpg",
        extension=".jpg",
    )


def test_valid_image(tmp_path: Path) -> None:
    record = create_test_image(tmp_path)

    validator = ImageValidator()
    result = validator.validate(record)

    assert result.is_valid is True


def test_invalid_image_path(tmp_path: Path) -> None:
    image_path = tmp_path / "missing.jpg"

    record = ImageRecord(
        path=str(image_path),
        relative_path="missing.jpg",
        filename="missing.jpg",
        extension=".jpg",
    )

    validator = ImageValidator()
    result = validator.validate(record)

    assert result.is_valid is False