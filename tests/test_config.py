import pytest

from imagecleaner.config.settings import CleaningSettings
from imagecleaner.core.pipeline import ImageCleanerPipeline


def test_default_settings():
    settings = CleaningSettings()

    assert settings.min_width is not None
    assert settings.min_height is not None
    assert settings.min_brightness is not None
    assert settings.max_brightness is not None
    assert settings.blur_threshold is not None


def test_custom_settings():
    settings = CleaningSettings(
        min_width=800,
        min_height=600,
        min_brightness=60,
        max_brightness=200,
        blur_threshold=150,
    )

    assert settings.min_width == 800
    assert settings.min_height == 600
    assert settings.min_brightness == 60
    assert settings.max_brightness == 200
    assert settings.blur_threshold == 150


def test_none_disables_requirement():
    settings = CleaningSettings(
        min_width=None,
        min_height=None,
        min_brightness=None,
        max_brightness=None,
        blur_threshold=None,
    )

    assert settings.min_width is None
    assert settings.min_height is None
    assert settings.min_brightness is None
    assert settings.max_brightness is None
    assert settings.blur_threshold is None


def test_invalid_width():
    with pytest.raises(ValueError):
        CleaningSettings(min_width=0)


def test_invalid_height():
    with pytest.raises(ValueError):
        CleaningSettings(min_height=0)


def test_invalid_brightness_range():
    with pytest.raises(ValueError):
        CleaningSettings(
            min_brightness=200,
            max_brightness=100,
        )


def test_pipeline_configure():
    pipeline = ImageCleanerPipeline(".")

    pipeline.configure(
        min_width=800,
        min_height=600,
        min_brightness=60,
    )

    settings = pipeline.settings

    assert settings.cleaning.min_width == 800
    assert settings.cleaning.min_height == 600
    assert settings.cleaning.min_brightness == 60