"""Unit conversion system for allometric calculations.

This module provides unit conversion functionality using Pint library,
enabling automatic unit handling and conversion throughout pylometree.

Example:
    >>> from pylometree.units import convert_units, set_units
    >>> # Convert diameter from cm to inches
    >>> d_cm = 25.0
    >>> d_in = convert_units(d_cm, "cm", "in")
    >>> print(f"Diameter: {d_in:.2f} in")
    Diameter: 9.84 in
    >>> # Set units on a value
    >>> volume = set_units(1.5, "m^3")
    >>> print(f"Volume: {volume}")
    Volume: 1.5 * meter ** 3
"""

from __future__ import annotations

from typing import Union

import pint
from numpy import ndarray
from pandas import DataFrame, Series
from scipy import stats

# Initialize Pint registry
_unit_registry = pint.UnitRegistry()
_quantity = _unit_registry.Quantity

# Cache for unit strings to Quantity objects
_unit_cache: dict[str, pint.Quantity] = {}


def _get_unit(unit_str: str) -> pint.Quantity:
    """Get or create a unit Quantity from a string.

    Args:
        unit_str: Unit string (e.g., "m", "cm", "m^3", "kg")

    Returns:
        Pint Quantity representing the unit
    """
    if unit_str not in _unit_cache:
        _unit_cache[unit_str] = _quantity(1, unit_str)
    return _unit_cache[unit_str]


def set_units(
    value: Union[float, int, ndarray, Series], unit_str: str | None = None
) -> pint.Quantity:
    """Attach units to a numeric value or array.

    Args:
        value: Numeric value or array
        unit_str: Unit string (e.g., "m", "cm", "m^3", "kg"). If None, dimensionless.

    Returns:
        Pint Quantity with units attached

    Example:
        >>> set_units(25.5, "cm")
        25.5 * centimeter
        >>> set_units([1, 2, 3], "m")
        [1. 2. 3.] * meter
        >>> set_units(42.0)
        42.0 * dimensionless
    """
    if unit_str is None:
        unit_str = "dimensionless"
    return _quantity(value, unit_str)


def convert_units(
    value: Union[float, int, ndarray, Series, pint.Quantity],
    from_unit: str | None = None,
    to_unit: str | None = None,
) -> Union[float, int, ndarray, Series, pint.Quantity]:
    """Convert a value from one unit to another.

    Args:
        value: Value to convert (can be scalar, array, or already-quantified)
        from_unit: Source unit string (required if value is not quantified)
        to_unit: Target unit string (required for conversion)

    Returns:
        Converted value (magnitude if scalar/array, Quantity if input was Quantity)

    Raises:
        ValueError: If from_unit is None when value has no units
        ValueError: If to_unit is None
        pint.DimensionalityError: If units are incompatible

    Example:
        >>> convert_units(25.5, "cm", "in")
        10.039370078740158
        >>> convert_units(set_units(100, "m"), to_unit="ft")
        328.0839895013123
    """
    if to_unit is None:
        raise ValueError("to_unit required for conversion")

    if isinstance(value, pint.Quantity):
        # Value already has units
        return value.to(to_unit).magnitude
    else:
        # Value needs units attached first
        if from_unit is None:
            raise ValueError("from_unit required when value has no units")
        return _quantity(value, from_unit).to(to_unit).magnitude


def strip_units(value: pint.Quantity) -> float:
    """Strip units and return numeric value.

    Args:
        value: Pint Quantity

    Returns:
        Numeric value without units

    Example:
        >>> strip_units(set_units(25.5, "cm"))
        25.5
    """
    return float(value.magnitude)


