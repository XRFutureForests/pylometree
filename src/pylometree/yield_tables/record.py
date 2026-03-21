"""Normalized yield table record for CSV export."""

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import pandas as pd


@dataclass
class YieldTableRecord:
    """A single normalized yield table ready for CSV export.

    Heights are in meters. DBHs are in centimeters (matching the convention
    where loaders divide by 100 when creating YieldTableData).
    Volumes are in m3/ha (optional).
    """

    species_latin: str
    species_common: str
    standardized_name: str
    region: str
    management: str
    site_index: float
    source: str
    table_id: str
    ages: List[float]
    heights: List[float]
    dbhs: List[float]
    volumes: List[float] = field(default_factory=list)

    def filename(self) -> str:
        """Generate a canonical filename for this table."""
        si = f"si{self.site_index:.0f}" if self.site_index else "si0"
        region = self.region.replace("-", "").replace(" ", "_").lower()
        return (
            f"{self.standardized_name}_{region}_{si}_{self.management}.csv"
        )

    def to_dataframe(self) -> pd.DataFrame:
        """Convert to a pandas DataFrame with the normalized schema."""
        n = len(self.ages)
        df = pd.DataFrame(
            {
                "age": self.ages,
                "height": self.heights,
                "dbh": self.dbhs,
                "species_latin": [self.species_latin] * n,
                "region": [self.region] * n,
                "management": [self.management] * n,
                "site_index": [self.site_index] * n,
                "source": [self.source] * n,
                "table_id": [self.table_id] * n,
            }
        )
        if self.volumes:
            df["volume"] = self.volumes[:n]
        return df

    def to_csv(self, path: Path) -> Path:
        """Write this table as a CSV file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        self.to_dataframe().to_csv(path, index=False)
        return path

    @staticmethod
    def from_csv(path: Path) -> "YieldTableRecord":
        """Read a normalized CSV back into a record."""
        df = pd.read_csv(path)
        first = df.iloc[0]
        return YieldTableRecord(
            species_latin=str(first.get("species_latin", "")),
            species_common="",
            standardized_name="",
            region=str(first.get("region", "")),
            management=str(first.get("management", "")),
            site_index=float(first.get("site_index", 0)),
            source=str(first.get("source", "")),
            table_id=str(first.get("table_id", "")),
            ages=df["age"].tolist(),
            heights=df["height"].tolist(),
            dbhs=df["dbh"].tolist(),
            volumes=df["volume"].tolist() if "volume" in df.columns else [],
        )

    def validate(self) -> List[str]:
        """Basic quality checks. Returns list of issues (empty = OK)."""
        issues: List[str] = []
        if not self.standardized_name:
            issues.append("empty standardized_name (species not in mapping)")
        if len(self.ages) < 2:
            issues.append("fewer than 2 age entries")
        if len(self.ages) != len(self.heights):
            issues.append("ages and heights have different lengths")
        if len(self.ages) != len(self.dbhs):
            issues.append("ages and dbhs have different lengths")
        if self.ages and list(self.ages) != sorted(self.ages):
            issues.append("ages not monotonically increasing")
        if self.heights and any(h < 0 for h in self.heights):
            issues.append("negative height values")
        if self.dbhs and any(d < 0 for d in self.dbhs):
            issues.append("negative DBH values")
        return issues
