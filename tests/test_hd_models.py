"""Tests for H-D allometric model functions."""

import numpy as np
import pytest

from pylometree.models.hd import (
    HD_MODELS,
    chapman_richards,
    exponential_3p,
    gompertz,
    hyperbolic,
    korf,
    log_linear,
    log_time_growth,
    logarithmic,
    michaelis_menten,
    power_law,
    von_bertalanffy,
    weibull_4p,
)

DBH = np.array([5.0, 10.0, 20.0, 40.0])


class TestMonotonicity:
    """All H-D models should be monotonically increasing for increasing DBH."""

    @pytest.mark.parametrize("name,entry", HD_MODELS.items())
    def test_monotone_increasing(self, name, entry):
        fn = entry["fn"]
        p0 = entry["p0"]
        h = fn(DBH, *p0)
        diffs = np.diff(h)
        assert np.all(
            diffs >= 0
        ), f"{name}: not monotonically increasing with DBH={DBH}, p0={p0}, h={h}"


class TestOutputShape:
    """Model outputs must match input shape."""

    @pytest.mark.parametrize("name,entry", HD_MODELS.items())
    def test_output_shape(self, name, entry):
        fn = entry["fn"]
        p0 = entry["p0"]
        h = fn(DBH, *p0)
        assert h.shape == DBH.shape

    @pytest.mark.parametrize("name,entry", HD_MODELS.items())
    def test_scalar_input(self, name, entry):
        fn = entry["fn"]
        p0 = entry["p0"]
        h = fn(20.0, *p0)
        assert np.isscalar(h) or h.ndim == 0


class TestSpecific:
    def test_power_law_known(self):
        h = power_law(10.0, 1.0, 1.0)
        assert abs(h - 10.0) < 1e-10

    def test_michaelis_menten_asymptote(self):
        """Very large DBH → h approaches a."""
        h = michaelis_menten(1e6, a=35.0, b=5.0)
        assert abs(float(h) - 35.0) < 0.01

    def test_chapman_richards_asymptote(self):
        h = chapman_richards(1e5, a=30.0, b=0.05, c=1.0)
        assert abs(float(h) - 30.0) < 0.01

    def test_log_time_growth_at_1yr(self):
        # ln(1) = 0 → H(1) = H1
        h = log_time_growth(1.0, h1=5.0, h_rate=2.0)
        assert abs(float(h) - 5.0) < 1e-10

    def test_all_positive_output(self):
        for name, entry in HD_MODELS.items():
            h = entry["fn"](DBH, *entry["p0"])
            assert np.all(h >= 0), f"{name} produced negative heights"
