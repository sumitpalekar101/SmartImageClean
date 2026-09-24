"""
SmartClean-AI Runtime Configuration.

This module defines user-configurable settings for image dataset
analysis and cleaning.
"""

from dataclasses import dataclass, field
from pathlib import Path

from imagecleaner.config.constants import (
    DEFAULT_BLUR_THRESHOLD,
    MAX_BRIGHTNESS,
    MIN_BRIGHTNESS,
    MIN_IMAGE_HEIGHT,
    MIN_IMAGE_WIDTH,
)


@dataclass(slots=True)
class CleaningSettings:
    """
    Configuration used by the image-cleaning pipeline.

    A value of None disables that individual requirement.
    """

    min_width: int | None = MIN_IMAGE_WIDTH
    max_width: int | None = None

    min_height: int | None = MIN_IMAGE_HEIGHT
    max_height: int | None = None

    min_brightness: float | None = MIN_BRIGHTNESS
    max_brightness: float | None = MAX_BRIGHTNESS

    blur_threshold: float | None = DEFAULT_BLUR_THRESHOLD
    min_quality_score: float | None = None

    required_format: str | None = None
    required_color_mode: str | None = None
    required_aspect_ratio: float | None = None

    max_file_size: int | None = None

    check_duplicates: bool = True
    check_blur: bool = True
    check_resolution: bool = True
    check_brightness: bool = True

    def __post_init__(self) -> None:
        """Validate the configuration."""
        self._validate_dimensions()
        self._validate_brightness()
        self._validate_blur()
        self._validate_quality_score()
        self._validate_format()
        self._validate_color_mode()
        self._validate_aspect_ratio()
        self._validate_file_size()
        self._validate_check_flags()

    def _validate_dimensions(self) -> None:
        """Validate width and height requirements."""
        for name, value in (
            ("min_width", self.min_width),
            ("max_width", self.max_width),
            ("min_height", self.min_height),
            ("max_height", self.max_height),
        ):
            if value is None:
                continue

            if not isinstance(value, int) or isinstance(value, bool):
                raise TypeError(f"{name} must be an integer or None.")

            if value <= 0:
                raise ValueError(
                    f"{name} must be greater than 0."
                )

        if (
            self.min_width is not None
            and self.max_width is not None
            and self.min_width > self.max_width
        ):
            raise ValueError(
                "min_width must not be greater than max_width."
            )

        if (
            self.min_height is not None
            and self.max_height is not None
            and self.min_height > self.max_height
        ):
            raise ValueError(
                "min_height must not be greater than max_height."
            )

    def _validate_brightness(self) -> None:
        """Validate brightness requirements."""
        for name, value in (
            ("min_brightness", self.min_brightness),
            ("max_brightness", self.max_brightness),
        ):
            if value is None:
                continue

            if (
                not isinstance(value, (int, float))
                or isinstance(value, bool)
            ):
                raise TypeError(
                    f"{name} must be a number or None."
                )

            if not 0 <= value <= 255:
                raise ValueError(
                    f"{name} must be between 0 and 255."
                )

        if (
            self.min_brightness is not None
            and self.max_brightness is not None
            and self.min_brightness > self.max_brightness
        ):
            raise ValueError(
                "min_brightness must not be greater than max_brightness."
            )

    def _validate_blur(self) -> None:
        """Validate the blur threshold."""
        if self.blur_threshold is None:
            return

        if (
            not isinstance(self.blur_threshold, (int, float))
            or isinstance(self.blur_threshold, bool)
        ):
            raise TypeError(
                "blur_threshold must be a number or None."
            )

        if self.blur_threshold < 0:
            raise ValueError(
                "blur_threshold must be greater than or equal to 0."
            )

    def _validate_quality_score(self) -> None:
        """Validate the minimum quality score."""
        if self.min_quality_score is None:
            return

        if (
            not isinstance(self.min_quality_score, (int, float))
            or isinstance(self.min_quality_score, bool)
        ):
            raise TypeError(
                "min_quality_score must be a number or None."
            )

        if not 0 <= self.min_quality_score <= 100:
            raise ValueError(
                "min_quality_score must be between 0 and 100."
            )

    def _validate_format(self) -> None:
        """Validate the required image format."""
        if self.required_format is None:
            return

        if not isinstance(self.required_format, str):
            raise TypeError(
                "required_format must be a string or None."
            )

        value = self.required_format.strip()

        if not value:
            raise ValueError(
                "required_format must not be empty."
            )

        self.required_format = value.upper().lstrip(".")

    def _validate_color_mode(self) -> None:
        """Validate the required image color mode."""
        if self.required_color_mode is None:
            return

        if not isinstance(self.required_color_mode, str):
            raise TypeError(
                "required_color_mode must be a string or None."
            )

        value = self.required_color_mode.strip()

        if not value:
            raise ValueError(
                "required_color_mode must not be empty."
            )

        self.required_color_mode = value.upper()

    def _validate_aspect_ratio(self) -> None:
        """Validate the required aspect ratio."""
        if self.required_aspect_ratio is None:
            return

        if (
            not isinstance(self.required_aspect_ratio, (int, float))
            or isinstance(self.required_aspect_ratio, bool)
        ):
            raise TypeError(
                "required_aspect_ratio must be a number or None."
            )

        if self.required_aspect_ratio <= 0:
            raise ValueError(
                "required_aspect_ratio must be greater than 0."
            )

    def _validate_file_size(self) -> None:
        """Validate the maximum file size."""
        if self.max_file_size is None:
            return

        if (
            not isinstance(self.max_file_size, int)
            or isinstance(self.max_file_size, bool)
        ):
            raise TypeError(
                "max_file_size must be an integer or None."
            )

        if self.max_file_size <= 0:
            raise ValueError(
                "max_file_size must be greater than 0."
            )

    def _validate_check_flags(self) -> None:
        """Validate detector enable/disable flags."""
        for name, value in (
            ("check_duplicates", self.check_duplicates),
            ("check_blur", self.check_blur),
            ("check_resolution", self.check_resolution),
            ("check_brightness", self.check_brightness),
        ):
            if not isinstance(value, bool):
                raise TypeError(
                    f"{name} must be a boolean."
                )


@dataclass(slots=True)
class OutputSettings:
    """Configuration for SmartClean-AI output."""

    output_directory: Path = field(
        default_factory=lambda: Path.cwd() / "reports"
    )

    generate_csv_report: bool = True
    generate_json_report: bool = True
    preserve_structure: bool = True

    def __post_init__(self) -> None:
        """Normalize the output directory."""
        self.output_directory = Path(self.output_directory)


@dataclass(slots=True)
class ImageCleanerSettings:
    """Complete SmartClean-AI configuration."""

    cleaning: CleaningSettings = field(
        default_factory=CleaningSettings
    )

    output: OutputSettings = field(
        default_factory=OutputSettings
    )