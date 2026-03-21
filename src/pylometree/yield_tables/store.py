"""Store manifest for ingested yield tables."""

import csv
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)

REFERENCE_AGE = 50
"""Standard reference age (years) for computing the normalized site index h50."""


def compute_h50(
    ages: List[float],
    heights: List[float],
    reference_age: float = REFERENCE_AGE,
) -> Optional[float]:
    """Compute the dominant height at a reference age (default 50 years).

    Uses PCHIP monotone interpolation when the reference age falls within the
    table's age range.  Returns None when the table does not span the
    reference age or contains fewer than 3 data points.
    """
    if len(ages) < 3 or len(heights) < 3:
        return None

    a = np.asarray(ages, dtype=float)
    h = np.asarray(heights, dtype=float)

    if reference_age < a.min() or reference_age > a.max():
        return None

    from scipy.interpolate import PchipInterpolator

    interp = PchipInterpolator(a, h)
    return round(float(interp(reference_age)), 2)


@dataclass
class StoreManifest:
    """Registry of all ingested yield tables in the store directory."""

    entries: List[Dict[str, Any]] = field(default_factory=list)

    COLUMNS = [
        "filename",
        "standardized_name",
        "species_latin",
        "region",
        "management",
        "site_index",
        "h50",
        "source",
        "table_id",
        "n_rows",
    ]

    def add(self, record: "YieldTableRecord", filename: str) -> None:
        from pylometree.yield_tables.record import YieldTableRecord  # noqa: F811

        h50 = compute_h50(record.ages, record.heights)
        self.entries.append(
            {
                "filename": filename,
                "standardized_name": record.standardized_name,
                "species_latin": record.species_latin,
                "region": record.region,
                "management": record.management,
                "site_index": record.site_index,
                "h50": h50 if h50 is not None else "",
                "source": record.source,
                "table_id": record.table_id,
                "n_rows": len(record.ages),
            }
        )

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.COLUMNS)
            writer.writeheader()
            for entry in self.entries:
                writer.writerow(entry)

    @classmethod
    def load(cls, path: Path) -> "StoreManifest":
        if not path.exists():
            return cls()
        manifest = cls()
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if "site_index" in row:
                    row["site_index"] = float(row["site_index"])
                if "n_rows" in row:
                    row["n_rows"] = int(row["n_rows"])
                if "h50" in row and row["h50"] not in ("", None):
                    row["h50"] = float(row["h50"])
                else:
                    row["h50"] = None
                manifest.entries.append(row)
        return manifest

    def find_tables_for_species(
        self, standardized_name: str
    ) -> List[Dict[str, Any]]:
        return [
            e for e in self.entries
            if e.get("standardized_name") == standardized_name
        ]


def select_best_table(
    tables: List[Dict[str, Any]],
    preferred_region: Optional[str] = None,
    preferred_site_index: Optional[float] = None,
    preferred_h50: Optional[float] = None,
) -> Optional[Dict[str, Any]]:
    """Pick the best table from a list of manifest entries.

    Selection logic:
        1. Filter by preferred_region if given.
        2. If preferred_h50 given, pick table with closest h50 value.
        3. Else if preferred_site_index given, pick closest site_index.
        4. Else pick median by h50 (falling back to median by site_index).
    """
    if not tables:
        return None

    candidates = list(tables)
    if preferred_region:
        region_match = [
            t for t in candidates
            if t.get("region", "").lower() == preferred_region.lower()
        ]
        if region_match:
            candidates = region_match

    # Prefer h50-based selection (source-independent metric)
    if preferred_h50 is not None:
        with_h50 = [t for t in candidates if t.get("h50") is not None]
        if with_h50:
            with_h50.sort(key=lambda t: abs(float(t["h50"]) - preferred_h50))
            best = with_h50[0]
            logger.debug(
                "  Selected table by h50: %.1f m (target %.1f m): %s",
                float(best["h50"]),
                preferred_h50,
                best.get("filename", "?"),
            )
            return best

    if preferred_site_index is not None:
        candidates.sort(
            key=lambda t: abs(float(t.get("site_index", 0)) - preferred_site_index)
        )
        return candidates[0]

    # Default: pick median by h50, falling back to site_index
    with_h50 = [t for t in candidates if t.get("h50") is not None]
    if with_h50:
        with_h50.sort(key=lambda t: float(t["h50"]))
        return with_h50[len(with_h50) // 2]

    candidates.sort(key=lambda t: float(t.get("site_index", 0)))
    return candidates[len(candidates) // 2]
