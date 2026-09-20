"""Money helper: 1 B = 1000 units (integer, BIGINT)."""
from __future__ import annotations


B_PER_UNIT = 1000


def units_to_b_display(units: int) -> str:
    """Convert integer units to display string.

    Examples:
        25000 -> "25"
        12400 -> "12.4"
        200   -> "0.2"
        1500  -> "1.5"
    """
    b_int = units // B_PER_UNIT
    remainder = units % B_PER_UNIT
    if remainder == 0:
        return str(b_int)
    # Trim trailing zeros from fractional part
    frac = f"{remainder:03d}".rstrip("0")
    return f"{b_int}.{frac}"


def b_to_units(b: int) -> int:
    """Whole B to units. Only accepts integers."""
    return b * B_PER_UNIT
