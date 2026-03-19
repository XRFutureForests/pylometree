"""Crown-based allometric models.

Predict AGB and/or DBH from crown measurements (crown area, crown height).
These models are of special relevance when trees are measured by remote
sensing (UAV-LiDAR, ALS) rather than field instruments.

References
----------
- Jucker T et al. (2017) Allometric equations for integrating remote sensing
  imagery into forest monitoring programmes.  Global Change Biology 23(1).
  doi:10.1111/gcb.13388
- Htoo H et al. (2025) Crown-based allometric equations for UAV-LiDAR in
  23 species-rich natural forests of Japan.
- Aguilar F J et al. (2021) TLS + ML regression for teak allometry.
  Applied Sciences 11(21):10139.  doi:10.3390/app11210139
"""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike


def _arr(x: ArrayLike) -> np.ndarray:
    return np.asarray(x, dtype=float)


# ---------------------------------------------------------------------------
# AGB from crown dimensions (Jucker et al. 2017 / Htoo et al. 2025)
# ---------------------------------------------------------------------------


def agb_from_crown(
    hst: ArrayLike,
    crown_area: ArrayLike,
    a: float,
    b: float,
    c: float,
) -> np.ndarray:
    """AGB from crown height and crown area (power-law form).

    AGB = a · H^b · CA^c

    Parameters
    ----------
    hst : array-like
        Total or crown height (m).
    crown_area : array-like
        Projected crown area (m²).
    a, b, c : float
        Fitted parameters.

    Notes
    -----
    Jucker et al. (2017) provide pantropical coefficients for this form.
    After log-transformation: ln(AGB) = ln(a) + b·ln(H) + c·ln(CA).
    """
    return a * _arr(hst) ** b * _arr(crown_area) ** c


def jucker2017_agb(hst: ArrayLike, crown_area: ArrayLike) -> np.ndarray:
    """Jucker et al. (2017) pantropical crown-based AGB equation (kg).

    AGB = 0.016 · H^0.940 · CA^0.932

    Returns AGB in **kg dry mass**.

    Valid range (from paper): H 2–70 m, CA 1–1500 m².

    Reference
    ---------
    Jucker T, Caspersen J, Chave J, et al. (2017) Allometric equations for
    integrating remote sensing imagery into forest monitoring programmes.
    Global Change Biology 23(1):177-190. doi:10.1111/gcb.13388
    """
    return 0.016 * _arr(hst) ** 0.940 * _arr(crown_area) ** 0.932


# ---------------------------------------------------------------------------
# DBH from crown dimensions
# ---------------------------------------------------------------------------


def dbh_from_crown_height(hst: ArrayLike, a: float, b: float) -> np.ndarray:
    """DBH from tree height.

    DBH = a · H^b  (power-law)

    Used in TLS/UAV studies (Aguilar et al. 2021: teak, Ecuador).
    """
    return a * _arr(hst) ** b


def dbh_from_height_cd(
    hst: ArrayLike, crown_diam: ArrayLike, a: float, b: float, c: float
) -> np.ndarray:
    """DBH from height and crown diameter.

    DBH = a · H^b · CD^c

    Adding crown diameter improved model accuracy in Aguilar et al. (2021).
    """
    return a * _arr(hst) ** b * _arr(crown_diam) ** c


# ---------------------------------------------------------------------------
# Crown area ↔ crown diameter conversions
# ---------------------------------------------------------------------------


def crown_area_from_diameter(crown_diam: ArrayLike) -> np.ndarray:
    """Projected crown area from crown diameter assuming circular crown.

    CA = π · (CD/2)²  (m²)
    """
    return np.pi * (_arr(crown_diam) / 2.0) ** 2


def crown_diameter_from_area(crown_area: ArrayLike) -> np.ndarray:
    """Crown diameter from projected crown area assuming circular crown (m)."""
    return 2.0 * np.sqrt(_arr(crown_area) / np.pi)


# ---------------------------------------------------------------------------
# Crown ratio
# ---------------------------------------------------------------------------


def crown_ratio(crown_height: ArrayLike, total_height: ArrayLike) -> np.ndarray:
    """Crown ratio = crown height / total height (dimensionless, 0–1)."""
    return _arr(crown_height) / _arr(total_height)


# ---------------------------------------------------------------------------
# Model catalogue
# ---------------------------------------------------------------------------

CROWN_MODELS: dict[str, dict] = {
    "agb_from_crown": {
        "fn": agb_from_crown,
        "covariates": ["hst", "crown_area"],
        "params": ["a", "b", "c"],
        "p0": [0.016, 0.94, 0.93],
        "notes": "AGB = a·H^b·CA^c",
    },
    "dbh_from_crown_height": {
        "fn": dbh_from_crown_height,
        "covariates": ["hst"],
        "params": ["a", "b"],
        "p0": [2.0, 0.8],
        "notes": "DBH = a·H^b",
    },
    "dbh_from_height_cd": {
        "fn": dbh_from_height_cd,
        "covariates": ["hst", "crown_diam"],
        "params": ["a", "b", "c"],
        "p0": [1.5, 0.7, 0.5],
        "notes": "DBH = a·H^b·CD^c",
    },
}
