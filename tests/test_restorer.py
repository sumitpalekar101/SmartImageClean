from PIL import Image

from imagecleaner.restoration import ImageRestorer


def test_restore_creates_output_image(tmp_path):
    source = tmp_path / "source.png"
    output = tmp_path / "restored.png"

    Image.new("RGB", (100, 100), color="gray").save(source)

    restorer = ImageRestorer()
    result = restorer.restore(source, output)

    assert result == output
    assert output.exists()


def test_restore_changes_brightness(tmp_path):
    source = tmp_path / "source.png"
    output = tmp_path / "restored.png"

    Image.new("RGB", (100, 100), color="gray").save(source)

    restorer = ImageRestorer()
    restorer.restore(
        source,
        output,
        brightness=1.5,
    )

    with Image.open(source) as original:
        original_pixel = original.getpixel((50, 50))

    with Image.open(output) as restored:
        restored_pixel = restored.getpixel((50, 50))

    assert restored_pixel != original_pixel


def test_restore_upscales_image(tmp_path):
    source = tmp_path / "source.png"
    output = tmp_path / "restored.png"

    Image.new("RGB", (100, 80), color="gray").save(source)

    restorer = ImageRestorer()
    restorer.restore(
        source,
        output,
        upscale=2.0,
    )

    with Image.open(output) as restored:
        assert restored.size == (200, 160)


def test_restore_preserves_original(tmp_path):
    source = tmp_path / "source.png"
    output = tmp_path / "restored.png"

    Image.new("RGB", (100, 100), color="gray").save(source)

    with Image.open(source) as original:
        original_size = original.size

    restorer = ImageRestorer()
    restorer.restore(
        source,
        output,
        brightness=1.5,
    )

    with Image.open(source) as original:
        assert original.size == original_size