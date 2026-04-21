"""Tests for crown-based allometric models (models/crown.py)."""

from __future__ import annotations

import math

import numpy as np
import pytest

from pylometree.models import crown


class TestAgbFromCrown:
    def test_scalar_power_law(self):
        # AGB = a * H^b * CA^c
        agb = crown.agb_from_crown(hst=20.0, crown_area=50.0, a=0.1, b=1.0, c=1.0)
        assert agb == pytest.approx(0.1 * 20.0 * 50.0)

    def test_array_inputs_broadcast(self):
        h = np.array([10.0, 20.0])
        ca = np.array([40.0, 80.0])
        out = crown.agb_from_crown(h, ca, a=1.0, b=1.0, c=1.0)
        assert out.shape == (2,)
        np.testing.assert_allclose(out, [400.0, 1600.0])

    def test_jucker2017_reference_value(self):
        # For H=20, CA=50: AGB = 0.016 * 20^0.940 * 50^0.932
        agb = crown.jucker2017_agb(hst=20.0, crown_area=50.0)
        expected = 0.016 * 20.0**0.940 * 50.0**0.932
        assert agb == pytest.approx(expected)

    def test_jucker2017_monotonic_in_height(self):
        out = crown.jucker2017_agb(hst=[5.0, 15.0, 30.0], crown_area=20.0)
        assert out[0] < out[1] < out[2]


class TestDbhFromCrown:
    def test_dbh_from_crown_height_power_law(self):
        dbh = crown.dbh_from_crown_height(hst=15.0, a=2.0, b=0.8)
        assert dbh == pytest.approx(2.0 * 15.0**0.8)

    def test_dbh_from_height_cd(self):
        dbh = crown.dbh_from_height_cd(hst=10.0, crown_diam=4.0, a=1.0, b=1.0, c=1.0)
        assert dbh == pytest.approx(40.0)

    def test_dbh_scales_with_height(self):
        small = crown.dbh_from_crown_height(hst=5.0, a=2.0, b=0.8)
        big = crown.dbh_from_crown_height(hst=30.0, a=2.0, b=0.8)
        assert big > small


class TestCrownGeometry:
    def test_area_from_diameter_matches_circle(self):
        ca = crown.crown_area_from_diameter(4.0)
        assert ca == pytest.approx(math.pi * 4.0)  # π·(d/2)² = π·4

    def test_diameter_from_area_inverts(self):
        ca = 28.274333882308138  # π·3² (radius 3, diameter 6)
        cd = crown.crown_diameter_from_area(ca)
        assert cd == pytest.approx(6.0)

    def test_roundtrip_area_diameter(self):
        d = np.array([2.0, 5.0, 10.0])
        a = crown.crown_area_from_diameter(d)
        d2 = crown.crown_diameter_from_area(a)
        np.testing.assert_allclose(d2, d)


class TestCrownRatio:
    def test_basic(self):
        assert crown.crown_ratio(crown_height=8.0, total_height=20.0) == pytest.approx(
            0.4
        )

    def test_full_crown(self):
        assert crown.crown_ratio(crown_height=10.0, total_height=10.0) == 1.0


class TestCrownCatalogue:
    def test_registered_models_callable(self):
        for name, meta in crown.CROWN_MODELS.items():
            fn = meta["fn"]
            params = dict(zip(meta["params"], meta["p0"]))
            # Synthesise covariate values
            covars = {
                "hst": 15.0,
                "crown_area": 40.0,
                "crown_diam": 5.0,
            }
            kwargs = {k: covars[k] for k in meta["covariates"]}
            out = fn(**kwargs, **params)
            assert np.isfinite(out), f"{name} returned non-finite value"
            assert out > 0
