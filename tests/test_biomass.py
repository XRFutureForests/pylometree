"""Tests for biomass allometric model functions."""

import numpy as np
import pytest

from pylometree.models.biomass import (
    bgb_from_agb,
    chave2014,
    log_correction_factor,
    m1_dbh,
    m2_height,
    m3_d2h,
    m4_dbh_height,
    m5_rho_d2h,
    musa_agb,
    musa_total_biomass_nsur,
)


class TestChave2014:
    def test_known_value(self):
        # Chave et al. paper example: DBH=20 cm, H=18 m, rho=0.55
        agb = float(chave2014(20.0, 18.0, 0.55))
        assert 100 < agb < 600  # kg; rough sanity range

    def test_vectorised(self):
        dbh = np.array([10.0, 20.0, 30.0])
        h = np.array([10.0, 20.0, 25.0])
        rho = np.array([0.55, 0.55, 0.55])
        agb = chave2014(dbh, h, rho)
        assert agb.shape == (3,)
        assert np.all(np.diff(agb) > 0)  # increasing with size

    def test_positive(self):
        assert float(chave2014(15.0, 15.0, 0.50)) > 0


class TestGenericForms:
    def test_m1_dbh_monotone(self):
        dbh = np.array([5.0, 10.0, 20.0, 40.0])
        agb = m1_dbh(dbh, a=0.1, b=2.3)
        assert np.all(np.diff(agb) > 0)

    def test_m3_d2h_shape(self):
        agb = m3_d2h([10, 20], [15, 20], a=0.05, b=0.9)
        assert len(agb) == 2

    def test_m4_positional(self):
        agb = float(m4_dbh_height(20, 18, a=0.05, b=2.0, c=0.5))
        assert agb > 0

    def test_m5_rho_d2h(self):
        agb = m5_rho_d2h(20.0, 18.0, 0.55, a=0.0673, b=0.976)
        agb_chave = chave2014(20.0, 18.0, 0.55)
        # Should be numerically identical
        assert abs(float(agb) - float(agb_chave)) < 1e-6


class TestCorrectionFactor:
    def test_zero_residuals(self):
        cf = log_correction_factor(np.zeros(10))
        assert abs(cf - 1.0) < 1e-10

    def test_positive_residuals(self):
        cf = log_correction_factor([0.1, -0.1, 0.2, -0.05])
        assert cf > 1.0


class TestMusa:
    def test_agb_positive(self):
        assert float(musa_agb(5.0, 3.0)) > 0

    def test_nsur_positive(self):
        assert float(musa_total_biomass_nsur(5.0)) > 0

    def test_nsur_monotone(self):
        dbh = np.array([2.0, 5.0, 10.0])
        agb = musa_total_biomass_nsur(dbh)
        assert np.all(np.diff(agb) > 0)


class TestBGB:
    def test_bgb_proportional(self):
        agb = np.array([100.0, 200.0, 300.0])
        root_shoot = 0.235
        bgb = bgb_from_agb(agb, root_shoot)
        np.testing.assert_allclose(bgb, agb * root_shoot)
