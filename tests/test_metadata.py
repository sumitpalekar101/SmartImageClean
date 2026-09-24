from pathlib import Path

from PIL import Image

from imagecleaner.core.dataset_loader import ImageRecord
from imagecleaner.core.image_metadata import ImageMetadataExtractor


def create_test_image(tmp_path: Path) -> ImageRecord:
    image_path = tmp_path / "metadata_test.jpg"

    image = Image.new("RGB", (200, 100), color="white")
    image.save(image_path)

    return ImageRecord(
        path=str(image_path),
        relative_path="metadata_test.jpg",
        filename="metadata_test.jpg",
        extension=".jpg",
    )


def test_extract_metadata(tmp_path: Path) -> None:
    record = create_test_image(tmp_path)

    extractor = ImageMetadataExtractor()
    metadata = extractor.extract(record)

    assert metadata.width == 200
    assert metadata.height == 100
    assert metadata.megapixels == 0.02


def test_metadata_dimensions(tmp_path: Path) -> None:
    record = create_test_image(tmp_path)

    extractor = ImageMetadataExtractor()
    metadata = extractor.extract(record)

    assert metadata.dimensions == (200, 100)