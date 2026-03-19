"""Stem volume and age-from-height allometric models.

Volume models
-------------
Form-factor method (Tripura study): V = f · π/4 · d² · h
Taper-based volume via conoid frustum (branch volumes)
BEF pipeline: AGB = V_stem · ρ_avg · BEF

Age from height
---------------
Extended Chapman-Richards inverse (Pretzsch et al. 2025)
for Norway spruce, Scots pine, European beech, sessile/common oak.

Variable names
--------------
dsob  – DBH outside bark (cm)
hst   – total stem height (m)
vsia  – stem volume inside bark (m³)
vsoa  – stem volume outside bark (m³)
agb   – above-ground biomass (kg)
"""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike


def _arr(x: ArrayLike) -> np.ndarray:
    return np.asarray(x, dtype=float)


# ---------------------------------------------------------------------------
# Stem volume
# ---------------------------------------------------------------------------


def volume_cylinder(dsob: ArrayLike, hst: ArrayLike) -> np.ndarray:
    """Stem volume approximated as a cylinder (m³).

    V = π/4 · (DBH/100)² · H

    Upper bound; real stems taper, so use with form factor.
    """
    d_m = _arr(dsob) / 100.0  # cm → m
    return np.pi / 4.0 * d_m**2 * _arr(hst)


def volume_form_factor(
    dsob: ArrayLike, hst: ArrayLike, form_factor: float = 0.5
) -> np.ndarray:
    """Stem volume using a constant form factor.

    V = f · π/4 · (DBH/100)² · H

    Parameters
    ----------
    form_factor : float
        Typically 0.4–0.6 for closed-canopy forests. The Tripura study uses
        a height-dependent form:  f = (2/3) · (h_{0.5} / h_stem).

    Notes
    -----
    For a rough generic estimate use f = 0.5 (neiloid-paraboloid average).
    """
    return form_factor * volume_cylinder(dsob, hst)


def volume_power_law(
    dsob: ArrayLike, hst: ArrayLike, a: float, b: float, c: float
) -> np.ndarray:
    """Volume via combined-variable power-law equation.

    V = a · DBH^b · H^c

    Standard forest mensuration form; fitted from taper data.
    """
    return a * _arr(dsob) ** b * _arr(hst) ** c


def volume_to_agb(
    volume_m3: ArrayLike,
    wood_density: float,
    bef: float = 1.0,
) -> np.ndarray:
    """Convert stem volume to AGB via wood density × BEF.

    AGB (kg) = V_stem (m³) × ρ (kg m⁻³) × BEF

    Parameters
    ----------
    volume_m3 : array-like
        Stem volume in m³.
    wood_density : float
        Oven-dry wood density in **kg m⁻³** (divide g/cm³ value by 1000×10³
        → multiply g/cm³ by 1000 to get kg/m³).
    bef : float
        Biomass Expansion Factor (dimensionless); use ``BEF_TROPICAL_INDIA``
        (1.59) or the nearest biome value from IPCC tables.
    """
    return _arr(volume_m3) * wood_density * bef


# ---------------------------------------------------------------------------
# Conoid frustum volume (branch / log sections)
# ---------------------------------------------------------------------------


def conoid_frustum_volume(
    d_base: ArrayLike, d_top: ArrayLike, length: ArrayLike
) -> np.ndarray:
    """Volume of a conoid frustum (truncated cone) in m³.

    V = π·L/12 · (D_base² + D_base·D_top + D_top²)

    Used for branch-volume summation in detailed volume inventories
    (Tripura study methodology).

    Parameters
    ----------
    d_base, d_top : array-like
        Diameters at the base and top of the section (cm).
    length : array-like
        Length of the section (m).
    """
    db = _arr(d_base) / 100.0  # cm → m
    dt = _arr(d_top) / 100.0
    l = _arr(length)
    return np.pi * l / 12.0 * (db**2 + db * dt + dt**2)


# ---------------------------------------------------------------------------
# Age from height – Chapman-Richards inverse (Pretzsch et al. 2025)
# ---------------------------------------------------------------------------


def height_from_age_cr(
    age: ArrayLike,
    hmax: float,
    k: float,
    c: float,
    si_correction: float = 0.0,
) -> np.ndarray:
    """Chapman-Richards height-age growth model.

    H(t) = H_max · (1 − exp(−k · t))^c + SI_correction

    Parameters
    ----------
    age : array-like
        Stand age (years).
    hmax : float
        Asymptotic maximum height (m).
    k : float
        Growth rate constant (yr⁻¹).
    c : float
        Shape parameter.
    si_correction : float
        Site-index additive correction (m).  Use 0 when SI is embedded in hmax.

    References
    ----------
    Pretzsch H, del Río M, Ammer C, et al. (2025) Estimating tree age from
    height using the extended Chapman-Richards function. Trees.
    doi:10.1007/s00468-025-02692-0
    """
    t = _arr(age)
    return hmax * (1.0 - np.exp(-k * t)) ** c + si_correction


def age_from_height_cr(
    hst: ArrayLike,
    hmax: float,
    k: float,
    c: float,
    si_correction: float = 0.0,
) -> np.ndarray:
    """Inverse Chapman-Richards: estimate age from height.

    t = −(1/k) · ln(1 − (H / H_max)^(1/c))

    Parameters
    ----------
    hst : array-like
        Observed height (m).
    hmax, k, c : float
        Parameters of the forward Chapman-Richards model.
    si_correction : float
        Site-index correction applied in the forward model.

    Returns
    -------
    np.ndarray
        Estimated age in years.  Returns ``nan`` for H ≥ H_max − SI_correction.

    References
    ----------
    Pretzsch et al. (2025).
    """
    h = _arr(hst) - si_correction
    ratio = h / hmax
    # Clamp to avoid NaN from values ≥ 1.0
    ratio = np.where(ratio >= 1.0, np.nan, ratio)
    with np.errstate(invalid="ignore"):
        age = -1.0 / k * np.log(1.0 - ratio ** (1.0 / c))
    return age


# ---------------------------------------------------------------------------
# Published species-level Chapman-Richards parameters (Pretzsch et al. 2025)
# ---------------------------------------------------------------------------

# Parameters for H_max, k, c at medium site index (SI reference = 100 yr)
# These are indicative values; species × site × stand-density interaction
# requires the full equations from the paper.
CR_SPECIES_PARAMS: dict[str, dict[str, float]] = {
    "Picea abies": {"hmax": 48.0, "k": 0.028, "c": 1.30},  # Norway spruce
    "Pinus sylvestris": {"hmax": 38.0, "k": 0.030, "c": 1.10},  # Scots pine
    "Fagus sylvatica": {"hmax": 42.0, "k": 0.024, "c": 1.20},  # European beech
    "Quercus petraea": {"hmax": 36.0, "k": 0.020, "c": 1.15},  # Sessile oak
    "Quercus robur": {"hmax": 34.0, "k": 0.019, "c": 1.10},  # Common oak
}