def ensure_units(
    value: Union[float, int, ndarray, Series, pint.Quantity],
    expected_unit: str,
) -> pint.Quantity:
    """Ensure a value has the expected units, converting if necessary.

    Args:
        value: Input value (may already have units)
        expected_unit: Expected unit string

    Returns:
        Value with expected units

    Example:
        >>> ensure_units(25.5, "cm")
        25.5 * centimeter
        >>> ensure_units(set_units(10, "m"), "cm")
        1000.0 * centimeter
    """
    if isinstance(value, pint.Quantity):
        return value.to(expected_unit)
    else:
        return _quantity(value, expected_unit)


def compatible_units(unit1: str, unit2: str) -> bool:
    """Check if two units are dimensionally compatible.

    Args:
        unit1: First unit string
        unit2: Second unit string

    Returns:
        True if units are compatible, False otherwise

    Example:
        >>> compatible_units("m", "cm")
        True
        >>> compatible_units("m", "kg")
        False
    """
    try:
        u1 = _get_unit(unit1)
        u2 = _get_unit(unit2)
        u1.to(u2)
        return True
    except (pint.DimensionalityError, ValueError):
        return False


def get_base_unit(unit_str: str) -> str:
    """Get the base unit for a given unit.

    Args:
        unit_str: Input unit string

    Returns:
        Base unit string (e.g., "meter" for "centimeter")

    Example:
        >>> get_base_unit("cm")
        'meter'
        >>> get_base_unit("m^3")
        'meter ** 3'
    """
    return str(_get_unit(unit_str).to_base_units().units)


# Predefined common forestry units
class Units:
    """Common forestry units as convenience attributes."""

    # Length/distance
    METER = "meter"
    METERS = "meter"
    CENTIMETER = "centimeter"
    CENTIMETERS = "centimeter"
    MILLIMETER = "millimeter"
    MILLIMETERS = "millimeter"
    KILOMETER = "kilometer"
    KILOMETERS = "kilometer"
    INCH = "inch"
    INCHES = "inch"
    FOOT = "foot"
    FEET = "foot"
    METER_PER_SECOND = "m/s"
    METER_PER_SECOND_SQUARED = "m/s^2"

    # Area
    SQUARE_METER = "square_meter"
    SQUARE_METERS = "square_meter"
    SQUARE_CENTIMETER = "square_centimeter"
    SQUARE_CENTIMETERS = "square_centimeter"
    HECTARE = "hectare"
    HECTARES = "hectare"
    ACRE = "acre"
    ACRES = "acre"

    # Volume
    CUBIC_METER = "cubic_meter"
    CUBIC_METERS = "cubic_meter"
    CUBIC_CENTIMETER = "cubic_centimeter"
    CUBIC_CENTIMETERS = "cubic_centimeter"
    LITER = "liter"
    LITERS = "liter"

    # Mass/weight
    KILOGRAM = "kilogram"
    KILOGRAMS = "kilogram"
    GRAM = "gram"
    GRAMS = "gram"
    TONNE = "tonne"
    TONNES = "tonne"
    POUND = "pound"
    POUNDS = "pound"
    TON = "ton"
    TONS = "ton"

    # Time
    SECOND = "second"
    SECONDS = "second"
    MINUTE = "minute"
    MINUTES = "minute"
    HOUR = "hour"
    HOURS = "hour"
    DAY = "day"
    DAYS = "day"
    YEAR = "year"
    YEARS = "year"

    # Temperature
    CELSIUS = "degC"
    FAHRENHEIT = "degF"
    KELVIN = "K"

    # Dimensionless
    PERCENT = "percent"
    UNITLESS = "dimensionless"

    # Forestry-specific compound units
    BIAS_CORRECTION_FACTOR = "dimensionless"  # For log bias correction
    FORM_FACTOR = "dimensionless"  # Volume ratio
    CROWN_RATIO = "dimensionless"  # Crown length / total height

    @staticmethod
    def get_unit(unit_str: str) -> pint.Quantity:
        """Get or create a unit Quantity from a string.

        Args:
            unit_str: Unit string (e.g., "meter", "centimeter", "hectare")

        Returns:
            Pint Quantity representing the unit
        """
        return _get_unit(unit_str)


