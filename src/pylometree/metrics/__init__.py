"""Model evaluation metrics.

Implements both classical regression metrics and the forestry-specific
accuracy measures used in Burt et al. (treeallom):

Classical
---------
R² (coefficient of determination)
RMSE (root mean squared error)
MAE  (mean absolute error)
BIAS (mean error = mean residual)
AIC / AICc (Akaike information criteria)
BIC  (Bayesian information criterion)

Forestry-specific (Burt / treeallom convention)
------------------------------------------------
MSA  – Median Symmetric Accuracy  = 100·(exp(median|ln(ŷ/y)|) − 1)
SSPB – Signed Symmetric Percent Bias = 100·sign(median(ln(ŷ/y)))
       × (exp(|median(ln(ŷ/y))|) − 1)

References
----------
- Smith (1993) / Sprugel (1983): log bias correction
- Burt & Disney (treeallom): MSA, SSPB definitions
- Burnham & Anderson (2002): AIC, AICc
"""

from __future__ import annotations

import math
from typing import Optional

import numpy as np
from numpy.typing import ArrayLike


def _arr(x: ArrayLike) -> np.ndarray:
    return np.asarray(x, dtype=float)


# ---------------------------------------------------------------------------
# Classical metrics
# ---------------------------------------------------------------------------


def r2(y_true: ArrayLike, y_pred: ArrayLike) -> float:
    """Coefficient of determination (R²)."""
    yt, yp = _arr(y_true), _arr(y_pred)
    ss_res = float(np.sum((yt - yp) ** 2))
    ss_tot = float(np.sum((yt - np.mean(yt)) ** 2))
    if ss_tot == 0.0:
        return float("nan")
    return 1.0 - ss_res / ss_tot


def rmse(y_true: ArrayLike, y_pred: ArrayLike) -> float:
    """Root Mean Squared Error."""
    yt, yp = _arr(y_true), _arr(y_pred)
    return float(np.sqrt(np.mean((yt - yp) ** 2)))


def mae(y_true: ArrayLike, y_pred: ArrayLike) -> float:
    """Mean Absolute Error."""
    yt, yp = _arr(y_true), _arr(y_pred)
    return float(np.mean(np.abs(yt - yp)))


def bias(y_true: ArrayLike, y_pred: ArrayLike) -> float:
    """Mean error (systematic bias): positive = over-prediction."""
    yt, yp = _arr(y_true), _arr(y_pred)
    return float(np.mean(yp - yt))


def relative_rmse(y_true: ArrayLike, y_pred: ArrayLike) -> float:
    """Relative RMSE as a percentage of the observed mean."""
    yt = _arr(y_true)
    mean_obs = float(np.mean(yt))
    if mean_obs == 0.0:
        return float("nan")
    return rmse(yt, y_pred) / mean_obs * 100.0


# ---------------------------------------------------------------------------
# Information criteria
# ---------------------------------------------------------------------------


def aic(y_true: ArrayLike, y_pred: ArrayLike, n_params: int) -> float:
    """Akaike Information Criterion (assuming Gaussian errors, OLS).

    AIC = n · ln(RSS/n) + 2k

    Parameters
    ----------
    n_params : int
        Number of free parameters in the model (not including σ²).
    """
    yt, yp = _arr(y_true), _arr(y_pred)
    n = len(yt)
    if n == 0:
        return float("nan")
    rss = float(np.sum((yt - yp) ** 2))
    if rss == 0.0:
        return float("-inf")
    return n * math.log(rss / n) + 2.0 * n_params


def aicc(y_true: ArrayLike, y_pred: ArrayLike, n_params: int) -> float:
    """Corrected AIC for small samples.

    AICc = AIC + 2k(k+1)/(n−k−1)
    """
    yt = _arr(y_true)
    n = len(yt)
    k = n_params
    a = aic(yt, y_pred, k)
    denom = n - k - 1
    if denom <= 0:
        return float("nan")
    return a + 2.0 * k * (k + 1) / denom


def bic(y_true: ArrayLike, y_pred: ArrayLike, n_params: int) -> float:
    """Bayesian Information Criterion.

    BIC = n · ln(RSS/n) + k · ln(n)
    """
    yt, yp = _arr(y_true), _arr(y_pred)
    n = len(yt)
    rss = float(np.sum((yt - yp) ** 2))
    if rss <= 0 or n == 0:
        return float("nan")
    return n * math.log(rss / n) + n_params * math.log(n)


def aic_weights(aic_values: list[float]) -> np.ndarray:
    """Compute AIC weights (Akaike weights) for a set of candidate models.

    w_i = exp(−0.5·Δ_i) / Σ exp(−0.5·Δ_j)

    where Δ_i = AIC_i − min(AIC).
    """
    a = np.asarray(aic_values, dtype=float)
    delta = a - np.nanmin(a)
    unnorm = np.exp(-0.5 * delta)
    return unnorm / np.nansum(unnorm)


# ---------------------------------------------------------------------------
# Forestry-specific accuracy metrics (Burt / treeallom)
# ---------------------------------------------------------------------------


def msa(y_true: ArrayLike, y_pred: ArrayLike) -> float:
    """Median Symmetric Accuracy (%).

    MSA = 100 · (exp(median(|ln(ŷ/y)|)) − 1)

    Interpretation: the typical relative error, symmetric on the
    multiplicative scale.  Lower is better.
    """
    yt, yp = _arr(y_true), _arr(y_pred)
    with np.errstate(divide="ignore", invalid="ignore"):
        log_ratio = np.log(yp / yt)
    valid = np.isfinite(log_ratio)
    if not np.any(valid):
        return float("nan")
    return float(100.0 * (np.exp(np.median(np.abs(log_ratio[valid]))) - 1.0))


def sspb(y_true: ArrayLike, y_pred: ArrayLike) -> float:
    """Signed Symmetric Percent Bias (%).

    SSPB = 100 · sign(median(ln(ŷ/y))) · (exp(|median(ln(ŷ/y))|) − 1)

    Positive = over-prediction; negative = under-prediction.
    """
    yt, yp = _arr(y_true), _arr(y_pred)
    with np.errstate(divide="ignore", invalid="ignore"):
        log_ratio = np.log(yp / yt)
    valid = np.isfinite(log_ratio)
    if not np.any(valid):
        return float("nan")
    med = float(np.median(log_ratio[valid]))
    return float(100.0 * np.sign(med) * (np.exp(abs(med)) - 1.0))


# ---------------------------------------------------------------------------
# Summary report
# ---------------------------------------------------------------------------


def model_report(
    y_true: ArrayLike,
    y_pred: ArrayLike,
    n_params: int,
    model_name: str = "",
) -> dict[str, float]:
    """Return a dictionary of all evaluation metrics for a model fit.

    Parameters
    ----------
    y_true : array-like
        Observed values.
    y_pred : array-like
        Model-predicted values.
    n_params : int
        Number of estimated parameters (used in AIC/AICc/BIC).
    model_name : str
        Optional label included in the returned dict.
    """
    return {
        "model": model_name,
        "n": len(_arr(y_true)),
        "r2": r2(y_true, y_pred),
        "rmse": rmse(y_true, y_pred),
        "rrmse_pct": relative_rmse(y_true, y_pred),
        "mae": mae(y_true, y_pred),
        "bias": bias(y_true, y_pred),
        "msa_pct": msa(y_true, y_pred),
        "sspb_pct": sspb(y_true, y_pred),
        "aic": aic(y_true, y_pred, n_params),
        "aicc": aicc(y_true, y_pred, n_params),
        "bic": bic(y_true, y_pred, n_params),
    }
