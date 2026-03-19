"""Tests for fitting utilities and model selection."""

import numpy as np
import pytest

from pylometree.fitting import FitResult, bootstrap_ci, fit_model, select_model
from pylometree.models.hd import HD_MODELS, chapman_richards, power_law

# Synthetic data: Chapman-Richards with known params + noise
RNG = np.random.default_rng(42)
TRUE_PARAMS = {"a": 28.0, "b": 0.06, "c": 1.2}
DBH = np.linspace(5, 60, 40)
H_TRUE = chapman_richards(DBH, **TRUE_PARAMS)
H_OBS = H_TRUE + RNG.normal(0, 0.5, size=len(DBH))


class TestFitModel:
    def test_recovers_params(self):
        res = fit_model(
            fn=chapman_richards,
            x=DBH,
            y=H_OBS,
            param_names=["a", "b", "c"],
            p0=[25.0, 0.05, 1.0],
            bounds=([0, 0, 0], [np.inf, np.inf, 10]),
            model_name="cr_test",
        )
        assert res.converged
        assert abs(res.params["a"] - TRUE_PARAMS["a"]) < 5.0
        assert res.metrics["r2"] > 0.95

    def test_returns_fit_result(self):
        res = fit_model(
            fn=power_law,
            x=DBH,
            y=H_OBS,
            param_names=["a", "b"],
            p0=[1.0, 0.5],
        )
        assert isinstance(res, FitResult)
        assert "r2" in res.metrics

    def test_repr(self):
        res = fit_model(
            fn=power_law,
            x=DBH,
            y=H_OBS,
            param_names=["a", "b"],
            p0=[1.0, 0.5],
            model_name="pw",
        )
        assert "pw" in repr(res)


class TestSelectModel:
    def test_returns_tuple(self):
        best_name, best_res, all_res = select_model(
            HD_MODELS, x=DBH, y=H_OBS, criterion="aicc"
        )
        assert isinstance(best_name, str)
        assert isinstance(best_res, FitResult)
        assert len(all_res) == len(HD_MODELS)

    def test_best_has_lowest_aicc(self):
        best_name, best_res, all_res = select_model(
            HD_MODELS, x=DBH, y=H_OBS, criterion="aicc"
        )
        best_val = best_res.metrics["aicc"]
        for r in all_res:
            v = r.metrics["aicc"]
            if np.isfinite(v):
                assert best_val <= v + 1e-6


class TestBootstrapCI:
    def test_ci_bounds(self):
        lo, hi = bootstrap_ci(
            fn=power_law,
            x=DBH,
            y=H_OBS,
            param_names=["a", "b"],
            p0=[1.0, 0.5],
            n_boot=200,
            random_state=0,
        )
        assert lo["a"] < hi["a"]
        assert lo["b"] < hi["b"]

    def test_finite_bounds(self):
        lo, hi = bootstrap_ci(
            fn=power_law,
            x=DBH,
            y=H_OBS,
            param_names=["a", "b"],
            p0=[1.0, 0.5],
            n_boot=100,
            random_state=1,
        )
        for k in ["a", "b"]:
            assert np.isfinite(lo[k])
            assert np.isfinite(hi[k])
