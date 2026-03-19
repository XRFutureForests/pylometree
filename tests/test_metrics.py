"""Tests for model evaluation metrics."""

import math

import numpy as np
import pytest

from pylometree.metrics import (
    aic,
    aic_weights,
    aicc,
    bias,
    bic,
    mae,
    model_report,
    msa,
    r2,
    relative_rmse,
    rmse,
    sspb,
)

Y_TRUE = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
Y_PERFECT = Y_TRUE.copy()
Y_OVER = Y_TRUE + 5.0  # systematic over-prediction by 5
Y_RANDOM = np.array([12.0, 18.0, 33.0, 38.0, 52.0])


class TestR2:
    def test_perfect(self):
        assert abs(r2(Y_TRUE, Y_PERFECT) - 1.0) < 1e-10

    def test_range(self):
        v = r2(Y_TRUE, Y_RANDOM)
        assert v <= 1.0

    def test_constant_prediction(self):
        # Predict the mean – R² should be 0
        mean_pred = np.full_like(Y_TRUE, Y_TRUE.mean())
        assert abs(r2(Y_TRUE, mean_pred)) < 1e-10


class TestRMSE:
    def test_perfect(self):
        assert rmse(Y_TRUE, Y_PERFECT) == 0.0

    def test_value(self):
        assert abs(rmse(Y_TRUE, Y_OVER) - 5.0) < 1e-10


class TestBias:
    def test_zero_bias(self):
        assert abs(bias(Y_TRUE, Y_PERFECT)) < 1e-10

    def test_positive_bias(self):
        assert bias(Y_TRUE, Y_OVER) > 0

    def test_magnitude(self):
        assert abs(bias(Y_TRUE, Y_OVER) - 5.0) < 1e-10


class TestAIC:
    def test_lower_for_better_fit(self):
        # Fewer residuals → lower AIC (keeping k constant)
        a_perfect = aic(Y_TRUE, Y_PERFECT, 2)
        a_bad = aic(Y_TRUE, Y_OVER, 2)
        assert a_perfect < a_bad

    def test_aicc_ge_aic(self):
        # AICc ≥ AIC for small n
        a = aic(Y_TRUE, Y_RANDOM, 2)
        ac = aicc(Y_TRUE, Y_RANDOM, 2)
        assert ac >= a


class TestAICWeights:
    def test_sum_to_one(self):
        vals = [100.0, 102.0, 105.0, 110.0]
        w = aic_weights(vals)
        assert abs(float(np.sum(w)) - 1.0) < 1e-10

    def test_best_has_highest_weight(self):
        vals = [100.0, 102.0, 108.0]
        w = aic_weights(vals)
        assert np.argmax(w) == 0


class TestMSA:
    def test_perfect(self):
        # ln(y/y)=0 for all → MSA = 0%
        assert abs(msa(Y_TRUE, Y_PERFECT)) < 1e-10

    def test_positive(self):
        assert msa(Y_TRUE, Y_RANDOM) >= 0


class TestSSPB:
    def test_perfect_zero(self):
        assert abs(sspb(Y_TRUE, Y_PERFECT)) < 1e-10

    def test_positive_for_overprediction(self):
        # Systematic over-prediction → positive SSPB
        assert sspb(Y_TRUE, Y_OVER) > 0

    def test_negative_for_underprediction(self):
        assert sspb(Y_TRUE, Y_TRUE - 5.0) < 0


class TestModelReport:
    def test_keys_present(self):
        report = model_report(Y_TRUE, Y_RANDOM, n_params=2, model_name="test")
        expected = [
            "r2",
            "rmse",
            "rrmse_pct",
            "mae",
            "bias",
            "msa_pct",
            "sspb_pct",
            "aic",
            "aicc",
            "bic",
            "n",
            "model",
        ]
        for key in expected:
            assert key in report, f"Missing key: {key}"
