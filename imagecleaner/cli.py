
"""
SmartClean-AI Command Line Interface.

This module provides the user-facing command-line interface
for running the image-cleaning pipeline and generating reports.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from imagecleaner.core.pipeline import ImageCleanerPipeline
from imagecleaner.exceptions.custom_exceptions import ImageProcessingError
from imagecleaner.reports.review_report import ReviewReportGenerator
from imagecleaner.reports.report_generator import ReportGenerator
from imagecleaner.utils.logger import get_logger

logger = get_logger(__name__)

def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="smartclean",
        description="SmartImageClean image cleaning and quality analysis.",
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
        help="Directory used for removal candidates. Default: quarantine",
    )

    parser.add_argument(
        "--clean",
        action="store_true",
        help=(
            "Execute removal decisions by moving candidates to quarantine. "
            "Without this option, the run is analysis-only."
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
        help="Directory used for standardized images. Default: standardized",
    )

    return parser


def run_cli(arguments: list[str] | None = None) -> int:
    """
    Run the SmartClean-AI command-line interface.

    Returns:
        Process exit code: 0 on success, 1 on processing failure,
        or 130 if interrupted by the user.
    """
    parser = build_parser()
    args = parser.parse_args(arguments)

    input_path = args.input.resolve()
    quarantine_path = args.quarantine.resolve()

    if not input_path.exists():
        parser.error(f"Input directory does not exist: {input_path}")

    if not input_path.is_dir():
        parser.error(f"Input path is not a directory: {input_path}")

    logger.info(
        "Starting CLI run: input=%s, clean=%s, process=%s",
        input_path,
        args.clean,
        args.process,
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

        # Use the configured output directory for every report.
        output_settings = pipeline.settings.output
        output_directory = output_settings.output_directory

        # 1. Generate the existing text review report.
        text_generator = ReviewReportGenerator(output_directory)
        text_path = text_generator.generate(result)

        print(f"\nText report: {text_path}")
        logger.info("Text report generated: %s", text_path)

        # 2. Generate CSV and JSON reports when enabled.
        data_generator = ReportGenerator(output_directory)

        if output_settings.generate_csv_report:
            csv_path = data_generator.generate_csv(result)
            print(f"CSV report:  {csv_path}")
            logger.info("CSV report generated: %s", csv_path)

        if output_settings.generate_json_report:
            json_path = data_generator.generate_json(result)
            print(f"JSON report: {json_path}")
            logger.info("JSON report generated: %s", json_path)

    except ImageProcessingError as error:
        logger.error("SmartClean-AI processing failed: %s", error)
        print(f"Error: {error}", file=sys.stderr)
        return 1

    except KeyboardInterrupt:
        logger.warning("SmartClean-AI execution interrupted by user.")
        print("\nOperation cancelled.", file=sys.stderr)
        return 130

    _print_summary(result)
    return 0


def _print_summary(result) -> None:
    """Print a human-readable pipeline summary."""
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
            f" -> {analysis.decision.action.value}"
            f" | Score: {analysis.quality.score:.2f}"
        )


def main() -> None:
    """Run the command-line interface."""
    raise SystemExit(run_cli())


if __name__ == "__main__":
    main()
