from pathlib import Path

import pytest
from PIL import Image

from imagecleaner.core.pipeline import ImageCleanerPipeline
from imagecleaner.exceptions.custom_exceptions import (
    DatasetEmptyError,
    ImageProcessingError,
)


def create_test_images(tmp_path: Path) -> None:
    for index in range(3):
        image_path = tmp_path / f"test_{index}.jpg"

        image = Image.new(
            "RGB",
            (800, 600),
            color="white",
        )

        image.save(image_path)


def test_pipeline_run(tmp_path: Path) -> None:
    create_test_images(tmp_path)

    pipeline = ImageCleanerPipeline(
    dataset_path=tmp_path,
    clean=False,
)
    result = pipeline.run()

    assert result.total_images == 3
    assert result.kept_count + result.review_count + result.removal_count == 3



def test_process_standardizes_unacceptable_image(tmp_path):
    dataset = tmp_path / "dataset"
    standardized = tmp_path / "standardized"
    dataset.mkdir()

    image_path = dataset / "small.png"

    Image.new("RGB", (50, 50), color="white").save(image_path)

    pipeline = ImageCleanerPipeline(dataset)

    pipeline.configure(
        min_width=100,
        min_height=100,
        max_width=None,
        max_height=None,
        min_brightness=None,
        max_brightness=None,
        blur_threshold=None,
        min_quality_score=None,
        required_format=None,
        required_color_mode=None,
        required_aspect_ratio=None,
        max_file_size=None,
        check_duplicates=False,
        check_blur=False,
        check_brightness=False,
        check_resolution=True,
    )

    result = pipeline.process(
        standardized_directory=standardized
    )

    standardized_image = standardized / "small.png"

    assert standardized_image.exists()
    assert image_path.exists()
    assert result.total_images == 1
    assert result.acceptable_count == 1
    assert result.unacceptable_count == 0


def test_process_does_not_modify_original_image(tmp_path):
    dataset = tmp_path / "dataset"
    standardized = tmp_path / "standardized"
    dataset.mkdir()

    image_path = dataset / "small.png"

    Image.new("RGB", (50, 50), color="white").save(image_path)

    original_size = Image.open(image_path).size

    pipeline = ImageCleanerPipeline(dataset)

    pipeline.configure(
        min_width=100,
        min_height=100,
        max_width=None,
        max_height=None,
        min_brightness=None,
        max_brightness=None,
        blur_threshold=None,
        min_quality_score=None,
        required_format=None,
        required_color_mode=None,
        required_aspect_ratio=None,
        max_file_size=None,
        check_duplicates=False,
        check_blur=False,
        check_brightness=False,
        check_resolution=True,
    )

    pipeline.process(
        standardized_directory=standardized
    )

    assert Image.open(image_path).size == original_size


def test_process_skips_already_acceptable_image(tmp_path):
    dataset = tmp_path / "dataset"
    standardized = tmp_path / "standardized"
    dataset.mkdir()

    image_path = dataset / "good.png"

    Image.new("RGB", (200, 200), color="white").save(image_path)

    pipeline = ImageCleanerPipeline(dataset)

    pipeline.configure(
        min_width=100,
        min_height=100,
        max_width=None,
        max_height=None,
        min_brightness=None,
        max_brightness=None,
        blur_threshold=None,
        min_quality_score=None,
        required_format=None,
        required_color_mode=None,
        required_aspect_ratio=None,
        max_file_size=None,
        check_duplicates=False,
        check_blur=False,
        check_brightness=False,
        check_resolution=True,
    )

    result = pipeline.process(
        standardized_directory=standardized
    )

    assert result.total_images == 1
    assert result.acceptable_count == 1
    assert result.unacceptable_count == 0
    assert standardized.exists()
    assert (standardized / "good.png").exists()
    assert image_path.exists()
def test_pipeline_rejects_empty_dataset(tmp_path):
    dataset = tmp_path / "empty_dataset"
    dataset.mkdir()

    pipeline = ImageCleanerPipeline(dataset)

    with pytest.raises(DatasetEmptyError):
        pipeline.run()

def test_pipeline_rejects_corrupted_image(tmp_path):
    dataset = tmp_path / "dataset"
    dataset.mkdir()

    corrupted_image = dataset / "corrupted.jpg"
    corrupted_image.write_bytes(b"this is not a valid image")

    pipeline = ImageCleanerPipeline(dataset)

    with pytest.raises(ImageProcessingError):
            pipeline.run()


def test_process_corrects_brightness_when_enabled(tmp_path):
    dataset = tmp_path / "dataset"
    standardized = tmp_path / "standardized"
    dataset.mkdir()

    image_path = dataset / "dark.png"
    Image.new("RGB", (300, 300), color=(30, 30, 30)).save(image_path)

    original_mean = sum(Image.open(image_path).convert("L").getdata()) / (
        300 * 300
    )

    pipeline = ImageCleanerPipeline(dataset)

    pipeline.configure(
        brightness_correction=True,
        required_format="PNG",
        required_color_mode="RGB",
        min_width=250,
        max_width=500,
        min_height=250,
        max_height=500,
        required_aspect_ratio=None,
        check_duplicates=False,
        check_blur=False,
        check_brightness=False,
        check_resolution=True,
    )

    pipeline.process(standardized_directory=standardized)

    output_path = standardized / "dark.png"
    assert output_path.exists()

    with Image.open(output_path) as output_image:
        output_mean = sum(
            output_image.convert("L").getdata()
        ) / (output_image.width * output_image.height)

    assert output_mean > original_mean
    assert image_path.exists()
