"""Physical and biological constants used in allometric calculations.

Sources
-------
- BEF tropical India: Tripura study (tropical moist deciduous, BEF=1.59)
- Root:shoot ratios: Mokany et al. (2006) global meta-analysis
- Carbon fraction: Ehrmann & Schroth (0.50 convention)
- BCEF_S (biomass conversion & expansion factors): IPCC Aalde et al. (2006)
  Tables 4.3/4.4 (used by EhrmannS/tree-allometry)
- Wood density (ρ): global averages from Chave et al. (2009)
"""

# Carbon fraction of dry biomass (dimensionless)
CARBON_FRACTION: float = 0.47  # IPCC default; 0.50 also widely used

# Biomass Expansion Factor for Indian tropical forests (dimensionless)
BEF_TROPICAL_INDIA: float = 1.59

# Root-to-shoot ratios by biome (Mokany et al. 2006)
ROOT_SHOOT: dict[str, float] = {
    "tropical_moist": 0.235,
    "tropical_dry": 0.275,
    "temperate_broadleaf": 0.261,
    "temperate_conifer": 0.228,
    "boreal": 0.310,
    "mediterranean": 0.291,
}

# BCEF_S – stem wood biomass conversion & expansion factors
# IPCC 2006 GL, Vol 4, Ch 4, Table 4.5 (t DM per m³ over-bark)
BCEF_S: dict[str, float] = {
    "temperate_broadleaf_young": 1.10,  # < 20 m³/ha
    "temperate_broadleaf_medium": 0.82,  # 20-80 m³/ha
    "temperate_broadleaf_mature": 0.59,  # > 80 m³/ha
    "temperate_conifer_young": 1.19,
    "temperate_conifer_medium": 0.83,
    "temperate_conifer_mature": 0.63,
    "boreal_conifer": 0.80,
    "tropical_moist": 0.87,
}

# Mean wood densities (g/cm³) by broad group; Chave et al. 2009 / IPCC
WOOD_DENSITY_DEFAULTS: dict[str, float] = {
    "tropical_hardwood": 0.60,
    "temperate_broadleaf": 0.55,
    "temperate_conifer": 0.45,
    "boreal_conifer": 0.40,
    "mangrove": 0.65,
    "generic": 0.55,
}

# Breast-height definition (m above ground)
BREAST_HEIGHT: float = 1.30
