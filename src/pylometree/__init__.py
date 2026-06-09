"""
pylometree – General-purpose tree allometry toolkit.

Subpackages
-----------
models      : Allometric model functions (H-D, biomass, crown, volume, age)
fitting     : Curve fitting, bootstrap CIs, model selection
registry    : Published-equation registry with metadata
metrics     : Model evaluation (R², AIC, AICc, RMSE, MAE, MSA, SSPB)
data        : Tree/Stand data classes and physical constants
io          : CSV / DataFrame ingestion helpers
units       : Unit conversion system using Pint
taxonomy    : Taxonomic searching and species management
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("pylometree")
except PackageNotFoundError:
    __version__ = "0.0.0+dev"

import pylometree.registry.published  # noqa: F401  – populate registry
from pylometree.data.stand import Stand
from pylometree.data.tree import Tree
from pylometree.registry.base import ModelEntry, ModelRegistry, registry
from pylometree.taxonomy import Taxa, Taxon, search_by_taxon, search_by_taxonomic_level
from pylometree.units import Units
from pylometree.units import Units as units
from pylometree.units import convert_units, set_units

__all__ = [
    "__version__",
    "Tree",
    "Stand",
    "ModelEntry",
    "ModelRegistry",
    "registry",
    "Units",
    "convert_units",
    "set_units",
    "units",
    "Taxon",
    "Taxa",
    "search_by_taxon",
    "search_by_taxonomic_level",
]
