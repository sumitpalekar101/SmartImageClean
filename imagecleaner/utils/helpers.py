"""
ImageCleaner General Utility Functions.

This module contains small, reusable helper functions that are
not specific to dataset loading, image detection, reporting,
or logging.
"""

from __future__ import annotations

from collections.abc import Iterable


def clamp(
    value: float,
    minimum: float,
    maximum: float,
) -> float:
    """
    Restrict a numeric value to a specified range.

    Args:
        value: Value to restrict.
        minimum: Lowest allowed value.
        maximum: Highest allowed value.

    Returns:
        The value restricted to the specified range.

    Raises:
        ValueError: If minimum is greater than maximum.
    """
    if minimum > maximum:
        raise ValueError(
            "minimum must not be greater than maximum."
        )

    return max(minimum, min(value, maximum))


def calculate_percentage(
    part: float,
    total: float,
) -> float:
    """
    Calculate the percentage represented by part out of total.

    Args:
        part: Portion of the total.
        total: Total value.

    Returns:
        Percentage value between 0 and 100.

    Raises:
        ValueError: If total is zero or negative.
    """
    if total <= 0:
        raise ValueError(
            "total must be greater than zero."
        )

    return (part / total) * 100


def safe_percentage(
    part: float,
    total: float,
) -> float:
    """
    Calculate a percentage without raising an exception for zero total.

    Args:
        part: Portion of the total.
        total: Total value.

    Returns:
        Percentage value between 0 and 100.
        Returns 0.0 when total is zero.
    """
    if total == 0:
        return 0.0

    return (part / total) * 100


def format_percentage(
    percentage: float,
    decimal_places: int = 2,
) -> str:
    """
    Format a percentage value for human-readable output.

    Args:
        percentage: Percentage value.
        decimal_places: Number of decimal places.

    Returns:
        Formatted percentage string.

    Raises:
        ValueError: If decimal_places is negative.
    """
    if decimal_places < 0:
        raise ValueError(
            "decimal_places must not be negative."
        )

    return f"{percentage:.{decimal_places}f}%"


def ensure_not_empty(
    value: str,
    field_name: str,
) -> str:
    """
    Validate that a string contains meaningful content.

    Args:
        value: String to validate.
        field_name: Name of the field being validated.

    Returns:
        The stripped string.

    Raises:
        ValueError: If the value is empty or contains only whitespace.
    """
    normalized_value = value.strip()

    if not normalized_value:
        raise ValueError(
            f"{field_name} must not be empty."
        )

    return normalized_value


def unique_preserve_order[T](
    values: Iterable[T],
) -> list[T]:
    """
    Remove duplicate values while preserving their original order.

    Args:
        values: Iterable containing potentially duplicated values.

    Returns:
        List containing unique values in their original order.
    """
    return list(dict.fromkeys(values))


def chunked[T](
    values: Iterable[T],
    size: int,
) -> list[list[T]]:
    """
    Split an iterable into fixed-size chunks.

    Args:
        values: Values to divide into chunks.
        size: Maximum number of items per chunk.

    Returns:
        List of chunks.

    Raises:
        ValueError: If size is less than or equal to zero.
    """
    if size <= 0:
        raise ValueError(
            "size must be greater than zero."
        )

    items = list(values)

    return [
        items[index:index + size]
        for index in range(0, len(items), size)
    ]