"""
ImageCleaner Configuration Constants

This module contains all project-wide constant values used
throughout the ImageCleaner library.

Changing values here automatically updates the behaviour
of the entire library.
"""

from pathlib import Path

# ==========================================================
# Project Information
# ==========================================================

PROJECT_NAME: str = "ImageCleaner"

PROJECT_VERSION: str = "0.1.0"

AUTHOR: str = "Sumit Palekar"

LICENSE: str = "MIT"

# ==========================================================
# Supported Image Formats
# ==========================================================

SUPPORTED_IMAGE_FORMATS: tuple[str, ...] = (
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".tiff",
    ".webp",
)

# ==========================================================
# Image Quality Thresholds
# ==========================================================

DEFAULT_BLUR_THRESHOLD: int = 100

MIN_IMAGE_WIDTH: int = 256

MIN_IMAGE_HEIGHT: int = 256

MIN_BRIGHTNESS: int = 40

MAX_BRIGHTNESS: int = 220

# ==========================================================
# Report Files
# ==========================================================

CSV_REPORT_NAME: str = "imagecleaner_report.csv"

JSON_REPORT_NAME: str = "imagecleaner_report.json"

LOG_FILE_NAME: str = "imagecleaner.log"

# ==========================================================
# Default Directories
# ==========================================================

ROOT_DIRECTORY: Path = Path.cwd()

REPORT_DIRECTORY: Path = ROOT_DIRECTORY / "reports"

LOG_DIRECTORY: Path = ROOT_DIRECTORY / "logs"

DATASET_DIRECTORY: Path = ROOT_DIRECTORY / "datasets"

# ==========================================================
# Dataset Quality Score
# ==========================================================

QUALITY_EXCELLENT: int = 90

QUALITY_GOOD: int = 75

QUALITY_AVERAGE: int = 50

QUALITY_POOR: int = 0