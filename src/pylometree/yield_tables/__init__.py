"""pylometree.yield_tables -- Yield table loading, ingestion, and store management.

Provides a provider-based system for extracting yield tables from external
sources (R packages, XLSX, PDF, parametric models, openyieldtables.org) and
a resolution chain for loading the best available table for a given species.

At **resolution time** only pre-ingested data is used (local CSVs and the
store).  To populate the store from external sources run ``pylometree-ingest``.

Usage::

    from pylometree.yield_tables import resolve_yield_table, YieldTableData

    result = resolve_yield_table(
        species_common="Norway spruce",
        species_std="norway_spruce",
        yield_tables_dir=Path("data/input/yield_tables"),
        store_dir=Path("data/input/yield_tables/store"),
    )
"""

from pylometree.yield_tables.schema import YieldTableData
from pylometree.yield_tables.record import YieldTableRecord
from pylometree.yield_tables.store import StoreManifest, select_best_table
from pylometree.yield_tables.species import SpeciesMapping, load_species_mapping
from pylometree.yield_tables.loaders import (
    load_local_yield_table,
    load_store_yield_table,
)
from pylometree.yield_tables.resolver import resolve_yield_table
from pylometree.yield_tables.providers import (
    YieldProvider,
    get_all_providers,
    get_available_providers,
    get_provider_by_name,
)

__all__ = [
    "YieldTableData",
    "YieldTableRecord",
    "StoreManifest",
    "select_best_table",
    "SpeciesMapping",
    "load_species_mapping",
    "load_local_yield_table",
    "load_store_yield_table",
    "resolve_yield_table",
    "YieldProvider",
    "get_all_providers",
    "get_available_providers",
    "get_provider_by_name",
]
