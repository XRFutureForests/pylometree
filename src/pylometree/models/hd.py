"""Height-Diameter (H-D) allometric model functions.

All functions share the signature  ``f(dsob, **params) -> h``  where

* ``dsob``  – diameter outside bark at breast height (cm)
* return    – total tree height (m)

The parameter names follow the convention:  ``a``, ``b``, ``c`` (and ``d``
for 4-parameter forms) so they integrate cleanly with scipy's ``curve_fit``.

References
----------
- Laskar et al. (2020) Musa balbisiana H-D models (exponential best fit)
- Pretzsch et al. (2025) Chapman-Richards for height-age (same form)
- Huang et al. (1992) – generalized logistic / Chapman-Richards review
- allometree (Song et al. 2020) – urban tree H-D review
- FAO/CIRAD H-D model catalogue (Picard, Saint-André, Henry 2012)
"""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _arr(x: ArrayLike) -> np.ndarray:
    return np.asarray(x, dtype=float)


# ---------------------------------------------------------------------------
# 2-parameter models
# ---------------------------------------------------------------------------


def power_law(dsob: ArrayLike, a: float, b: float) -> np.ndarray:
    """Power-law H-D model.

    H = a · D^b

    Parameters
    ----------
    dsob : array-like
        DBH (cm).
    a, b : float
        Scale and shape parameters.
    """
    d = _arr(dsob)
    return a * d**b


def log_linear(dsob: ArrayLike, a: float, b: float) -> np.ndarray:
    """Log-linear H-D model (linearised power-law).

    H = exp(a + b · ln(D))   ≡   H = exp(a) · D^b

    Equivalent to power_law but parameterised in log-space.
    """
    d = _arr(dsob)
    return np.exp(a + b * np.log(d))


def hyperbolic(dsob: ArrayLike, a: float, b: float) -> np.ndarray:
    """Hyperbolic / reciprocal H-D model.

    H = D / (a + b · D)   or equivalently   H = a + b/D

    Common form used in forest mensuration.
    """
    d = _arr(dsob)
    return d / (a + b * d)


def michaelis_menten(dsob: ArrayLike, a: float, b: float) -> np.ndarray:
    """Michaelis-Menten asymptotic H-D model.

    H = a · D / (b + D)

    Parameter ``a`` is the asymptotic height; ``b`` is the half-saturation
    constant (DBH at half max height).
    """
    d = _arr(dsob)
    return a * d / (b + d)


def logarithmic(dsob: ArrayLike, a: float, b: float) -> np.ndarray:
    """Logarithmic H-D relationship.

    H = a + b · ln(D)
    """
    d = _arr(dsob)
    return a + b * np.log(d)


# ---------------------------------------------------------------------------
# 3-parameter models
# ---------------------------------------------------------------------------


def chapman_richards(dsob: ArrayLike, a: float, b: float, c: float) -> np.ndarray:
    """Chapman-Richards H-D model (3-parameter).

    H = a · (1 − exp(−b · D))^c

    ``a`` – asymptotic height (m)
    ``b`` – growth rate parameter (cm⁻¹)
    ``c`` – shape parameter (dimensionless)

    References
    ----------
    Richards (1959); Chapman (1961); Pretzsch et al. (2025).
    """
    d = _arr(dsob)
    return a * (1.0 - np.exp(-b * d)) ** c


def exponential_3p(dsob: ArrayLike, a: float, b: float, c: float) -> np.ndarray:
    """3-parameter exponential H-D model.

    H = a − b · exp(−c · D)

    Best-performing model for *Musa balbisiana* (Laskar et al. 2020,
    AICw = 0.57).  Asymptote is ``a`` as D → ∞.
    """
    d = _arr(dsob)
    return a - b * np.exp(-c * d)


def gompertz(dsob: ArrayLike, a: float, b: float, c: float) -> np.ndarray:
    """Gompertz H-D model.

    H = a · exp(−exp(b − c · D))

    ``a`` – asymptotic height; ``b``, ``c`` – shape parameters.
    """
    d = _arr(dsob)
    return a * np.exp(-np.exp(b - c * d))


def von_bertalanffy(dsob: ArrayLike, a: float, b: float, c: float) -> np.ndarray:
    """Von Bertalanffy H-D growth model.

    H = a · (1 − b · exp(−c · D))^3

    Cube-root formulation of the von Bertalanffy growth function.
    """
    d = _arr(dsob)
    return a * (1.0 - b * np.exp(-c * d)) ** 3


def logistic_3p(dsob: ArrayLike, a: float, b: float, c: float) -> np.ndarray:
    """3-parameter logistic (sigmoid) H-D model.

    H = a / (1 + b · exp(−c · D))
    """
    d = _arr(dsob)
    return a / (1.0 + b * np.exp(-c * d))


# ---------------------------------------------------------------------------
# 4-parameter models
# ---------------------------------------------------------------------------


