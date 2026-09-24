"""
SmartClean-AI Command Line Interface.

This module provides the user-facing command-line interface
for running the image-cleaning pipeline.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from imagecleaner.core.pipeline import ImageCleanerPipeline
from imagecleaner.exceptions.custom_exceptions import ImageProcessingError
from imagecleaner.reports.review_report import ReviewReportGenerator
from imagecleaner.utils.logger import get_logger

logger = get_logger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """
    Build the command-line argument parser.

    Returns:
        Configured ArgumentParser.
    """
    parser = argparse.ArgumentParser(
        prog="smartclean",
        description=(
            "SmartClean-AI image cleaning and quality analysis."
        ),
    )

    parser.add_argument(
        "input",
        type=Path,
        help="Directory containing images to analyze.",
    )

    parser.add_argument(
        "--quarantine",
        type=Path,
        default=Path("quarantine"),
        help=(
            "Directory used for removal candidates. "
            "Default: quarantine"
        ),
    )

    parser.add_argument(
        "--clean",
        action="store_true",
        help=(
            "Execute removal decisions by moving candidates "
            "to quarantine. Without this option, the run is "
            "analysis-only."
        ),
    )
    parser.add_argument(
        "--process",
        action="store_true",
        help=(
            "Automatically standardize configuration-unacceptable "
            "images and re-analyze them."
        ),
    )

    parser.add_argument(
        "--standardized",
        type=Path,
        default=Path("standardized"),
        help=(
            "Directory used for standardized images. "
            "Default: standardized"
        ),
    )
    return parser


def run_cli(
    arguments: list[str] | None = None,
) -> int:
    """
    Run the SmartClean-AI command-line interface.

    Args:
        arguments: Optional command-line arguments. If None,
            arguments are read from sys.argv.

    Returns:
        Process exit code.
    """
    parser = build_parser()
    args = parser.parse_args(arguments)

    input_path = args.input.resolve()
    quarantine_path = args.quarantine.resolve()

    if not input_path.exists():
        parser.error(
            f"Input directory does not exist: {input_path}"
        )

    if not input_path.is_dir():
        parser.error(
            f"Input path is not a directory: {input_path}"
        )

    logger.info(
        "Starting CLI run: input=%s, clean=%s",
        input_path,
        args.clean,
    )

    try:
        pipeline = ImageCleanerPipeline(
            str(input_path),
            quarantine_directory=str(quarantine_path),
            clean=args.clean,
        )

        if args.process:
            result = pipeline.process(
                standardized_directory=args.standardized
            )
        else:
            result = pipeline.run()

        report_generator = ReviewReportGenerator()
        report_path = report_generator.generate(result)

        logger.info(
            "Review report available at: %s",
            report_path,
        )

    except ImageProcessingError as error:
        logger.error(
            "SmartClean-AI processing failed: %s",
            error,
        )

        print(
            f"Error: {error}",
            file=sys.stderr,
        )

        return 1

    except KeyboardInterrupt:
        logger.warning(
            "SmartClean-AI execution interrupted by user."
        )

        print(
            "\nOperation cancelled.",
            file=sys.stderr,
        )

        return 130

    _print_summary(result)

    return 0

def _print_summary(result) -> None:
    """
    Print a human-readable pipeline summary.

    Args:
        result: Completed pipeline result.
    """
    print()
    print("=" * 50)
    print("          SmartClean-AI Results")
    print("=" * 50)
    print(f"Total images       : {result.total_images}")
    print(f"Kept               : {result.kept_count}")
    print(f"Review required    : {result.review_count}")
    print(f"Removal candidates : {result.removal_count}")
    print(f"Exact duplicates   : {result.duplicate_count}")
    print("=" * 50)

    print()

    for image_result in result.images:
        analysis = image_result.analysis

        print(
            f"{analysis.image.filename}"
            f" → {analysis.decision.action.value}"
            f" | Score: {analysis.quality.score:.2f}"
        )


def main() -> None:
    """Run the command-line interface."""
    raise SystemExit(run_cli())