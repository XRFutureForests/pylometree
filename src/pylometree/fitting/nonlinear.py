"""Non-linear curve fitting utilities.

Wraps ``scipy.optimize.curve_fit`` with:
- Automatic initial parameter selection from model catalogue
- AIC / AICc model comparison
- Optional bootstrap confidence intervals (Burt / treeallom approach)
- Per-species model selection (allometree approach)

All public functions return ``FitResult`` dataclasses for easy inspection.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from typing import Callable, Optional

import numpy as np
from numpy.typing import ArrayLike
from scipy.optimize import curve_fit

from pylometree import metrics as met

# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------


@dataclass
class FitResult:
    """Outcome of a single non-linear curve fit.

    Attributes
    ----------
    model_name : str
        Human-readable model label.
    params : dict[str, float]
        Fitted parameter values keyed by name.
    param_se : dict[str, float]
        Standard errors (square root of diagonal of covariance matrix).
    covariance : np.ndarray
        Full covariance matrix from ``curve_fit``.
    metrics : dict[str, float]
        Evaluation metrics (R², RMSE, AIC, …) from ``metrics.model_report``.
    converged : bool
        Whether optimisation converged.
    ci_lower : dict[str, float]
        Bootstrap lower CI bounds (empty if bootstrap not run).
    ci_upper : dict[str, float]
        Bootstrap upper CI bounds (empty if bootstrap not run).
    """

    model_name: str
    params: dict[str, float]
    param_se: dict[str, float]
    covariance: np.ndarray
    metrics: dict[str, float]
    converged: bool = True
    ci_lower: dict[str, float] = field(default_factory=dict)
    ci_upper: dict[str, float] = field(default_factory=dict)

    def predict(self, *args) -> np.ndarray:
        """Re-run the stored function is not cached; use the fn from catalogue."""
        raise NotImplementedError(
            "Use the original model function with self.params to predict."
        )

    def __repr__(self) -> str:
        r2v = self.metrics.get("r2", float("nan"))
        return (
            f"FitResult({self.model_name!r}, "
            f"R²={r2v:.3f}, converged={self.converged})"
        )


# ---------------------------------------------------------------------------
# Core fitting function
# ---------------------------------------------------------------------------


def fit_model(
    fn: Callable,
    x: ArrayLike,
    y: ArrayLike,
    param_names: list[str],
    p0: Optional[list[float]] = None,
    bounds: tuple = (-np.inf, np.inf),
    model_name: str = "model",
    max_nfev: int = 5000,
) -> FitResult:
    """Fit a single allometric model using non-linear least squares.

    Parameters
    ----------
    fn : callable
        Model function.  Must accept positional covariate array(s) (from *x*)
        followed by free parameters as positional arguments.
    x : array-like or tuple of array-like
        Covariate(s).  Pass a tuple for multi-covariate functions.
    y : array-like
        Response variable (observed values).
    param_names : list[str]
        Names of free parameters in the order ``fn`` accepts them.
    p0 : list[float], optional
        Initial parameter guesses.  If *None*, defaults to all-ones.
    bounds : tuple
        Lower/upper bounds as ``([lb1, lb2, …], [ub1, ub2, …])``.
    model_name : str
        Label for the FitResult.
    max_nfev : int
        Maximum number of function evaluations.

    Returns
    -------
    FitResult
    """
    y_arr = np.asarray(y, dtype=float)
    if isinstance(x, tuple):
        x_in = tuple(np.asarray(xi, dtype=float) for xi in x)
    else:
        x_in = np.asarray(x, dtype=float)

    if p0 is None:
        p0 = [1.0] * len(param_names)

    converged = True
    try:
        popt, pcov = curve_fit(
            fn,
            x_in,  # type: ignore[arg-type]
            y_arr,
            p0=p0,
            bounds=bounds,
            maxfev=max_nfev,
        )
    except (RuntimeError, ValueError) as exc:
        warnings.warn(f"curve_fit failed for {model_name!r}: {exc}")
        popt = np.array(p0, dtype=float)
        pcov = np.full((len(p0), len(p0)), np.nan)
        converged = False

    param_dict = dict(zip(param_names, popt))
    se_dict = dict(zip(param_names, np.sqrt(np.maximum(np.diag(pcov), 0.0))))

    # Predictions and metrics
    if isinstance(x_in, tuple):
        y_pred = fn(*x_in, *popt)
    else:
        y_pred = fn(x_in, *popt)

    report = met.model_report(y_arr, y_pred, n_params=len(popt), model_name=model_name)

    return FitResult(
        model_name=model_name,
        params=param_dict,
        param_se=se_dict,
        covariance=pcov,
        metrics=report,
        converged=converged,
    )


# ---------------------------------------------------------------------------
# Model selection over a catalog
# ---------------------------------------------------------------------------


def select_model(
    catalogue: dict[str, dict],
    x: ArrayLike,
    y: ArrayLike,
    criterion: str = "aicc",
    covariate_keys: Optional[list[str]] = None,
) -> tuple[str, FitResult, list[FitResult]]:
    """Fit all models in a catalogue and select the best by information criterion.

    Parameters
    ----------
    catalogue : dict
        Model catalogue such as ``HD_MODELS`` or ``BIOMASS_MODELS``.
        Each entry must have keys ``fn``, ``params``, ``p0``, ``bounds``.
    x : array-like or tuple
        Covariate(s) in the same order the model function expects.
    y : array-like
        Response variable.
    criterion : str
        Comparison criterion: ``"aicc"`` (default), ``"aic"``, ``"bic"``,
        ``"r2"`` (maximised), or ``"rmse"`` (minimised).
    covariate_keys : list[str], optional
        Subset of catalogue keys to evaluate.  Defaults to all.

    Returns
    -------
    best_name : str
    best_result : FitResult
    all_results : list[FitResult]
    """
    keys = covariate_keys or list(catalogue.keys())
    results: list[FitResult] = []

    for key in keys:
        entry = catalogue[key]
        res = fit_model(
            fn=entry["fn"],
            x=x,
            y=y,
            param_names=entry["params"],
            p0=entry.get("p0"),
            bounds=entry.get("bounds", (-np.inf, np.inf)),
            model_name=key,
        )
        results.append(res)

    # Sort by criterion
    maximise = criterion in ("r2",)

    def _score(r: FitResult) -> float:
        v = r.metrics.get(criterion, float("nan"))
        if not np.isfinite(v):
            return -np.inf if maximise else np.inf
        return v

    results.sort(key=_score, reverse=maximise)
    best = results[0]
    return best.model_name, best, results


# ---------------------------------------------------------------------------
# Bootstrap confidence intervals (Burt / treeallom approach)
# ---------------------------------------------------------------------------


def bootstrap_ci(
    fn: Callable,
    x: ArrayLike,
    y: ArrayLike,
    param_names: list[str],
    p0: Optional[list[float]] = None,
    bounds: tuple = (-np.inf, np.inf),
    n_boot: int = 1000,
    alpha: float = 0.05,
    random_state: Optional[int] = None,
) -> tuple[dict[str, float], dict[str, float]]:
    """Parametric bootstrap confidence intervals for curve_fit parameters.

    Resamples (x, y) with replacement and re-fits ``fn`` at each replicate.

    Parameters
    ----------
    fn, x, y, param_names, p0, bounds
        Same as in :func:`fit_model`.
    n_boot : int
        Number of bootstrap replicates.
    alpha : float
        Significance level (e.g. 0.05 for 95 % CI).
    random_state : int, optional
        Seed for reproducibility.

    Returns
    -------
    ci_lower, ci_upper : dict[str, float]
    """
    rng = np.random.default_rng(random_state)
    y_arr = np.asarray(y, dtype=float)
    if isinstance(x, tuple):
        x_arrs = tuple(np.asarray(xi, dtype=float) for xi in x)
        n = len(x_arrs[0])
    else:
        x_arrs = np.asarray(x, dtype=float)
        n = len(x_arrs)

    boot_params = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        y_b = y_arr[idx]
        if isinstance(x_arrs, tuple):
            x_b: tuple | np.ndarray = tuple(xi[idx] for xi in x_arrs)
        else:
            x_b = x_arrs[idx]
        try:
            popt, _ = curve_fit(
                fn,
                x_b,
                y_b,  # type: ignore[arg-type]
                p0=p0 or [1.0] * len(param_names),
                bounds=bounds,
                maxfev=3000,
            )
            boot_params.append(popt)
        except (RuntimeError, ValueError):
            continue  # skip failed replicates

    if not boot_params:
        nan_dict = {k: float("nan") for k in param_names}
        return nan_dict, nan_dict

    arr = np.array(boot_params)
    lo = np.percentile(arr, alpha / 2 * 100, axis=0)
    hi = np.percentile(arr, (1 - alpha / 2) * 100, axis=0)
    return dict(zip(param_names, lo)), dict(zip(param_names, hi))
