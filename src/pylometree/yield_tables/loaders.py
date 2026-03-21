"""Yield table loading functions.

Supports loading from local CSV files, the ingested store, and the
openyieldtables.org API.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from pylometree.yield_tables.schema import YieldTableData
from pylometree.yield_tables.store import StoreManifest, select_best_table

logger = logging.getLogger(__name__)


def load_local_yield_table(
    species_std: str, yield_tables_dir: Path
) -> Optional[YieldTableData]:
    """Load a yield table from a local CSV file.

    Args:
        species_std: Standardized species name (e.g., "norway_spruce").
        yield_tables_dir: Directory containing yield table CSVs.

    Returns:
        YieldTableData if found, None otherwise.
    """
    csv_path = yield_tables_dir / f"{species_std}.csv"
    if not csv_path.exists():
        return None

    df = pd.read_csv(csv_path)
    required = {"age", "height", "dbh"}
    if not required.issubset(df.columns):
        logger.error(
            "Local yield table %s missing columns: %s (has: %s)",
            csv_path, required - set(df.columns), list(df.columns),
        )
        return None

    df = df.sort_values("age").reset_index(drop=True)

    return YieldTableData(
        ages=df["age"].tolist(),
        heights=df["height"].tolist(),
        dbhs=[d / 100.0 for d in df["dbh"].tolist()],
        title=f"Local: {csv_path.name}",
        source="local",
    )


def load_openyieldtables(
    table_id: int, yield_class: float
) -> Optional[YieldTableData]:
    """Load a yield table from the openyieldtables.org API.

    Args:
        table_id: Yield table ID from openyieldtables.org.
        yield_class: Yield class to select.

    Returns:
        YieldTableData if found, None otherwise.
    """
    from openyieldtables.yieldtables import get_yield_table

    table = get_yield_table(table_id)

    for yc in table.data.yield_classes:
        if float(yc.yield_class) != float(yield_class):
            continue
        ages, heights, dbhs = [], [], []
        for row in yc.rows:
            if row.dominant_height is not None:
                ages.append(row.age)
                heights.append(row.dominant_height)
                dbhs.append(row.dbh / 100.0 if row.dbh else 0.0)

        return YieldTableData(
            ages=ages,
            heights=heights,
            dbhs=dbhs,
            title=table.title,
            source="openyieldtables",
            yield_class=yield_class,
            table_id=table_id,
        )

    logger.error(
        "Yield class %s not found in table %d (%s)",
        yield_class, table_id, table.title,
    )
    return None


def auto_discover_yield_table(
    species_name: str, search_term: str
) -> Optional[Dict[str, Any]]:
    """Auto-discover the best yield table from openyieldtables.org.

    Returns:
        {"table_id": int, "yield_class": float} or None.
    """
    from openyieldtables.yieldtables import get_yield_table, get_yield_tables_meta

    meta = get_yield_tables_meta()
    term = search_term.lower()
    matches = [t for t in meta if term in t.title.lower()]
    if not matches:
        return None

    table_meta = matches[0]
    table = get_yield_table(table_meta.id)

    yc_values = []
    for yc in table.data.yield_classes:
        has_data = any(row.dominant_height is not None for row in yc.rows)
        if has_data:
            yc_values.append(float(yc.yield_class))

    if not yc_values:
        return None

    yc_values.sort()
    middle_yc = yc_values[len(yc_values) // 2]

    return {"table_id": table_meta.id, "yield_class": middle_yc}


def load_store_yield_table(
    species_std: str,
    store_dir: Path,
    preferred_site_index: Optional[float] = None,
    preferred_region: str = "",
    preferred_h50: Optional[float] = None,
) -> Optional[YieldTableData]:
    """Load a yield table from the ingested store.

    Reads the manifest CSV to find tables for this species, selects the best
    match, then loads the corresponding CSV.
    """
    manifest_path = store_dir / "manifest.csv"
    if not manifest_path.exists():
        return None

    manifest = StoreManifest.load(manifest_path)
    tables = manifest.find_tables_for_species(species_std)
    if not tables:
        return None

    best = select_best_table(
        tables, preferred_region, preferred_site_index, preferred_h50
    )
    if not best:
        return None

    csv_path = store_dir / best["filename"]
    if not csv_path.exists():
        logger.warning("Store manifest references missing file: %s", csv_path)
        return None

    df = pd.read_csv(csv_path)
    if not {"age", "height", "dbh"}.issubset(df.columns):
        logger.error("Store CSV missing required columns: %s", csv_path)
        return None

    df = df.sort_values("age").reset_index(drop=True)
    first = df.iloc[0]

    h50_val = best.get("h50")

    return YieldTableData(
        ages=df["age"].tolist(),
        heights=df["height"].tolist(),
        dbhs=[d / 100.0 for d in df["dbh"].tolist()],
        title=f"Store: {csv_path.name}",
        source=str(first.get("source", "store")),
        site_index=float(first.get("site_index", 0)),
        species_latin=str(first.get("species_latin", "")),
        region=str(first.get("region", "")),
        management=str(first.get("management", "")),
        h50=float(h50_val) if h50_val is not None else None,
    )
