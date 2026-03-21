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
    # 1. Try local CSV
    if yield_tables_dir and yield_tables_dir.exists():
        local = load_local_yield_table(species_std, yield_tables_dir)
        if local:
            logger.info("  Using local yield table: %s", local.title)
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
            logger.info("  Using store yield table: %s", store_result.title)
            return store_result

    logger.info("  No yield table found for %s", species_common)
    return None
