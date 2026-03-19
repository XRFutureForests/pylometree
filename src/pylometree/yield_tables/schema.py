"""Resolved yield table data container."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class YieldTableData:
    """Resolved yield table data for a single species and yield class."""

    ages: List[float]
    heights: List[float]
    dbhs: List[float]
    title: str
    source: str
    yield_class: Optional[float] = None
    table_id: Optional[int] = None
    species_latin: str = ""
    region: str = ""
    management: str = ""
    site_index: Optional[float] = None
