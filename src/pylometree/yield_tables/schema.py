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
    h50: Optional[float] = None
    # Set when this table was resolved through SPECIES_PROXIES rather than for
    # the species actually asked for -- holds that requested standardized name.
    # Without it a proxied table is indistinguishable from a real one
    # downstream, and a caller can silently publish another species' curve.
    proxy_for: str = ""
