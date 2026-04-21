"""Tests for volume and age-from-height models (models/volume.py)."""

from __future__ import annotations

import math

import numpy as np
import pytest

from pylometree.models import volume


class TestStemVolume:
    def test_cylinder_formula(self):
        # DBH 40 cm → 0.4 m, H 20 m → V = π/4 · 0.16 · 20
        v = volume.volume_cylinder(dsob=40.0, hst=20.0)
        expected = math.pi / 4.0 * 0.16 * 20.0
        assert v == pytest.approx(expected)

    def test_form_factor_scales_cylinder(self):
        cyl = volume.volume_cylinder(dsob=30.0, hst=25.0)
        ff = volume.volume_form_factor(dsob=30.0, hst=25.0, form_factor=0.5)
        assert ff == pytest.approx(cyl * 0.5)

    def test_form_factor_default(self):
        v = volume.volume_form_factor(dsob=30.0, hst=25.0)
        # Default f=0.5
        assert v == pytest.approx(volume.volume_cylinder(30.0, 25.0) * 0.5)

    def test_power_law(self):
        v = volume.volume_power_law(dsob=20.0, hst=15.0, a=0.0001, b=2.0, c=1.0)
        assert v == pytest.approx(0.0001 * 400.0 * 15.0)

    def test_array_input(self):
        v = volume.volume_cylinder(dsob=[20.0, 30.0], hst=[10.0, 20.0])
        assert v.shape == (2,)
        assert v[1] > v[0]


class TestVolumeToAgb:
    def test_density_expansion(self):
        agb = volume.volume_to_agb(volume_m3=1.0, wood_density=500.0, bef=1.5)
        assert agb == pytest.approx(750.0)

    def test_default_bef_one(self):
        agb = volume.volume_to_agb(volume_m3=2.0, wood_density=600.0)
        assert agb == pytest.approx(1200.0)


class TestConoidFrustum:
    def test_equal_diameters_reduce_to_cylinder(self):
        # D_base = D_top → reduces to cylinder
        v_frust = volume.conoid_frustum_volume(d_base=20.0, d_top=20.0, length=10.0)
        v_cyl = math.pi * 10.0 / 12.0 * (0.04 + 0.04 + 0.04)
        assert v_frust == pytest.approx(v_cyl)
        # Also equal to π/4 · d² · L
        assert v_frust == pytest.approx(math.pi / 4.0 * 0.04 * 10.0)

    def test_zero_top_cone(self):
        # D_top=0 → V = π·L/12 · D_base²
        v = volume.conoid_frustum_volume(d_base=20.0, d_top=0.0, length=10.0)
        assert v == pytest.approx(math.pi * 10.0 / 12.0 * 0.04)

    def test_taper_less_than_cylinder(self):
        v_tap = volume.conoid_frustum_volume(d_base=30.0, d_top=10.0, length=10.0)
        v_cyl = math.pi / 4.0 * 0.09 * 10.0  # cylinder at base diameter
        assert v_tap < v_cyl


class TestChapmanRichards:
    def test_height_at_age_zero(self):
        h = volume.height_from_age_cr(age=0.0, hmax=40.0, k=0.03, c=1.2)
        assert h == pytest.approx(0.0)

    def test_height_approaches_asymptote(self):
        h = volume.height_from_age_cr(age=500.0, hmax=40.0, k=0.03, c=1.2)
        assert h == pytest.approx(40.0, rel=1e-3)

    def test_height_monotonic_in_age(self):
        ages = np.array([10.0, 30.0, 60.0, 100.0])
        h = volume.height_from_age_cr(age=ages, hmax=40.0, k=0.03, c=1.2)
        assert np.all(np.diff(h) > 0)

    def test_inverse_roundtrip(self):
        params = dict(hmax=40.0, k=0.03, c=1.2)
        age_in = 50.0
        h = volume.height_from_age_cr(age=age_in, **params)
        age_out = volume.age_from_height_cr(hst=h, **params)
        assert age_out == pytest.approx(age_in)

    def test_si_correction_shifts_height(self):
        h0 = volume.height_from_age_cr(age=50.0, hmax=40.0, k=0.03, c=1.2)
        h_si = volume.height_from_age_cr(
            age=50.0, hmax=40.0, k=0.03, c=1.2, si_correction=2.0
        )
        assert h_si == pytest.approx(h0 + 2.0)

    def test_age_from_height_returns_nan_above_asymptote(self):
        # H >= hmax → ratio >= 1 → nan
        age = volume.age_from_height_cr(hst=45.0, hmax=40.0, k=0.03, c=1.2)
        assert np.isnan(age)


class TestSpeciesParams:
    def test_all_five_species_present(self):
        expected = {
            "Picea abies",
            "Pinus sylvestris",
            "Fagus sylvatica",
            "Quercus petraea",
            "Quercus robur",
        }
        assert set(volume.CR_SPECIES_PARAMS.keys()) == expected

    def test_params_complete(self):
        for sp, params in volume.CR_SPECIES_PARAMS.items():
            assert {"hmax", "k", "c"} <= set(params.keys()), sp
            assert params["hmax"] > 0
            assert params["k"] > 0
            assert params["c"] > 0
