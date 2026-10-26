
"""Brightness enhancement using gamma correction and CLAHE."""

from pathlib import Path

import cv2
import numpy as np

from imagecleaner.exceptions.custom_exceptions import ImageProcessingError


def correct_brightness(
    image_path: str | Path,
    output_path: str | Path,
    *,
    target_mean: float = 125.0,
) -> Path:
    """Brighten shadows and improve local contrast using CLAHE."""

    if not 0 <= target_mean <= 255:
        raise ValueError("target_mean must be between 0 and 255.")

    image_path = Path(image_path)
    output_path = Path(output_path)

    image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)

    if image is None:
        raise ImageProcessingError(
            f"Unable to read image: {image_path}"
        )

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    current_mean = float(gray.mean())

    if current_mean < 1:
        raise ImageProcessingError(
            "Image is too dark for reliable brightness correction."
        )

    # Use a gentle gamma curve to lift shadows.
    # Lower gamma brightens the image; gamma=1 leaves it unchanged.
    gamma = 0.75
    lookup = np.array(
        [
            round(((value / 255.0) ** gamma) * 255)
            for value in range(256)
        ],
        dtype=np.uint8,
    )
    gamma_corrected = cv2.LUT(image, lookup)

    # Apply CLAHE to luminance, preserving the color channels.
    lab = cv2.cvtColor(gamma_corrected, cv2.COLOR_BGR2LAB)
    luminance, channel_a, channel_b = cv2.split(lab)

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8),
    )
    enhanced_luminance = clahe.apply(luminance)

    enhanced_lab = cv2.merge(
        (enhanced_luminance, channel_a, channel_b)
    )
    corrected = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not cv2.imwrite(str(output_path), corrected):
        raise ImageProcessingError(
            f"Unable to save enhanced image: {output_path}"
        )

    return output_path
