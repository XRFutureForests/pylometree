"""Tests for units module."""

import numpy as np
import pandas as pd
import pint
import pytest

from pylometree.units import (
    Units,
    convert_dataframe_units,
    convert_units,
    set_units,
)


class TestUnits:
    """Test Units class."""

    def test_predefined_units(self):
        """Test that predefined units are accessible."""
        assert Units.METER == "meter"
        assert Units.CENTIMETER == "centimeter"
        assert Units.HECTARE == "hectare"
        assert Units.KILOGRAM == "kilogram"
        assert Units.GRAM == "gram"
        assert Units.YEAR == "year"
        assert Units.SQUARE_METER == "square_meter"
        assert Units.CUBIC_METER == "cubic_meter"

    def test_unit_cache(self):
        """Test that unit cache works."""
        unit1 = Units.get_unit("meter")
        unit2 = Units.get_unit("meter")
        assert unit1 == unit2


class TestSetUnits:
    """Test set_units function."""

    def test_set_units_scalar(self):
        """Test setting units on scalar value."""
        value = set_units(10.5, "meter")
        assert value.magnitude == 10.5
        assert str(value.units) == "meter"

    def test_set_units_array(self):
        """Test setting units on numpy array."""
        arr = np.array([1, 2, 3])
        value = set_units(arr, "meter")
        assert np.array_equal(value.magnitude, arr)
        assert str(value.units) == "meter"

    def test_set_units_without_unit(self):
        """Test setting units without unit string."""
        value = set_units(10.5)
        assert value.magnitude == 10.5
        assert str(value.units) == "dimensionless"


class TestConvertUnits:
    """Test convert_units function."""

    def test_convert_length(self):
        """Test converting between length units."""
        result = convert_units(100, "centimeter", "meter")
        assert result == 1.0

    def test_convert_area(self):
        """Test converting between area units."""
        result = convert_units(1, "hectare", "m^2")
        assert result == 10000.0

    def test_convert_mass(self):
        """Test converting between mass units."""
        result = convert_units(1000, "gram", "kilogram")
        assert result == 1.0

    def test_convert_incompatible_raises(self):
        """Test that converting incompatible units raises error."""
        with pytest.raises(pint.DimensionalityError):
            convert_units(100, "meter", "kilogram")

    def test_convert_with_quantity(self):
        """Test converting a quantity with units."""
        value = set_units(100, "centimeter")
        result = convert_units(value, to_unit="meter")
        assert result == 1.0


class TestConvertDataFrameUnits:
    """Test convert_dataframe_units function."""

    def test_convert_single_column(self):
        """Test converting a single column."""
        df = pd.DataFrame({"dbh": [10, 20, 30]})
        result = convert_dataframe_units(df, {"dbh": "centimeter"}, {"dbh": "meter"})
        assert np.array_equal(result["dbh"].values, [0.1, 0.2, 0.3])

    def test_convert_multiple_columns(self):
        """Test converting multiple columns."""
        df = pd.DataFrame({"dbh": [10, 20, 30], "height": [100, 200, 300]})
        result = convert_dataframe_units(
            df,
            {"dbh": "centimeter", "height": "centimeter"},
            {"dbh": "meter", "height": "meter"},
        )
        assert np.array_equal(result["dbh"].values, [0.1, 0.2, 0.3])
        assert np.array_equal(result["height"].values, [1.0, 2.0, 3.0])

    def test_convert_with_quantity_columns(self):
        """Test converting columns that already have units."""
        df = pd.DataFrame(
            {
                "dbh": [
                    set_units(10, "centimeter").magnitude,
                    set_units(20, "centimeter").magnitude,
                    set_units(30, "centimeter").magnitude,
                ],
                "height": [
                    set_units(100, "centimeter").magnitude,
                    set_units(200, "centimeter").magnitude,
                    set_units(300, "centimeter").magnitude,
                ],
            }
        )
        result = convert_dataframe_units(
            df,
            {"dbh": "centimeter", "height": "centimeter"},
            {"dbh": "meter", "height": "meter"},
        )
        assert np.array_equal(result["dbh"].values, [0.1, 0.2, 0.3])
        assert np.array_equal(result["height"].values, [1.0, 2.0, 3.0])

    def test_convert_incompatible_raises(self):
        """Test that converting incompatible units raises error."""
        df = pd.DataFrame({"dbh": [10, 20, 30]})
        with pytest.raises(pint.DimensionalityError):
            convert_dataframe_units(df, {"dbh": "meter"}, {"dbh": "kilogram"})
