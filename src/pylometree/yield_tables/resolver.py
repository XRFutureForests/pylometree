"""Yield table resolution with priority chain."""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from pylometree.yield_tables.schema import YieldTableData
from pylometree.yield_tables.loaders import (
    auto_discover_yield_table,
    load_local_yield_table,
    load_openyieldtables,
    load_store_yield_table,
)

logger = logging.getLogger(__name__)


def resolve_yield_table(
    species_common: str,
    species_std: str,
    yield_tables_dir: Optional[Path] = None,
    calibration_species: Optional[Dict[str, Dict[str, Any]]] = None,
    yield_search: str = "",
    store_dir: Optional[Path] = None,
    preferred_site_index: Optional[float] = None,
    preferred_region: str = "",
) -> Optional[YieldTableData]:
    """Resolve the best yield table for a species.

    Priority:
        1. Local CSV in yield_tables_dir (by standardized name)
        2. TOML override (explicit table_id + yield_class)
        3. Ingested store (provider-generated CSVs)
        4. openyieldtables auto-discovery (via Yield Search term)

    Args:
        species_common: Common name (e.g., "Norway spruce").
        species_std: Standardized name (e.g., "norway_spruce").
        yield_tables_dir: Path to local yield table CSVs.
        calibration_species: Config overrides (table_id, yield_class, site_index).
        yield_search: Search term for openyieldtables auto-discovery.
        store_dir: Path to the ingested yield table store.
        preferred_site_index: Preferred site index for store selection.
        preferred_region: Preferred region for store selection.

    Returns:
        YieldTableData or None.
    """
    if calibration_species is None:
        calibration_species = {}

    # 1. Try local CSV
    if yield_tables_dir and yield_tables_dir.exists():
        local = load_local_yield_table(species_std, yield_tables_dir)
        if local:
            logger.info("  Using local yield table: %s", local.title)
            return local

    # 2. Try config override
    cfg = calibration_species.get(species_common, {})
    tid = cfg.get("table_id")
    yc = cfg.get("yield_class")
    if tid and yc:
        result = load_openyieldtables(tid, yc)
        if result:
            logger.info("  Using config override: table %d, YC %s", tid, yc)
            return result

    # 3. Try ingested store
    si = cfg.get("site_index", preferred_site_index)
    if store_dir and store_dir.exists():
        store_result = load_store_yield_table(
            species_std, store_dir, si, preferred_region
        )
        if store_result:
            logger.info("  Using store yield table: %s", store_result.title)
            return store_result

    # 4. Auto-discover from openyieldtables
    if yield_search:
        discovered = auto_discover_yield_table(species_common, yield_search)
        if discovered:
            result = load_openyieldtables(
                discovered["table_id"], discovered["yield_class"]
            )
            if result:
                logger.info(
                    "  Auto-discovered: %s (table %d, YC %s)",
                    result.title, discovered["table_id"], discovered["yield_class"],
                )
                return result

    return None
