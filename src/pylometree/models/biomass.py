"""Biomass allometric models.

All power-law functions are implemented in both natural-scale and
log-transformed forms.  Back-transformation from log-space requires a
correction factor  CF = exp(MSE / 2)  (Sprugel 1983) to remove the
systematic under-prediction bias.

Supported model forms (Laskar et al. 2020; Tripura study; Chave 2014)
-----------------------------------------------------------------------
M1 : AGB = a · DBH^b
M2 : AGB = a · H^b
M3 : AGB = a · (DBH² · H)^b          [best overall in Laskar 2020]
M4 : AGB = a · DBH^b · H^c
Chave2014  : AGB = 0.0673 · (ρ · DBH² · H)^0.976   [pantropical]
NSUR additive system (Laskar et al. 2020, Musa)

Variable naming
---------------
dsob  – DBH outside bark (cm)
hst   – total stem height (m)
rho   – wood density (g cm⁻³)
agb   – above-ground biomass (kg dry mass)
"""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike


def _arr(x: ArrayLike) -> np.ndarray:
    return np.asarray(x, dtype=float)


# ---------------------------------------------------------------------------
# Power-law forms (natural scale, additive error)
# ---------------------------------------------------------------------------


def m1_dbh(dsob: ArrayLike, a: float, b: float) -> np.ndarray:
    """M1 – DBH only.

    AGB = a · DBH^b
    """
    return a * _arr(dsob) ** b


def m2_height(hst: ArrayLike, a: float, b: float) -> np.ndarray:
    """M2 – Height only.

    AGB = a · H^b
    """
    return a * _arr(hst) ** b


def m3_d2h(dsob: ArrayLike, hst: ArrayLike, a: float, b: float) -> np.ndarray:
    """M3 – DBH² × H composite predictor.

    AGB = a · (DBH² · H)^b

    Best-performing form for Musa balbisiana (Laskar 2020) and widely
    used in tropical biomass studies.
    """
    d2h = _arr(dsob) ** 2 * _arr(hst)
    return a * d2h**b


def m4_dbh_height(
    dsob: ArrayLike, hst: ArrayLike, a: float, b: float, c: float
) -> np.ndarray:
    """M4 – DBH and height separately.

    AGB = a · DBH^b · H^c
    """
    return a * _arr(dsob) ** b * _arr(hst) ** c


def m5_rho_d2h(
    dsob: ArrayLike, hst: ArrayLike, rho: ArrayLike, a: float, b: float
) -> np.ndarray:
    """M5 – Wood density × DBH² × H (Chave-style).

    AGB = a · (ρ · DBH² · H)^b
    """
    combo = _arr(rho) * _arr(dsob) ** 2 * _arr(hst)
    return a * combo**b


# ---------------------------------------------------------------------------
# Log-transformed forms  (for OLS fitting in log-space)
# ---------------------------------------------------------------------------


def log_m1_dbh(log_dsob: ArrayLike, log_a: float, b: float) -> np.ndarray:
    """ln(AGB) = ln(a) + b · ln(DBH)"""
    return log_a + b * _arr(log_dsob)


def log_m3_d2h(log_d2h: ArrayLike, log_a: float, b: float) -> np.ndarray:
    """ln(AGB) = ln(a) + b · ln(DBH² · H)"""
    return log_a + b * _arr(log_d2h)


def log_m4_dbh_height(
    log_dsob: ArrayLike, log_hst: ArrayLike, log_a: float, b: float, c: float
) -> np.ndarray:
    """ln(AGB) = ln(a) + b · ln(DBH) + c · ln(H)"""
    return log_a + b * _arr(log_dsob) + c * _arr(log_hst)


# ---------------------------------------------------------------------------
# Back-transformation correction factor (Sprugel 1983)
# ---------------------------------------------------------------------------


def log_correction_factor(residuals: ArrayLike) -> float:
    """Compute the correction factor for bias in log back-transformation.

    CF = exp(MSE / 2)

    where MSE is the mean squared error of the log-space residuals.

    Parameters
    ----------
    residuals : array-like
        Residuals in log-space: ``ln(observed) - ln(predicted)``.
    """
    mse = float(np.mean(np.asarray(residuals, dtype=float) ** 2))
    return float(np.exp(mse / 2.0))


# ---------------------------------------------------------------------------
# Published pantropical equation – Chave et al. (2014)
# ---------------------------------------------------------------------------


def chave2014(dsob: ArrayLike, hst: ArrayLike, rho: ArrayLike) -> np.ndarray:
    """Chave et al. (2014) pantropical AGB equation.

    AGB = 0.0673 · (ρ · DBH² · H)^0.976

    Returns AGB in **kg dry mass**.

    Parameters
    ----------
    dsob : array-like
        DBH outside bark (cm).
    hst : array-like
        Total stem height (m).
    rho : array-like
        Wood specific gravity (g cm⁻³).

    References
    ----------
    Chave J, Réjou‐Méchain M, Búrquez A, et al. (2014) Improved allometric
    models to estimate the aboveground biomass of tropical trees. Global
    Change Biology 20(10): 3177-3190.  doi:10.1111/gcb.12629
    """
    return 0.0673 * (_arr(rho) * _arr(dsob) ** 2 * _arr(hst)) ** 0.976


