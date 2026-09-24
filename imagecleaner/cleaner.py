"""
ImageCleaner File Operations.

This module performs safe filesystem operations based on cleaning
decisions.

Removal candidates are moved to a quarantine directory instead
of being permanently deleted.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from imagecleaner.core.decision_engine import (
    CleaningAction,
    CleaningDecision,
)
from imagecleaner.exceptions.custom_exceptions import ImageProcessingError
from imagecleaner.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class CleaningOperationResult:
    """
    Result of a filesystem cleaning operation.

    Attributes:
        image: Original image path.
        action: Requested cleaning action.
        destination: Destination path when an operation occurred.
        success: Whether the operation succeeded.
        message: Human-readable operation message.
    """

    image: Path
    action: CleaningAction
    destination: Path | None
    success: bool
    message: str


class ImageCleaner:
    """
    Perform safe filesystem operations for cleaning decisions.

    The cleaner uses quarantine instead of permanent deletion.

    KEEP:
        No filesystem modification.

    REVIEW:
        No filesystem modification.

    REMOVE:
        Move the image to the quarantine directory.
    """

    def __init__(
        self,
        quarantine_directory: str | Path,
    ) -> None:
        """
        Initialize the image cleaner.

        Args:
            quarantine_directory: Directory where removal candidates
                will be moved.

        Raises:
            ValueError: If the quarantine path is invalid.
        """
        quarantine_path = Path(quarantine_directory).resolve()

        if quarantine_path.exists() and not quarantine_path.is_dir():
            raise ValueError(
                "Quarantine path must be a directory."
            )

        self._quarantine_directory = quarantine_path

        logger.debug(
            "ImageCleaner initialized: quarantine=%s",
            self._quarantine_directory,
        )

    @property
    def quarantine_directory(self) -> Path:
        """Return the configured quarantine directory."""
        return self._quarantine_directory

    def execute(
        self,
        decision: CleaningDecision,
    ) -> CleaningOperationResult:
        """
        Execute a cleaning decision.

        Args:
            decision: Cleaning decision produced by the
                CleaningDecisionEngine.

        Returns:
            CleaningOperationResult describing the operation.

        Raises:
            ImageProcessingError: If the decision is invalid or
                the filesystem operation fails.
        """
        self._validate_decision(decision)

        image_path = decision.image.path

        logger.info(
            "Executing cleaning action: path=%s, action=%s",
            image_path,
            decision.action,
        )

        if decision.action == CleaningAction.KEEP:
            return self._keep(image_path)

        if decision.action == CleaningAction.REVIEW:
            return self._review(image_path)

        if decision.action == CleaningAction.REMOVE:
            return self._quarantine(image_path)

        raise ImageProcessingError(
            f"Unsupported cleaning action: {decision.action}"
        )

    def _keep(
        self,
        image_path: Path,
    ) -> CleaningOperationResult:
        """
        Handle a KEEP decision.

        No filesystem modification is performed.
        """
        message = "Image kept. No filesystem changes were made."

        logger.info(
            "Image kept: %s",
            image_path,
        )

        return CleaningOperationResult(
            image=image_path,
            action=CleaningAction.KEEP,
            destination=None,
            success=True,
            message=message,
        )

    def _review(
        self,
        image_path: Path,
    ) -> CleaningOperationResult:
        """
        Handle a REVIEW decision.

        No filesystem modification is performed.
        """
        message = (
            "Image requires manual review. "
            "No filesystem changes were made."
        )

        logger.info(
            "Image marked for review: %s",
            image_path,
        )

        return CleaningOperationResult(
            image=image_path,
            action=CleaningAction.REVIEW,
            destination=None,
            success=True,
            message=message,
        )

    def _quarantine(
        self,
        image_path: Path,
    ) -> CleaningOperationResult:
        """
        Move a removal candidate to quarantine.

        Args:
            image_path: Image to move.

        Returns:
            CleaningOperationResult describing the move.

        Raises:
            ImageProcessingError: If the image cannot be moved.
        """
        if not image_path.exists():
            message = (
                f"Cannot quarantine missing image: "
                f"{image_path}"
            )

            logger.error(message)

            raise ImageProcessingError(message)

        if not image_path.is_file():
            message = (
                f"Cannot quarantine non-file path: "
                f"{image_path}"
            )

            logger.error(message)

            raise ImageProcessingError(message)

        self._quarantine_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        destination = self._build_unique_destination(
            image_path
        )

        try:
            shutil.move(
                str(image_path),
                str(destination),
            )

        except OSError as error:
            message = (
                f"Failed to quarantine image "
                f"'{image_path}': {error}"
            )

            logger.error(message)

            raise ImageProcessingError(message) from error

        message = (
            f"Image moved to quarantine: "
            f"{destination}"
        )

        logger.info(message)

        return CleaningOperationResult(
            image=image_path,
            action=CleaningAction.REMOVE,
            destination=destination,
            success=True,
            message=message,
        )

    def _build_unique_destination(
        self,
        image_path: Path,
    ) -> Path:
        """
        Build a unique destination path in quarantine.

        If the original filename already exists, a numeric suffix
        is added.

        Example:

            image.jpg
            image_1.jpg
            image_2.jpg
        """
        destination = (
            self._quarantine_directory
            / image_path.name
        )

        counter = 1

        while destination.exists():
            destination = (
                self._quarantine_directory
                / (
                    f"{image_path.stem}_"
                    f"{counter}"
                    f"{image_path.suffix}"
                )
            )

            counter += 1

        return destination

    @staticmethod
    def _validate_decision(
        decision: CleaningDecision,
    ) -> None:
        """
        Validate a cleaning decision.

        Args:
            decision: Decision to validate.

        Raises:
            ImageProcessingError: If the decision is invalid.
        """
        if not isinstance(
            decision,
            CleaningDecision,
        ):
            raise ImageProcessingError(
                "ImageCleaner expects a CleaningDecision."
            )

        if not decision.image.path:
            raise ImageProcessingError(
                "CleaningDecision contains an empty image path."
            )