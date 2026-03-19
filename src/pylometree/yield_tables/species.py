"""Generic species name registry for yield table resolution.

Maps Latin (scientific) names to common names and standardized identifiers.
Ships a bundled default CSV covering Central European and North American
species. Projects can supply their own CSV or extend the mapping.
"""

import importlib.resources
import logging
from pathlib import Path
from typing import Dict, Optional

import pandas as pd

logger = logging.getLogger(__name__)


class SpeciesMapping:
    """Latin name -> common name + standardized name mapping.

    The mapping dict is keyed by lowercase Latin name with values:
    {"common_name": ..., "standardized_name": ..., "yield_search": ...}
    """

    def __init__(self, mapping: Dict[str, Dict[str, str]]):
        self._mapping = mapping

    def get(self, latin_name: str) -> Dict[str, str]:
        return self._mapping.get(latin_name.lower().strip(), {})

    def common_name(self, latin_name: str) -> str:
        return self.get(latin_name).get("common_name", "")

    def standardized_name(self, latin_name: str) -> str:
        return self.get(latin_name).get("standardized_name", "")

    def yield_search(self, latin_name: str) -> str:
        return self.get(latin_name).get("yield_search", "")

    def as_dict(self) -> Dict[str, Dict[str, str]]:
        return dict(self._mapping)

    def __len__(self) -> int:
        return len(self._mapping)

    def __contains__(self, latin_name: str) -> bool:
        return latin_name.lower().strip() in self._mapping

    @classmethod
    def from_csv(cls, path: Path) -> "SpeciesMapping":
        """Load species mapping from a CSV file.

        Expected columns: Scientific Name, Common Name, Standardized Name
        Optional column: Yield Search
        """
        df = pd.read_csv(path)
        return cls._from_dataframe(df)

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame) -> "SpeciesMapping":
        return cls._from_dataframe(df)

    @classmethod
    def _from_dataframe(cls, df: pd.DataFrame) -> "SpeciesMapping":
        mapping: Dict[str, Dict[str, str]] = {}
        for _, row in df.iterrows():
            latin = str(row.get("Scientific Name", "")).strip()
            if not latin:
                continue
            mapping[latin.lower()] = {
                "common_name": str(row.get("Common Name", "")).strip(),
                "standardized_name": str(row.get("Standardized Name", "")).strip(),
                "yield_search": str(row.get("Yield Search", "")).strip(),
            }
        return cls(mapping)


def _bundled_species_csv() -> Path:
    """Return path to the bundled species.csv shipped with pylometree."""
    ref = importlib.resources.files("pylometree.yield_tables") / "data" / "species.csv"
    # For editable installs, ref is already a Path. For installed packages,
    # we need as_file() but try the simple path first.
    p = Path(str(ref))
    if p.exists():
        return p
    return ref  # type: ignore[return-value]


def load_species_mapping(source: Optional[Path] = None) -> SpeciesMapping:
    """Load a species mapping from CSV.

    Args:
        source: Path to a CSV file with species data. If None, loads the
            bundled default that ships with pylometree.

    Returns:
        SpeciesMapping instance.
    """
    if source is not None:
        if not source.exists():
            logger.error("Species mapping CSV not found: %s", source)
            return SpeciesMapping({})
        return SpeciesMapping.from_csv(source)

    csv_path = _bundled_species_csv()
    if not Path(str(csv_path)).exists():
        logger.warning("Bundled species.csv not found; returning empty mapping")
        return SpeciesMapping({})
    return SpeciesMapping.from_csv(Path(str(csv_path)))
