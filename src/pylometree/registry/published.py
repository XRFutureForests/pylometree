"""Populate the global registry with published allometric equations.

This module is imported by ``pylometree.__init__`` and adds well-known
published equations to the singleton ``registry``.

To add your own equations:

    from pylometree.registry import registry, ModelEntry
    registry.register(ModelEntry(...))
"""

from __future__ import annotations

from pylometree.models.biomass import chave2014, m1_dbh, m3_d2h, m4_dbh_height
from pylometree.models.crown import jucker2017_agb
from pylometree.models.hd import (
    chapman_richards,
    exponential_3p,
    gompertz,
    hyperbolic,
    log_linear,
    michaelis_menten,
    power_law,
)
from pylometree.models.volume import (
    height_from_age_cr,
    volume_form_factor,
    volume_power_law,
)
from pylometree.registry.base import ModelEntry, registry

# ---------------------------------------------------------------------------
# Biomass – generic / pantropical
# ---------------------------------------------------------------------------

registry.register(
    ModelEntry(
        model_id="chave2014_pantropical",
        model_type="agb",
        equation_form="AGB = 0.0673 · (rho · DBH² · H)^0.976",
        response="agb",
        covariates=["dsob", "hst", "rho"],
        parameters={"a": 0.0673, "b": 0.976},
        fn=lambda dsob, hst, rho, **_: chave2014(dsob, hst, rho),
        species=[],
        region=["pantropical"],
        reference=(
            "Chave J et al. (2014) Improved allometric models to estimate "
            "the aboveground biomass of tropical trees.  Global Change "
            "Biology 20(10):3177-3190.  doi:10.1111/gcb.12629"
        ),
        pub_year=2014,
        units={"agb": "kg", "dsob": "cm", "hst": "m", "rho": "g/cm3"},
        notes="n=4004 trees, 58 sites, pantropical.  Valid DBH 5-212 cm.",
    )
)

# ---------------------------------------------------------------------------
# Crown-based AGB – Jucker et al. 2017
# ---------------------------------------------------------------------------

registry.register(
    ModelEntry(
        model_id="jucker2017_crown_agb",
        model_type="crown_agb",
        equation_form="AGB = 0.016 · H^0.940 · CA^0.932",
        response="agb",
        covariates=["hst", "crown_area"],
        parameters={"a": 0.016, "b": 0.940, "c": 0.932},
        fn=lambda hst, crown_area, **_: jucker2017_agb(hst, crown_area),
        species=[],
        region=["pantropical"],
        reference=(
            "Jucker T, Caspersen J, Chave J, et al. (2017) Allometric "
            "equations for integrating remote sensing imagery into forest "
            "monitoring programmes.  Global Change Biology 23(1):177-190. "
            "doi:10.1111/gcb.13388"
        ),
        pub_year=2017,
        units={"agb": "kg", "hst": "m", "crown_area": "m2"},
        notes="Pantropical crown-based; requires only H and crown area.",
    )
)

# ---------------------------------------------------------------------------
# Musa balbisiana – Laskar et al. 2020
# ---------------------------------------------------------------------------


def _musa_agb(dsob, hst, **_):
    from pylometree.models.biomass import musa_agb

    return musa_agb(dsob, hst)


registry.register(
    ModelEntry(
        model_id="laskar2020_musa_agb",
        model_type="agb",
        equation_form="AGB = exp(-4.54 + 0.874·ln(D²H)) × CF(1.06)",
        response="agb",
        covariates=["dsob", "hst"],
        parameters={"log_a": -4.54, "b": 0.874, "cf": 1.06},
        fn=_musa_agb,
        species=["Musa balbisiana"],
        region=["tropical_asia"],
        reference=(
            "Laskar S Y et al. (2020) Allometric models for estimating "
            "biomass of wild Musa balbisiana.  Journal of Environmental "
            "Management."
        ),
        pub_year=2020,
        units={"agb": "kg", "dsob": "cm", "hst": "m"},
        notes="NSUR additive system.  D²H composite.  Sample n=240 plants.",
    )
)

# ---------------------------------------------------------------------------
# H-D models
# ---------------------------------------------------------------------------

registry.register(
    ModelEntry(
        model_id="chapman_richards_generic_hd",
        model_type="hd",
        equation_form="H = a·(1 - exp(-b·D))^c",
        response="hst",
        covariates=["dsob"],
        parameters={"a": 30.0, "b": 0.05, "c": 1.0},
        fn=lambda dsob, a, b, c, **_: chapman_richards(dsob, a, b, c),
        species=[],
        region=[],
        reference="Richards (1959); Chapman (1961)",
        pub_year=1961,
        units={"hst": "m", "dsob": "cm"},
        notes="Generic form; parameters to be fitted to local data.",
    )
)

registry.register(
    ModelEntry(
        model_id="laskar2020_musa_hd_exponential",
        model_type="hd",
        equation_form="H = a - b·exp(-c·D)",
        response="hst",
        covariates=["dsob"],
        parameters={"a": 5.21, "b": 4.88, "c": 0.25},
        fn=lambda dsob, a, b, c, **_: exponential_3p(dsob, a, b, c),
        species=["Musa balbisiana"],
        region=["tropical_asia"],
        reference="Laskar S Y et al. (2020) Allometry of wild Musa balbisiana.",
        pub_year=2020,
        units={"hst": "m", "dsob": "cm"},
        notes="Best-fit H-D model for Musa; AICw=0.57.",
    )
)

