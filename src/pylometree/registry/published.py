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

registry.register(ModelEntry(
    model_id="chave2014_pantropical",
    model_type="agb",
    equation_form="AGB = 0.0673 · (rho · DBH² · H)^0.976",
    response="agb",
    covariates=["dsob", "hst", "rho"],
    parameters={"a": 0.0673, "b": 0.976},
    fn=lambda dsob, hst, rho, **_: chave2014(dsob, hst, rho),
    species=[],
    region=["pantropical"],
    reference=("Chave J et al. (2014) Improved allometric models to estimate "
               "the aboveground biomass of tropical trees.  Global Change "
               "Biology 20(10):3177-3190.  doi:10.1111/gcb.12629"),
    pub_year=2014,
    units={"agb": "kg", "dsob": "cm", "hst": "m", "rho": "g/cm3"},
    notes="n=4004 trees, 58 sites, pantropical.  Valid DBH 5-212 cm.",
))

# ---------------------------------------------------------------------------
# Crown-based AGB – Jucker et al. 2017
# ---------------------------------------------------------------------------

registry.register(ModelEntry(
    model_id="jucker2017_crown_agb",
    model_type="crown_agb",
    equation_form="AGB = 0.016 · H^0.940 · CA^0.932",
    response="agb",
    covariates=["hst", "crown_area"],
    parameters={"a": 0.016, "b": 0.940, "c": 0.932},
    fn=lambda hst, crown_area, **_: jucker2017_agb(hst, crown_area),
    species=[],
    region=["pantropical"],
    reference=("Jucker T, Caspersen J, Chave J, et al. (2017) Allometric "
               "equations for integrating remote sensing imagery into forest "
               "monitoring programmes.  Global Change Biology 23(1):177-190. "
               "doi:10.1111/gcb.13388"),
    pub_year=2017,
    units={"agb": "kg", "hst": "m", "crown_area": "m2"},
    notes="Pantropical crown-based; requires only H and crown area.",
))

# ---------------------------------------------------------------------------
# Musa balbisiana – Laskar et al. 2020
# ---------------------------------------------------------------------------

def _musa_agb(dsob, hst, **_):
    from pylometree.models.biomass import musa_agb
    return musa_agb(dsob, hst)


registry.register(ModelEntry(
    model_id="laskar2020_musa_agb",
    model_type="agb",
    equation_form="AGB = exp(-4.54 + 0.874·ln(D²H)) × CF(1.06)",
    response="agb",
    covariates=["dsob", "hst"],
    parameters={"log_a": -4.54, "b": 0.874, "cf": 1.06},
    fn=_musa_agb,
    species=["Musa balbisiana"],
    region=["tropical_asia"],
    reference=("Laskar S Y et al. (2020) Allometric models for estimating "
               "biomass of wild Musa balbisiana.  Journal of Environmental "
               "Management."),
    pub_year=2020,
    units={"agb": "kg", "dsob": "cm", "hst": "m"},
    notes="NSUR additive system.  D²H composite.  Sample n=240 plants.",
))

# ---------------------------------------------------------------------------
# H-D models
# ---------------------------------------------------------------------------

registry.register(ModelEntry(
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
))

registry.register(ModelEntry(
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
))

# ---------------------------------------------------------------------------
# Height-age (Chapman-Richards) – Pretzsch et al. 2025 European species
# ---------------------------------------------------------------------------

from pylometree.models.volume import CR_SPECIES_PARAMS

for _sp, _pars in CR_SPECIES_PARAMS.items():
    _sp_safe = _sp.lower().replace(" ", "_")
    registry.register(ModelEntry(
        model_id=f"pretzsch2025_{_sp_safe}_height_age",
        model_type="height_age",
        equation_form="H = hmax·(1 - exp(-k·t))^c",
        response="hst",
        covariates=["age"],
        parameters=_pars,
        fn=(lambda dsob, hmax, k, c, **_:  # noqa: E731
            height_from_age_cr(dsob, hmax, k, c)),
        species=[_sp],
        region=["temperate_europe"],
        reference=("Pretzsch H et al. (2025) Estimating tree age from height "
                   "using the extended Chapman-Richards function.  Trees. "
                   "doi:10.1007/s00468-025-02692-0"),
        pub_year=2025,
        units={"hst": "m", "age": "years"},
        notes="Medium site index; ignores stand-density interaction.",
    ))
                   "using the extended Chapman-Richards function.  Trees. "
                   "doi:10.1007/s00468-025-02692-0"),
        pub_year=2025,
        units={"hst": "m", "age": "years"},
        notes="Medium site index; ignores stand-density interaction.",
    ))
