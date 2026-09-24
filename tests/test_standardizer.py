from pathlib import Path

from PIL import Image

from imagecleaner.standardization import ImageStandardizer


def create_test_image(path: Path, size=(100, 100), mode="RGB"):
    image = Image.new(mode, size)
    image.save(path)


def test_resize_to_minimum(tmp_path):
    source = tmp_path / "input.jpg"
    output = tmp_path / "output.jpg"

    create_test_image(source, size=(100, 100))

    standardizer = ImageStandardizer()

    result = standardizer.standardize(
        source,
        output,
        min_width=500,
        min_height=400,
    )

    with Image.open(result) as image:
        assert image.size == (500, 400)


def test_color_mode_conversion(tmp_path):
    source = tmp_path / "input.jpg"
    output = tmp_path / "output.jpg"

    create_test_image(source, mode="L")

    standardizer = ImageStandardizer()

    result = standardizer.standardize(
        source,
        output,
        required_color_mode="RGB",
    )

    with Image.open(result) as image:
        assert image.mode == "RGB"


def test_format_conversion(tmp_path):
    source = tmp_path / "input.png"
    output = tmp_path / "output.jpg"

    create_test_image(source)

    standardizer = ImageStandardizer()

    result = standardizer.standardize(
        source,
        output,
        required_format="JPEG",
    )

    with Image.open(result) as image:
        assert image.format == "JPEG"


def test_image_already_meets_requirements(tmp_path):
    source = tmp_path / "input.jpg"
    output = tmp_path / "output.jpg"

    create_test_image(source, size=(800, 600))

    standardizer = ImageStandardizer()

    result = standardizer.standardize(
        source,
        output,
        min_width=500,
        min_height=400,
    )

    with Image.open(result) as image:
        assert image.size == (800, 600)


def test_output_directory_is_created(tmp_path):
    source = tmp_path / "input.jpg"
    output = tmp_path / "standardized" / "result.jpg"

    create_test_image(source)

    standardizer = ImageStandardizer()

    result = standardizer.standardize(source, output)

    assert result.exists()