# ---------------------------------------------------------------------------
# Height-age (Chapman-Richards) – Pretzsch et al. 2025 European species
# ---------------------------------------------------------------------------

from pylometree.models.volume import CR_SPECIES_PARAMS


def _make_height_age_fn(pars: dict[str, float]):
    """Factory to avoid closure-capture issues in the loop below."""
    return lambda age, **_: height_from_age_cr(age, **pars)


for _sp, _pars in CR_SPECIES_PARAMS.items():
    _sp_safe = _sp.lower().replace(" ", "_")
    registry.register(
        ModelEntry(
            model_id=f"pretzsch2025_{_sp_safe}_height_age",
            model_type="height_age",
            equation_form="H = hmax·(1 - exp(-k·t))^c",
            response="hst",
            covariates=["age"],
            parameters=_pars,
            fn=_make_height_age_fn(_pars),
            species=[_sp],
            region=["temperate_europe"],
            reference=(
                "Pretzsch H et al. (2025) Estimating tree age from height "
                "using the extended Chapman-Richards function.  Trees. "
                "doi:10.1007/s00468-025-02692-0"
            ),
            pub_year=2025,
            units={"hst": "m", "age": "years"},
            notes="Medium site index; ignores stand-density interaction.",
        )
    )

# ---------------------------------------------------------------------------
# Aboveground biomass – Zianis et al. 2005, European species
# ---------------------------------------------------------------------------
#
# Transcribed from Appendix A of Silva Fennica Monographs 4 (doi:10.14214/sf.sfm4),
# an open-access compilation of 607 published European biomass equations.
#
# Only entries meeting all of the following are included:
#   * component AB  = total aboveground biomass (not ABW, branch, foliage, ...)
#   * form M1 (a*D^b) or M4 (a*D^b*H^c)
#   * biomass in kg, D in cm, H in m
#
# `eqNNN` in each model_id is the equation number in Appendix A, so every entry
# can be checked against the source. `notes` carries the sample size, r2, the
# fitted DBH range and the country, because the DBH range is what decides
# whether an equation may be applied to a given stand.
#
# Species with NO qualifying equation in the monograph -- Quercus robur,
# Quercus petraea, Abies alba and Larix decidua -- are deliberately absent
# rather than approximated by a congener.

_ZIANIS_REF = (
    "Zianis D, Muukkonen P, Mäkipää R, Mencuccini M (2005) Biomass and stem "
    "volume equations for tree species in Europe. Silva Fennica Monographs 4, "
    "63 p. doi:10.14214/sf.sfm4"
)


def _m1(a: float, b: float):
    return lambda dsob, **_: m1_dbh(dsob, a=a, b=b)


def _m4(a: float, b: float, c: float):
    return lambda dsob, hst, **_: m4_dbh_height(dsob, hst, a=a, b=b, c=c)


_ZIANIS_AGB = [
    # (eq_no, species, a, b, c or None, notes)
    (88, "Fagus sylvatica", 0.453, 2.139, None,
     "n=20, r2=0.974, D 5.7-62.1 cm, Czech Republic. Widest fitted DBH range "
     "of the beech entries."),
    (91, "Fagus sylvatica", 0.0798, 2.601, None,
     "n=38, r2=0.988, DBH range not reported, Netherlands."),
    (92, "Fagus sylvatica", 0.1315, 2.4321, None,
     "n=7, r2=0.98, D 4-34.5 cm, Spain. Small sample."),
    (90, "Fagus sylvatica", 0.0306, 2.347, 0.590,
     "n=38, r2=0.991, DBH range not reported, Netherlands. Highest r2 of the "
     "beech entries and uses height as well as diameter."),
    (141, "Picea abies", 0.57669, 1.964, None,
     "n=17, r2=0.967, D 11-47 cm, Czech Republic."),
    (151, "Picea abies", 0.2465, 2.12, -0.167, 
     "n=16, r2=0.981, D 2.7-27.9 cm, Iceland. Fitted on small trees at a "
     "marginal site; the negative height exponent is unusual."),
    (334, "Pinus sylvestris", 0.1182, 2.3281, None,
     "r2=0.98, D 2-16 cm, Czech Republic. Sapling/pole stage only -- do not "
     "apply to mature stands."),
    (328, "Pinus sylvestris", 0.1599, 2.2060, None,
     "r2=0.94, D 2-6 cm, Czech Republic. Saplings only."),
    (526, "Pseudotsuga menziesii", 0.111, 2.397, None,
     "D from 5 cm, upper bound not reported, Netherlands."),
]

for _no, _sp, _a, _b, _c, _note in _ZIANIS_AGB:
    _slug = _sp.lower().replace(" ", "_")
    registry.register(
        ModelEntry(
            model_id=f"zianis2005_eq{_no}_{_slug}_agb",
            model_type="agb",
            equation_form="AGB = a · D^b" if _c is None else "AGB = a · D^b · H^c",
            response="agb",
            covariates=["dsob"] if _c is None else ["dsob", "hst"],
            parameters={"a": _a, "b": _b} if _c is None else {"a": _a, "b": _b, "c": _c},
            fn=_m1(_a, _b) if _c is None else _m4(_a, _b, _c),
            species=[_sp],
            region=["temperate_europe"],
            reference=_ZIANIS_REF,
            pub_year=2005,
            units={"agb": "kg", "dsob": "cm"} if _c is None
            else {"agb": "kg", "dsob": "cm", "hst": "m"},
            notes=f"Appendix A eq. {_no}. Total aboveground biomass (AB). {_note}",
        )
    )