# ---------------------------------------------------------------------------
# Musa balbisiana NSUR component equations (Laskar et al. 2020)
# ---------------------------------------------------------------------------


def musa_leaf_biomass(dsob: ArrayLike, hst: ArrayLike) -> np.ndarray:
    """Leaf biomass for *Musa balbisiana* (kg).

    W_leaf = exp(−7.27 + 1.12 · ln(D²H)) × CF(1.23)

    CF is already embedded (Laskar et al. 2020).
    """
    d2h = _arr(dsob) ** 2 * _arr(hst)
    return np.exp(-7.27 + 1.12 * np.log(d2h)) * 1.23


def musa_pseudostem_biomass(dsob: ArrayLike, hst: ArrayLike) -> np.ndarray:
    """Pseudostem biomass for *Musa balbisiana* (kg).

    W_ps = exp(−4.66 + 0.829 · ln(D²H)) × CF(1.06)
    """
    d2h = _arr(dsob) ** 2 * _arr(hst)
    return np.exp(-4.66 + 0.829 * np.log(d2h)) * 1.06


def musa_agb(dsob: ArrayLike, hst: ArrayLike) -> np.ndarray:
    """Total above-ground biomass for *Musa balbisiana* (kg).

    AGB = exp(−4.54 + 0.874 · ln(D²H)) × CF(1.06)
    """
    d2h = _arr(dsob) ** 2 * _arr(hst)
    return np.exp(-4.54 + 0.874 * np.log(d2h)) * 1.06


def musa_corm_biomass(dsob: ArrayLike, hst: ArrayLike) -> np.ndarray:
    """Corm (below-ground) biomass for *Musa balbisiana* (kg).

    W_corm = exp(−3.93 + 0.715 · ln(D²H)) × CF(1.09)
    """
    d2h = _arr(dsob) ** 2 * _arr(hst)
    return np.exp(-3.93 + 0.715 * np.log(d2h)) * 1.09


def musa_total_biomass_nsur(dsob: ArrayLike) -> np.ndarray:
    """Additive NSUR total biomass for *Musa balbisiana* (kg).

    W_total = 0.00428 · D^2.28 + 0.01039 · D^2.19 + 0.00679 · D^2.32

    The three terms represent leaf, pseudostem, and corm components
    constrained to sum to the total via systems of equations.

    Reference
    ---------
    Laskar S Y et al. (2020) Allometric models for estimating biomass of
    wild Musa balbisiana. Journal of Environmental Management.
    """
    d = _arr(dsob)
    return 0.00428 * d**2.28 + 0.01039 * d**2.19 + 0.00679 * d**2.32


# ---------------------------------------------------------------------------
# Below-ground biomass via root:shoot ratio
# ---------------------------------------------------------------------------


def bgb_from_agb(agb: ArrayLike, root_shoot: float) -> np.ndarray:
    """Estimate below-ground biomass from AGB and root:shoot ratio.

    BGB = AGB × R/S

    Parameters
    ----------
    agb : array-like
        Above-ground biomass (kg or Mg ha⁻¹).
    root_shoot : float
        Root-to-shoot ratio (dimensionless).  Use ``data.constants.ROOT_SHOOT``
        for published biome-level defaults (Mokany et al. 2006).
    """
    return _arr(agb) * root_shoot


# ---------------------------------------------------------------------------
# Biomass model catalogue
# ---------------------------------------------------------------------------

BIOMASS_MODELS: dict[str, dict] = {
    "m1_dbh": {
        "fn": m1_dbh,
        "covariates": ["dsob"],
        "params": ["a", "b"],
        "p0": [0.1, 2.0],
        "notes": "AGB = a·DBH^b",
    },
    "m2_height": {
        "fn": m2_height,
        "covariates": ["hst"],
        "params": ["a", "b"],
        "p0": [0.1, 2.0],
        "notes": "AGB = a·H^b",
    },
    "m3_d2h": {
        "fn": m3_d2h,
        "covariates": ["dsob", "hst"],
        "params": ["a", "b"],
        "p0": [0.05, 0.9],
        "notes": "AGB = a·(DBH²·H)^b",
    },
    "m4_dbh_height": {
        "fn": m4_dbh_height,
        "covariates": ["dsob", "hst"],
        "params": ["a", "b", "c"],
        "p0": [0.05, 2.0, 0.5],
        "notes": "AGB = a·DBH^b·H^c",
    },
    "m5_rho_d2h": {
        "fn": m5_rho_d2h,
        "covariates": ["dsob", "hst", "rho"],
        "params": ["a", "b"],
        "p0": [0.0673, 0.976],
        "notes": "AGB = a·(ρ·DBH²·H)^b",
    },
}