def weibull_4p(
    dsob: ArrayLike, a: float, b: float, c: float, d_par: float
) -> np.ndarray:
    """4-parameter Weibull H-D model.

    H = a · (1 − exp(−b · D^c)) + d_par

    ``a`` – scale; ``b`` – rate; ``c`` – shape; ``d_par`` – offset.
    """
    x = _arr(dsob)
    return a * (1.0 - np.exp(-b * x**c)) + d_par


def korf(dsob: ArrayLike, a: float, b: float, c: float) -> np.ndarray:
    """Korf (reciprocal exponential) H-D model.

    H = a · exp(−b · D^(−c))

    Also known as the Lundqvist-Korf model.
    """
    d = _arr(dsob)
    return a * np.exp(-b * d ** (-c))


# ---------------------------------------------------------------------------
# Logarithmic growth model (YouTube / textbook)
# ---------------------------------------------------------------------------


def log_time_growth(t: ArrayLike, h1: float, h_rate: float) -> np.ndarray:
    """Logarithmic height-time growth model.

    H(t) = H₁ + h_rate · ln(t)

    where ``t`` is time (years) and ``H₁`` is height at t = 1.

    References
    ----------
    YouTube: "The Mathematics of Tree Growth" (logarithmic model).
    """
    t_arr = _arr(t)
    return h1 + h_rate * np.log(t_arr)


# ---------------------------------------------------------------------------
# Catalogue of named H-D models for fitting
# ---------------------------------------------------------------------------

HD_MODELS: dict[str, dict] = {
    "power_law": {
        "fn": power_law,
        "params": ["a", "b"],
        "p0": [1.5, 0.6],
        "bounds": ([0, 0], [np.inf, 2]),
        "notes": "H = a·D^b",
    },
    "log_linear": {
        "fn": log_linear,
        "params": ["a", "b"],
        "p0": [0.5, 0.6],
        "bounds": ([-np.inf, 0], [np.inf, 2]),
        "notes": "H = exp(a + b·ln(D))",
    },
    "hyperbolic": {
        "fn": hyperbolic,
        "params": ["a", "b"],
        "p0": [0.05, 0.05],
        "bounds": ([0, 0], [np.inf, np.inf]),
        "notes": "H = D / (a + b·D)",
    },
    "michaelis_menten": {
        "fn": michaelis_menten,
        "params": ["a", "b"],
        "p0": [30.0, 10.0],
        "bounds": ([0, 0], [np.inf, np.inf]),
        "notes": "H = a·D / (b + D)",
    },
    "logarithmic": {
        "fn": logarithmic,
        "params": ["a", "b"],
        "p0": [1.0, 4.0],
        "bounds": ([-np.inf, 0], [np.inf, np.inf]),
        "notes": "H = a + b·ln(D)",
    },
    "chapman_richards": {
        "fn": chapman_richards,
        "params": ["a", "b", "c"],
        "p0": [30.0, 0.05, 1.0],
        "bounds": ([0, 0, 0], [np.inf, np.inf, 10]),
        "notes": "H = a·(1 − exp(−b·D))^c",
    },
    "exponential_3p": {
        "fn": exponential_3p,
        "params": ["a", "b", "c"],
        "p0": [30.0, 28.0, 0.05],
        "bounds": ([0, 0, 0], [np.inf, np.inf, np.inf]),
        "notes": "H = a − b·exp(−c·D)  [best for Musa, Laskar 2020]",
    },
    "gompertz": {
        "fn": gompertz,
        "params": ["a", "b", "c"],
        "p0": [30.0, 3.0, 0.1],
        "bounds": ([0, 0, 0], [np.inf, np.inf, np.inf]),
        "notes": "H = a·exp(−exp(b − c·D))",
    },
    "von_bertalanffy": {
        "fn": von_bertalanffy,
        "params": ["a", "b", "c"],
        "p0": [30.0, 0.9, 0.05],
        "bounds": ([0, 0, 0], [np.inf, 1, np.inf]),
        "notes": "H = a·(1 − b·exp(−c·D))^3",
    },
    "logistic_3p": {
        "fn": logistic_3p,
        "params": ["a", "b", "c"],
        "p0": [35.0, 10.0, 0.1],
        "bounds": ([0, 0, 0], [np.inf, np.inf, np.inf]),
        "notes": "H = a / (1 + b·exp(−c·D))",
    },
    "weibull_4p": {
        "fn": weibull_4p,
        "params": ["a", "b", "c", "d_par"],
        "p0": [30.0, 0.05, 1.0, 1.3],
        "bounds": ([0, 0, 0, -np.inf], [np.inf, np.inf, 10, np.inf]),
        "notes": "H = a·(1 − exp(−b·D^c)) + d",
    },
    "korf": {
        "fn": korf,
        "params": ["a", "b", "c"],
        "p0": [35.0, 5.0, 0.5],
        "bounds": ([0, 0, 0], [np.inf, np.inf, np.inf]),
        "notes": "H = a·exp(−b·D^(−c))",
    },
}
