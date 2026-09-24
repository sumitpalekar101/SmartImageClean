"""
SmartClean-AI Processing Pipeline.

The pipeline coordinates dataset discovery, metadata extraction,
quality detection, configuration-based analysis, cleaning decisions,
automatic standardization, restoration, and optional safe cleaning.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from math import isclose
from pathlib import Path

from imagecleaner.cleaner import (
    CleaningOperationResult,
    ImageCleaner,
)
from imagecleaner.config.settings import ImageCleanerSettings
from imagecleaner.core.dataset_loader import (
    Dataset,
    DatasetLoader,
    ImageRecord,
)
from imagecleaner.core.decision_engine import (
    CleaningDecision,
    CleaningDecisionEngine,
)
from imagecleaner.core.image_metadata import (
    ImageMetadata,
    ImageMetadataExtractor,
)
from imagecleaner.detectors.blur_detector import (
    BlurDetectionResult,
    BlurDetector,
)
from imagecleaner.detectors.brightness_detector import (
    BrightnessDetectionResult,
    BrightnessDetector,
)
from imagecleaner.detectors.duplicate_detector import (
    DuplicateDetectionResult,
    DuplicateDetector,
)
from imagecleaner.detectors.resolution_detector import (
    ResolutionDetectionResult,
    ResolutionDetector,
)
from imagecleaner.exceptions.custom_exceptions import ImageProcessingError
from imagecleaner.reports.quality_score import (
    QualityScorer,
    QualityScoreResult,
)
from imagecleaner.restoration import ImageRestorer
from imagecleaner.standardization import ImageStandardizer
from imagecleaner.utils.logger import get_logger

logger = get_logger(__name__)


# ================================================================
# Analysis Result Classes
# ================================================================


@dataclass(frozen=True, slots=True)
class ConfigurationAnalysis:
    """Result of comparing image properties with active requirements."""

    acceptable: bool
    checks: dict[str, bool]
    reasons: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ImageAnalysis:
    """Complete analysis result for one image."""

    image: ImageRecord
    metadata: ImageMetadata
    blur: BlurDetectionResult
    brightness: BrightnessDetectionResult
    resolution: ResolutionDetectionResult
    quality: QualityScoreResult
    decision: CleaningDecision
    is_duplicate: bool
    configuration: ConfigurationAnalysis | None = None


@dataclass(frozen=True, slots=True)
class PipelineImageResult:
    """Final result for one processed image."""

    analysis: ImageAnalysis
    operation: CleaningOperationResult | None = None


@dataclass(frozen=True, slots=True)
class ProcessingSummary:
    """
    Summary of automatic standardization processing.

    This stores only the information required for the final report.
    """

    initial_total: int
    initial_acceptable: int
    initial_unacceptable: int
    standardized_count: int


@dataclass(frozen=True, slots=True)
class PipelineResult:
    """Final result of an entire dataset pipeline run."""

    dataset: Dataset
    images: tuple[PipelineImageResult, ...]
    processing: ProcessingSummary | None = None

    @property
    def total_images(self) -> int:
        """Return the number of processed images."""
        return len(self.images)

    @property
    def kept_count(self) -> int:
        """Return the number of images kept."""
        return sum(
            result.analysis.decision.should_keep
            for result in self.images
        )

    @property
    def review_count(self) -> int:
        """Return the number of images requiring review."""
        return sum(
            result.analysis.decision.requires_review
            for result in self.images
        )

    @property
    def removal_count(self) -> int:
        """Return the number of removal candidates."""
        return sum(
            result.analysis.decision.is_removal_candidate
            for result in self.images
        )

    @property
    def duplicate_count(self) -> int:
        """Return the number of exact duplicate images."""
        return sum(
            result.analysis.is_duplicate
            for result in self.images
        )

    @property
    def acceptable_count(self) -> int:
        """Return the number of configuration-acceptable images."""
        return sum(
            result.analysis.configuration is not None
            and result.analysis.configuration.acceptable
            for result in self.images
        )

    @property
    def unacceptable_count(self) -> int:
        """Return the number of configuration-unacceptable images."""
        return sum(
            result.analysis.configuration is not None
            and not result.analysis.configuration.acceptable
            for result in self.images
        )


# ================================================================
# Main Pipeline
# ================================================================


class ImageCleanerPipeline:
    """Orchestrate the SmartClean-AI processing workflow."""

    def __init__(
        self,
        dataset_path: str | Path,
        *,
        quarantine_directory: str | Path = "quarantine",
        clean: bool = False,
        settings: ImageCleanerSettings | None = None,
    ) -> None:
        """
        Initialize the pipeline.

        Args:
            dataset_path: Directory containing images.
            quarantine_directory: Destination for removal candidates.
            clean: Whether removal decisions should be executed.
            settings: Optional SmartClean-AI configuration.
        """
        self._loader = DatasetLoader(dataset_path)

        self._settings = settings or ImageCleanerSettings()

        self._metadata_extractor = ImageMetadataExtractor()

        self._blur_detector = BlurDetector(
            threshold=self._detector_blur_threshold()
        )

        self._brightness_detector = BrightnessDetector(
            lower_threshold=self._detector_min_brightness(),
            upper_threshold=self._detector_max_brightness(),
        )

        self._resolution_detector = ResolutionDetector(
            minimum_width=self._detector_min_width(),
            minimum_height=self._detector_min_height(),
        )

        self._duplicate_detector = DuplicateDetector()
        self._quality_scorer = QualityScorer()
        self._decision_engine = CleaningDecisionEngine()

        self._cleaner = ImageCleaner(
            quarantine_directory
        )

        self._standardizer = ImageStandardizer()
        self._restorer = ImageRestorer()

        self._clean = clean

        logger.info(
            "ImageCleanerPipeline initialized: clean=%s",
            clean,
        )

    # ============================================================
    # Properties
    # ============================================================

    @property
    def clean(self) -> bool:
        """Return whether filesystem cleaning is enabled."""
        return self._clean

    @property
    def settings(self) -> ImageCleanerSettings:
        """Return the current pipeline configuration."""
        return self._settings

    # ============================================================
    # Configuration
    # ============================================================

    def configure(
        self,
        **overrides: object,
    ) -> ImageCleanerSettings:
        """
        Partially update the active cleaning configuration.

        Unspecified settings retain their current values.

        Returns:
            Updated ImageCleanerSettings.

        Raises:
            ValueError: If an unknown setting is supplied.
        """
        valid_fields = {
            "min_width",
            "max_width",
            "min_height",
            "max_height",
            "min_brightness",
            "max_brightness",
            "blur_threshold",
            "min_quality_score",
            "required_format",
            "required_color_mode",
            "required_aspect_ratio",
            "max_file_size",
            "check_duplicates",
            "check_blur",
            "check_resolution",
            "check_brightness",
        }

        unknown = set(overrides) - valid_fields

        if unknown:
            names = ", ".join(sorted(unknown))
            raise ValueError(
                f"Unknown configuration setting(s): {names}"
            )

        updated_cleaning = replace(
            self._settings.cleaning,
            **overrides,
        )

        self._settings = ImageCleanerSettings(
            cleaning=updated_cleaning,
            output=self._settings.output,
        )

        self._refresh_detectors()

        logger.info(
            "SmartClean-AI configuration updated."
        )

        return self._settings

    # ============================================================
    # Restoration
    # ============================================================

    def restore(
        self,
        image_path: str | Path,
        output_path: str | Path,
        *,
        brightness: float = 1.0,
        contrast: float = 1.0,
        sharpness: float = 1.0,
        denoise: bool = False,
        upscale: float = 1.0,
    ) -> Path:
        """Restore and enhance an image using configured operations."""
        return self._restorer.restore(
            image_path,
            output_path,
            brightness=brightness,
            contrast=contrast,
            sharpness=sharpness,
            denoise=denoise,
            upscale=upscale,
        )

    # ============================================================
    # Standardization
    # ============================================================

    def standardize(
        self,
        image_path: str | Path,
        output_path: str | Path,
    ) -> Path:
        """Standardize an image using the active configuration."""
        settings = self._settings.cleaning

        return self._standardizer.standardize(
            image_path,
            output_path,
            required_format=settings.required_format,
            required_color_mode=settings.required_color_mode,
            min_width=settings.min_width,
            max_width=settings.max_width,
            min_height=settings.min_height,
            max_height=settings.max_height,
            required_aspect_ratio=settings.required_aspect_ratio,
        )

    # ============================================================
    # Normal Analysis Run
    # ============================================================

    def run(self) -> PipelineResult:
        """
        Process the configured dataset.

        Returns:
            PipelineResult containing all image-level results.

        Raises:
            ImageProcessingError: If processing fails.
        """
        logger.info(
            "Starting SmartClean-AI pipeline."
        )

        dataset = self._loader.discover()

        duplicate_result = self._duplicate_detector.analyze(
            dataset.images
        )

        duplicate_paths = self._build_duplicate_path_set(
            duplicate_result
        )

        results: list[PipelineImageResult] = []

        for image in dataset.images:
            try:
                result = self._process_image(
                    image=image,
                    duplicate_paths=duplicate_paths,
                )

                results.append(result)

            except ImageProcessingError:
                logger.exception(
                    "Image processing failed: %s",
                    image.path,
                )
                raise

        pipeline_result = PipelineResult(
            dataset=dataset,
            images=tuple(results),
        )

        logger.info(
            "SmartClean-AI pipeline completed: "
            "total=%d, kept=%d, review=%d, removal=%d, "
            "duplicates=%d, acceptable=%d, unacceptable=%d",
            pipeline_result.total_images,
            pipeline_result.kept_count,
            pipeline_result.review_count,
            pipeline_result.removal_count,
            pipeline_result.duplicate_count,
            pipeline_result.acceptable_count,
            pipeline_result.unacceptable_count,
        )

        return pipeline_result

    # ============================================================
    # Automatic Processing
    # ============================================================

    def process(
        self,
        *,
        standardized_directory: str | Path = "standardized",
    ) -> PipelineResult:
        """
        Automatically standardize unacceptable images and re-analyze them.

        The original images are preserved. Standardized images are
        written to a separate directory.
        """
        if self._clean:
            raise ValueError(
                "Automatic standardization cannot be combined with "
                "filesystem cleaning. Use clean=False for process()."
            )

        logger.info(
            "Starting automatic SmartClean-AI processing."
        )

        # --------------------------------------------------------
        # Step 1: Initial analysis
        # --------------------------------------------------------

        initial_result = self.run()

        standardized_directory = Path(
            standardized_directory
        )

        unacceptable_images = [
            result.analysis.image
            for result in initial_result.images
            if (
                result.analysis.configuration is not None
                and not result.analysis.configuration.acceptable
            )
        ]

        # --------------------------------------------------------
        # Step 2: Nothing requires standardization
        # --------------------------------------------------------

        if not unacceptable_images:
            logger.info(
                "All images already satisfy the active configuration."
            )

            return initial_result

        # --------------------------------------------------------
        # Step 3: Standardize unacceptable images
        # --------------------------------------------------------

        for image in unacceptable_images:
            relative_path = image.path.relative_to(
                self._loader.dataset_path
            )

            output_path = (
                standardized_directory / relative_path
            )

            self.standardize(
                image.path,
                output_path,
            )

        standardized_count = len(
            unacceptable_images
        )

        logger.info(
            "Standardization completed for %d image(s). "
            "Re-analyzing standardized dataset.",
            standardized_count,
        )

        # --------------------------------------------------------
        # Step 4: Re-analyze standardized images
        # --------------------------------------------------------

        final_pipeline = ImageCleanerPipeline(
            standardized_directory,
            quarantine_directory="quarantine",
            clean=False,
            settings=self._settings,
        )

        final_result = final_pipeline.run()

        # --------------------------------------------------------
        # Step 5: Store processing summary
        # --------------------------------------------------------

        processing_summary = ProcessingSummary(
            initial_total=initial_result.total_images,
            initial_acceptable=initial_result.acceptable_count,
            initial_unacceptable=initial_result.unacceptable_count,
            standardized_count=standardized_count,
        )

        final_result = replace(
            final_result,
            processing=processing_summary,
        )

        logger.info(
            "Automatic processing completed: "
            "initial_unacceptable=%d, "
            "final_acceptable=%d, "
            "final_unacceptable=%d",
            standardized_count,
            final_result.acceptable_count,
            final_result.unacceptable_count,
        )

        return final_result

    # ============================================================
    # Single Image Processing
    # ============================================================

    def _process_image(
        self,
        *,
        image: ImageRecord,
        duplicate_paths: set[Path],
    ) -> PipelineImageResult:
        """Process one image through the analysis pipeline."""
        logger.debug(
            "Processing image: %s",
            image.path,
        )

        metadata = self._metadata_extractor.extract(
            image
        )

        blur_result = self._blur_detector.detect(
            image
        )

        brightness_result = self._brightness_detector.detect(
            image
        )

        resolution_result = self._resolution_detector.detect(
            metadata
        )

        is_duplicate = image.path in duplicate_paths

        quality_result = self._quality_scorer.calculate(
            image=image,
            blur=blur_result,
            brightness=brightness_result,
            resolution=resolution_result,
            is_duplicate=is_duplicate,
        )

        decision = self._decision_engine.decide(
            quality_result=quality_result,
            is_duplicate=is_duplicate,
        )

        configuration_result = self._analyze_configuration(
            metadata=metadata,
            blur=blur_result,
            brightness=brightness_result,
            quality=quality_result,
            is_duplicate=is_duplicate,
        )

        analysis = ImageAnalysis(
            image=image,
            metadata=metadata,
            blur=blur_result,
            brightness=brightness_result,
            resolution=resolution_result,
            quality=quality_result,
            decision=decision,
            is_duplicate=is_duplicate,
            configuration=configuration_result,
        )

        operation = None

        if self._clean:
            operation = self._cleaner.execute(
                decision
            )

        return PipelineImageResult(
            analysis=analysis,
            operation=operation,
        )

    # ============================================================
    # Configuration Analysis
    # ============================================================

    def _analyze_configuration(
        self,
        *,
        metadata: ImageMetadata,
        blur: BlurDetectionResult,
        brightness: BrightnessDetectionResult,
        quality: QualityScoreResult,
        is_duplicate: bool,
    ) -> ConfigurationAnalysis:
        """
        Compare actual image properties with active configuration.
        """
        settings = self._settings.cleaning

        checks: dict[str, bool] = {}
        reasons: list[str] = []

        # --------------------------------------------------------
        # Resolution checks
        # --------------------------------------------------------

        if settings.check_resolution:
            self._check_dimension(
                checks=checks,
                reasons=reasons,
                name="min_width",
                value=metadata.width,
                minimum=settings.min_width,
            )

            self._check_dimension(
                checks=checks,
                reasons=reasons,
                name="max_width",
                value=metadata.width,
                maximum=settings.max_width,
            )

            self._check_dimension(
                checks=checks,
                reasons=reasons,
                name="min_height",
                value=metadata.height,
                minimum=settings.min_height,
            )

            self._check_dimension(
                checks=checks,
                reasons=reasons,
                name="max_height",
                value=metadata.height,
                maximum=settings.max_height,
            )

        # --------------------------------------------------------
        # Brightness check
        # --------------------------------------------------------

        if settings.check_brightness:
            self._check_brightness(
                checks=checks,
                reasons=reasons,
                brightness=brightness.score,
                minimum=settings.min_brightness,
                maximum=settings.max_brightness,
            )

        # --------------------------------------------------------
        # Blur / sharpness check
        # --------------------------------------------------------

        if (
            settings.check_blur
            and settings.blur_threshold is not None
        ):
            passed = (
                blur.score
                >= settings.blur_threshold
            )

            checks["blur_threshold"] = passed

            if not passed:
                reasons.append(
                    "Image is below the configured "
                    "blur/sharpness threshold."
                )

        # --------------------------------------------------------
        # Format check
        # --------------------------------------------------------

        if settings.required_format is not None:
            passed = (
                metadata.image_format.upper()
                == settings.required_format.upper()
            )

            checks["required_format"] = passed

            if not passed:
                reasons.append(
                    "Image format does not match the "
                    "required format."
                )

        # --------------------------------------------------------
        # Color mode check
        # --------------------------------------------------------

        if settings.required_color_mode is not None:
            passed = (
                metadata.mode.upper()
                == settings.required_color_mode.upper()
            )

            checks["required_color_mode"] = passed

            if not passed:
                reasons.append(
                    "Image color mode does not match "
                    "the required color mode."
                )

        # --------------------------------------------------------
        # Aspect ratio check
        # --------------------------------------------------------

        if settings.required_aspect_ratio is not None:
            passed = isclose(
                metadata.aspect_ratio,
                settings.required_aspect_ratio,
                rel_tol=0.01,
                abs_tol=0.01,
            )

            checks["required_aspect_ratio"] = passed

            if not passed:
                reasons.append(
                    "Image aspect ratio does not match "
                    "the required aspect ratio."
                )

        # --------------------------------------------------------
        # File size check
        # --------------------------------------------------------

        if settings.max_file_size is not None:
            passed = (
                metadata.file_size_bytes
                <= settings.max_file_size
            )

            checks["max_file_size"] = passed

            if not passed:
                reasons.append(
                    "Image file size exceeds the "
                    "configured maximum."
                )

        # --------------------------------------------------------
        # Duplicate check
        # --------------------------------------------------------

        if settings.check_duplicates:
            passed = not is_duplicate

            checks["duplicate_check"] = passed

            if not passed:
                reasons.append(
                    "Image is an exact duplicate."
                )

        # --------------------------------------------------------
        # Quality score check
        # --------------------------------------------------------

        if settings.min_quality_score is not None:
            passed = (
                quality.score
                >= settings.min_quality_score
            )

            checks["min_quality_score"] = passed

            if not passed:
                reasons.append(
                    "Image quality score is below "
                    "the configured minimum."
                )

        return ConfigurationAnalysis(
            acceptable=all(checks.values()),
            checks=checks,
            reasons=tuple(reasons),
        )

    # ============================================================
    # Dimension Helper
    # ============================================================

    @staticmethod
    def _check_dimension(
        *,
        checks: dict[str, bool],
        reasons: list[str],
        name: str,
        value: int,
        minimum: int | None = None,
        maximum: int | None = None,
    ) -> None:
        """Check one dimension against configured limits."""

        if minimum is not None:
            passed = value >= minimum

            checks[name] = passed

            if not passed:
                reasons.append(
                    f"Image {name.removeprefix('min_')} "
                    f"is below the configured minimum."
                )

        if maximum is not None:
            passed = value <= maximum

            checks[name] = passed

            if not passed:
                reasons.append(
                    f"Image {name.removeprefix('max_')} "
                    f"exceeds the configured maximum."
                )

    # ============================================================
    # Brightness Helper
    # ============================================================

    @staticmethod
    def _check_brightness(
        *,
        checks: dict[str, bool],
        reasons: list[str],
        brightness: float,
        minimum: float | None,
        maximum: float | None,
    ) -> None:
        """Check brightness against configured limits."""

        if minimum is not None:
            passed = brightness >= minimum

            checks["min_brightness"] = passed

            if not passed:
                reasons.append(
                    "Image brightness is below the "
                    "configured minimum."
                )

        if maximum is not None:
            passed = brightness <= maximum

            checks["max_brightness"] = passed

            if not passed:
                reasons.append(
                    "Image brightness exceeds the "
                    "configured maximum."
                )

    # ============================================================
    # Detector Refresh
    # ============================================================

    def _refresh_detectors(self) -> None:
        """Recreate detectors using the active configuration."""

        self._blur_detector = BlurDetector(
            threshold=self._detector_blur_threshold()
        )

        self._brightness_detector = BrightnessDetector(
            lower_threshold=self._detector_min_brightness(),
            upper_threshold=self._detector_max_brightness(),
        )

        self._resolution_detector = ResolutionDetector(
            minimum_width=self._detector_min_width(),
            minimum_height=self._detector_min_height(),
        )

    # ============================================================
    # Detector Configuration Helpers
    # ============================================================

    def _detector_blur_threshold(self) -> float:
        """Return a valid blur detector threshold."""
        return (
            self._settings.cleaning.blur_threshold
            if self._settings.cleaning.blur_threshold
            is not None
            else 0.0
        )

    def _detector_min_brightness(self) -> float:
        """Return a valid detector brightness minimum."""
        return (
            self._settings.cleaning.min_brightness
            if self._settings.cleaning.min_brightness
            is not None
            else 0.0
        )

    def _detector_max_brightness(self) -> float:
        """Return a valid detector brightness maximum."""
        return (
            self._settings.cleaning.max_brightness
            if self._settings.cleaning.max_brightness
            is not None
            else 255.0
        )

    def _detector_min_width(self) -> int:
        """Return a valid detector minimum width."""
        return (
            self._settings.cleaning.min_width
            if self._settings.cleaning.min_width
            is not None
            else 1
        )

    def _detector_min_height(self) -> int:
        """Return a valid detector minimum height."""
        return (
            self._settings.cleaning.min_height
            if self._settings.cleaning.min_height
            is not None
            else 1
        )

    # ============================================================
    # Duplicate Helper
    # ============================================================

    @staticmethod
    def _build_duplicate_path_set(
        duplicate_result: DuplicateDetectionResult,
    ) -> set[Path]:
        """Build a set containing exact duplicate image paths."""

        duplicate_paths: set[Path] = set()

        for group in duplicate_result.exact_duplicate_groups:
            for image in group:
                duplicate_paths.add(image.path)

        return duplicate_paths