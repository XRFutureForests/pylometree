"""Store manifest for ingested yield tables."""

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


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
        "source",
        "table_id",
        "n_rows",
    ]

    def add(self, record: "YieldTableRecord", filename: str) -> None:
        from pylometree.yield_tables.record import YieldTableRecord  # noqa: F811

        self.entries.append(
            {
                "filename": filename,
                "standardized_name": record.standardized_name,
                "species_latin": record.species_latin,
                "region": record.region,
                "management": record.management,
                "site_index": record.site_index,
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
) -> Optional[Dict[str, Any]]:
    """Pick the best table from a list of manifest entries.

    Selection logic:
        1. Filter by preferred_region if given.
        2. Pick by preferred_site_index if given, else pick middle site index.
    """
    if not tables:
        return None

    candidates = tables
    if preferred_region:
        region_match = [
            t for t in candidates
            if t.get("region", "").lower() == preferred_region.lower()
        ]
        if region_match:
            candidates = region_match

    if preferred_site_index is not None:
        candidates.sort(
            key=lambda t: abs(float(t.get("site_index", 0)) - preferred_site_index)
        )
        return candidates[0]

    candidates.sort(key=lambda t: float(t.get("site_index", 0)))
    return candidates[len(candidates) // 2]
