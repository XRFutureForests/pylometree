"""Yield table resolution with priority chain.

Resolution uses only pre-ingested local data.  Runtime API calls to
openyieldtables.org have been removed -- use ``pylometree-ingest`` to
populate the store beforehand.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from pylometree.yield_tables.schema import YieldTableData
from pylometree.yield_tables.loaders import (
    load_local_yield_table,
    load_store_yield_table,
)

logger = logging.getLogger(__name__)


# Species proxy table: when no yield table is found for the primary species,
# fall back to a related species with similar growth characteristics.
# Key = standardized name, value = proxy standardized name.
#
# These are not ad-hoc guesses. Several German species were never given yield
# tables of their own -- the classical tables (Wiedemann, Schober, Gehrhardt,
# Wimmenauer et al.) cover the commercially dominant species only -- so forest
# administrations assign each remaining species an established table to use in
# its place. Where an official assignment exists it is followed here, and the
# entry says so; the authority is the Bavarian State Forest species-to-yield-
# table map shipped as `ytables_bavrn_state_var_1` in the ForestElementsR R
# package.
#
# A resolution through this table sets YieldTableData.proxy_for, so a caller
# can tell a substituted curve from the species' own and disclose it.
SPECIES_PROXIES: Dict[str, str] = {
    "field_maple": "sycamore_maple",  # Acer campestre -> A. pseudoplatanus
    "grand_fir": "silver_fir",  # Abies grandis -> A. alba (same genus)
    # Carpinus betulus -> Fagus sylvatica. Bavarian state assignment (id 63).
    "hornbeam": "european_beech",
    # Tilia cordata -> Fagus sylvatica (Wiedemann 1931). Matches the Bavarian
    # state assignment for Winterlinde (id 62) exactly.
    "small_leaved_linden": "european_beech",
    # Acer pseudoplatanus -> Fraxinus excelsior (Wimmenauer 1919/29). Matches
    # the Bavarian state assignment for Bergahorn (id 64) exactly.
    "sycamore_maple": "common_ash",
    # Prunus avium -> Fraxinus excelsior. The Bavarian state assigns Vogelkirsche
    # (id 68) the ash table, NOT birch as this entry used to say. Only reached
    # when the measured Pryor (FC Bulletin 75) cherry tables are not ingested.
    "wild_cherry": "common_ash",
}


def resolve_yield_table(
    species_common: str,
    species_std: str,
    yield_tables_dir: Optional[Path] = None,
    calibration_species: Optional[Dict[str, Dict[str, Any]]] = None,
    yield_search: str = "",
    store_dir: Optional[Path] = None,
    preferred_site_index: Optional[float] = None,
    preferred_region: str = "",
    preferred_h50: Optional[float] = None,
) -> Optional[YieldTableData]:
    """Resolve the best yield table for a species.

    Priority:
        1. Local CSV in yield_tables_dir (by standardized name)
        2. Ingested store (provider-generated CSVs via pylometree-ingest)
        3. Species proxy (related species with similar growth, see SPECIES_PROXIES)

    Unused keyword arguments (``calibration_species``, ``yield_search``)
    are accepted for backward compatibility but ignored.

    Args:
        species_common: Common name (e.g., "Norway spruce").
        species_std: Standardized name (e.g., "norway_spruce").
        yield_tables_dir: Path to local yield table CSVs.
        calibration_species: Accepted for compatibility, ignored.
        yield_search: Accepted for compatibility, ignored.
        store_dir: Path to the ingested yield table store.
        preferred_site_index: Preferred site index for store selection.
        preferred_region: Preferred region for store selection.
        preferred_h50: Preferred h50 (height at age 50) for store selection.
            When given, selects the table whose h50 is closest to this value.
            Takes priority over preferred_site_index.

    Returns:
        YieldTableData or None.
    """
    result = _try_resolve(
        species_std, yield_tables_dir, store_dir,
        preferred_site_index, preferred_region, preferred_h50,
    )
    if result:
        logger.info("  Using yield table: %s", result.title)
        return result

    # 3. Try species proxy chain (follow up to 3 hops to avoid cycles)
    current = species_std
    visited = {current}
    for _ in range(3):
        proxy_std = SPECIES_PROXIES.get(current)
        if not proxy_std or proxy_std in visited:
            break
        visited.add(proxy_std)
        result = _try_resolve(
            proxy_std, yield_tables_dir, store_dir,
            preferred_site_index, preferred_region, preferred_h50,
        )
        if result:
            chain = " -> ".join(visited)
            logger.info(
                "  Using proxy yield table for %s (%s): %s",
                species_common, chain, result.title,
            )
            result.proxy_for = species_std
            return result
        current = proxy_std

    logger.info("  No yield table found for %s", species_common)
    return None


def _try_resolve(
    species_std: str,
    yield_tables_dir: Optional[Path],
    store_dir: Optional[Path],
    preferred_site_index: Optional[float],
    preferred_region: str,
    preferred_h50: Optional[float],
) -> Optional[YieldTableData]:
    """Try local CSV then ingested store for a single species key."""
    # 1. Try local CSV
    if yield_tables_dir and yield_tables_dir.exists():
        local = load_local_yield_table(species_std, yield_tables_dir)
        if local:
            return local

    # 2. Try ingested store
    if store_dir and store_dir.exists():
        store_result = load_store_yield_table(
            species_std,
            store_dir,
            preferred_site_index,
            preferred_region,
            preferred_h50=preferred_h50,
        )
        if store_result:
            return store_result

    return None
