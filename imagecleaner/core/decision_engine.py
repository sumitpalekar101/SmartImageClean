"""
ImageCleaner Cleaning Decision Engine.

This module converts an image quality score and duplicate status
into a safe cleaning decision.

The decision engine does not modify, delete, or move files.
It only determines what action should be considered.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from imagecleaner.core.dataset_loader import ImageRecord
from imagecleaner.exceptions.custom_exceptions import ImageProcessingError
from imagecleaner.reports.quality_score import QualityScoreResult
from imagecleaner.utils.logger import get_logger

logger = get_logger(__name__)


class CleaningAction(StrEnum):
    """
    Possible actions produced by the decision engine.
    """

    KEEP = "keep"
    REVIEW = "review"
    REMOVE = "remove"


@dataclass(frozen=True, slots=True)
class DecisionThresholds:
    """
    Thresholds controlling cleaning decisions.

    Attributes:
        keep_score: Minimum quality score required to keep an image.
        remove_score: Maximum quality score allowed for automatic
            removal consideration.

    Scores between remove_score and keep_score are sent for review.
    """

    keep_score: float = 75.0
    remove_score: float = 40.0

    def __post_init__(self) -> None:
        """Validate decision thresholds."""
        if not 0 <= self.remove_score <= 100:
            raise ValueError(
                "remove_score must be between 0 and 100."
            )

        if not 0 <= self.keep_score <= 100:
            raise ValueError(
                "keep_score must be between 0 and 100."
            )

        if self.remove_score >= self.keep_score:
            raise ValueError(
                "remove_score must be less than keep_score."
            )


@dataclass(frozen=True, slots=True)
class CleaningDecision:
    """
    Decision produced for one image.

    Attributes:
        image: Image being evaluated.
        action: Recommended cleaning action.
        quality_score: Overall quality score.
        quality_grade: Human-readable quality grade.
        is_duplicate: Whether the image is an exact duplicate.
        reason: Explanation for the decision.
    """

    image: ImageRecord
    action: CleaningAction
    quality_score: float
    quality_grade: str
    is_duplicate: bool
    reason: str

    @property
    def should_keep(self) -> bool:
        """Return whether the image should be kept."""
        return self.action == CleaningAction.KEEP

    @property
    def requires_review(self) -> bool:
        """Return whether the image requires manual review."""
        return self.action == CleaningAction.REVIEW

    @property
    def is_removal_candidate(self) -> bool:
        """Return whether the image is a removal candidate."""
        return self.action == CleaningAction.REMOVE


class CleaningDecisionEngine:
    """
    Convert quality analysis into cleaning decisions.

    The engine follows a conservative policy:

        1. Exact duplicates are removal candidates.
        2. Very low quality images are removal candidates.
        3. Borderline images require review.
        4. Good-quality images are kept.

    The engine does not perform any filesystem operations.
    """

    def __init__(
        self,
        thresholds: DecisionThresholds | None = None,
    ) -> None:
        """
        Initialize the decision engine.

        Args:
            thresholds: Optional custom decision thresholds.
        """
        self._thresholds = thresholds or DecisionThresholds()

        logger.debug(
            "CleaningDecisionEngine initialized: thresholds=%s",
            self._thresholds,
        )

    @property
    def thresholds(self) -> DecisionThresholds:
        """Return the configured decision thresholds."""
        return self._thresholds

    def decide(
        self,
        *,
        quality_result: QualityScoreResult,
        is_duplicate: bool,
    ) -> CleaningDecision:
        """
        Produce a cleaning decision for an image.

        Args:
            quality_result: Result produced by QualityScorer.
            is_duplicate: Whether the image is an exact duplicate.

        Returns:
            CleaningDecision describing the recommended action.

        Raises:
            ImageProcessingError: If the supplied quality result
                is invalid.
        """
        self._validate_quality_result(quality_result)

        action, reason = self._determine_action(
            quality_score=quality_result.score,
            is_duplicate=is_duplicate,
        )

        decision = CleaningDecision(
            image=quality_result.image,
            action=action,
            quality_score=quality_result.score,
            quality_grade=quality_result.grade,
            is_duplicate=is_duplicate,
            reason=reason,
        )

        logger.info(
            "Cleaning decision: path=%s, action=%s, score=%.2f",
            quality_result.image.path,
            action,
            quality_result.score,
        )

        return decision

    def _determine_action(
        self,
        *,
        quality_score: float,
        is_duplicate: bool,
    ) -> tuple[CleaningAction, str]:
        """
        Determine an action from quality and duplicate status.

        Args:
            quality_score: Overall quality score from 0 to 100.
            is_duplicate: Whether the image is an exact duplicate.

        Returns:
            Tuple containing action and explanation.
        """
        if is_duplicate:
            return (
                CleaningAction.REMOVE,
                "Image is an exact duplicate.",
            )

        if quality_score < self._thresholds.remove_score:
            return (
                CleaningAction.REMOVE,
                "Image quality is below the removal threshold.",
            )

        if quality_score < self._thresholds.keep_score:
            return (
                CleaningAction.REVIEW,
                "Image quality falls within the manual-review range.",
            )

        return (
            CleaningAction.KEEP,
            "Image meets the configured quality threshold.",
        )

    @staticmethod
    def _validate_quality_result(
        quality_result: QualityScoreResult,
    ) -> None:
        """
        Validate the quality result.

        Args:
            quality_result: Result to validate.

        Raises:
            ImageProcessingError: If the result is invalid.
        """
        if not isinstance(
            quality_result,
            QualityScoreResult,
        ):
            raise ImageProcessingError(
                "CleaningDecisionEngine expects a "
                "QualityScoreResult."
            )

        if not isinstance(
            quality_result.image,
            ImageRecord,
        ):
            raise ImageProcessingError(
                "QualityScoreResult contains an invalid image."
            )

        if not 0 <= quality_result.score <= 100:
            raise ImageProcessingError(
                "Quality score must be between 0 and 100."
            )