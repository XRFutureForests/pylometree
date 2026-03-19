"""I/O utilities – load tree data from CSV or pandas DataFrames."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np

from pylometree.data.stand import Stand
from pylometree.data.tree import Tree


def read_csv(
    filepath: str | Path,
    dbh_col: str = "dbh",
    height_col: str = "height",
    species_col: Optional[str] = "species",
    plot_area: Optional[float] = None,
    **extra_cols,
) -> Stand:
    """Read a CSV file into a :class:`~pylometree.data.Stand`.

    Parameters
    ----------
    filepath : str | Path
        Path to the CSV file.
    dbh_col, height_col, species_col : str
        Column names for DBH (cm), height (m), and species name.
    plot_area : float | None
        Plot area in hectares.
    **extra_cols
        Additional ``Tree`` attribute → CSV column name mappings,
        e.g. ``crown_area="ca_m2"``.

    Returns
    -------
    Stand
    """
    import csv

    filepath = Path(filepath)
    trees: list[Tree] = []
    with filepath.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            kw: dict = {}
            if dbh_col in (reader.fieldnames or []):
                raw = row[dbh_col].strip()
                kw["dbh"] = float(raw) if raw else None
            if height_col in (reader.fieldnames or []):
                raw = row[height_col].strip()
                kw["height"] = float(raw) if raw else None
            if species_col and species_col in (reader.fieldnames or []):
                kw["species"] = row[species_col].strip() or None
            for attr, col in extra_cols.items():
                if col in (reader.fieldnames or []):
                    raw = row[col].strip()
                    try:
                        kw[attr] = float(raw) if raw else None
                    except ValueError:
                        kw[attr] = raw or None
            trees.append(Tree(**kw))

    return Stand(trees=trees, plot_area=plot_area)


def stand_to_dataframe(stand: Stand):
    """Convert a :class:`~pylometree.data.Stand` to a pandas DataFrame.

    Requires ``pandas`` to be installed.
    """
    try:
        import pandas as pd
    except ImportError as exc:
        raise ImportError("pandas is required for stand_to_dataframe.") from exc

    records = []
    for t in stand.trees:
        records.append(
            {
                "species": t.species,
                "dbh": t.dbh,
                "height": t.height,
                "crown_area": t.crown_area,
                "crown_height": t.crown_height,
                "wood_density": t.wood_density,
                "region": t.region,
                "age": t.age,
                "agb": t.agb,
                "bgb": t.bgb,
            }
        )
    return pd.DataFrame(records)