# Create singleton instance for convenience
units = Units()


def format_unit(unit_str: str) -> str:
    """Format a unit string in a consistent way.

    Args:
        unit_str: Input unit string

    Returns:
        Formatted unit string

    Example:
        >>> format_unit("m^2")
        'm²'
        >>> format_unit("m^3")
        'm³'
    """
    # Use Pint's pretty formatting
    return str(_get_unit(unit_str).units)


def parse_unit_string(unit_str: str) -> str:
    """Parse and validate a unit string.

    Args:
        unit_str: Unit string to parse

    Returns:
        Validated unit string

    Raises:
        ValueError: If unit string is invalid

    Example:
        >>> parse_unit_string("m^2")
        'm^2'
        >>> parse_unit_string("invalid_unit")
        Traceback (most recent call last):
            ...
        ValueError: Invalid unit: invalid_unit
    """
    try:
        _get_unit(unit_str)
        return unit_str
    except (pint.UndefinedUnitError, ValueError) as e:
        raise ValueError(f"Invalid unit: {unit_str}") from e


def convert_dataframe_units(
    df: DataFrame,
    column_unit_map: dict[str, str],
    target_units: dict[str, str],
) -> DataFrame:
    """Convert units in a DataFrame.

    Args:
        df: Input DataFrame
        column_unit_map: Mapping of column names to current units
        target_units: Mapping of column names to target units

    Returns:
        DataFrame with converted units

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"diameter": [25, 30, 35], "height": [15, 18, 22]})
        >>> column_units = {"diameter": "cm", "height": "m"}
        >>> target_units = {"diameter": "in", "height": "ft"}
        >>> convert_dataframe_units(df, column_units, target_units)
           diameter  height
        0   9.84252  49.2126
        1  11.81102  59.0551
        2  13.77953  72.1785
    """
    df_converted = df.copy()

    for column, target_unit in target_units.items():
        if column in df_converted.columns:
            current_unit = column_unit_map.get(column)
            if current_unit:
                df_converted[column] = df_converted[column].apply(
                    lambda x: (
                        convert_units(x, current_unit, target_unit)
                        if not isinstance(x, pint.Quantity)
                        or str(x.units) != target_unit
                        else float(x.to(target_unit))
                    )
                )

    return df_converted


def calculate_density(
    mass: Union[float, int, ndarray, Series, pint.Quantity],
    volume: Union[float, int, ndarray, Series, pint.Quantity],
    mass_unit: str = "kg",
    volume_unit: str = "m^3",
) -> pint.Quantity:
    """Calculate density from mass and volume.

    Args:
        mass: Mass value(s)
        volume: Volume value(s)
        mass_unit: Mass unit string
        volume_unit: Volume unit string

    Returns:
        Density value(s) in kg/m^3

    Example:
        >>> calculate_density(100, 0.5)
        200.0 * kilogram / meter ** 3
        >>> calculate_density(set_units(100, "kg"), set_units(0.5, "m^3"))
        200.0 * kilogram / meter ** 3
    """
    mass_q = set_units(mass, mass_unit)
    volume_q = set_units(volume, volume_unit)
    density = mass_q / volume_q
    return density.to_base_units()


def calculate_specificGravity(
    density: Union[float, int, ndarray, Series, pint.Quantity],
    reference_density: float = 1000,  # Water at 4°C in kg/m^3
    density_unit: str = "kg/m^3",
) -> Union[float, ndarray]:
    """Calculate specific gravity (dimensionless density relative to water).

    Args:
        density: Density value(s)
        reference_density: Reference density (water at 4°C)
        density_unit: Density unit string

    Returns:
        Specific gravity (dimensionless)

    Example:
        >>> calculate_specificGravity(800)
        0.8
        >>> calculate_specificGravity(set_units(800, "kg/m^3"))
        0.8
    """
    density_q = set_units(density, density_unit)
    return density_q.magnitude / reference_density
