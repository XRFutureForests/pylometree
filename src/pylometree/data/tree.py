"""Tree dataclass – a single measured or predicted tree."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Tree:
    """Represents a single tree with common dendrometric attributes.

    Attributes
    ----------
    dbh : float
        Diameter at breast height (cm), outside bark at 1.30 m.
        Use ``None`` when unknown and to be predicted.
    height : float | None
        Total tree height (m).  ``None`` when unknown.
    crown_area : float | None
        Projected crown area (m²).  ``None`` when not measured.
    crown_height : float | None
        Crown height = total height – crown base height (m).
    wood_density : float | None
        Oven-dry wood density (g cm⁻³).  ``None`` → biome default used.
    species : str | None
        Scientific or common name of the species.
    genus : str | None
        Genus (for registry look-ups when full species name is unavailable).
    family : str | None
        Plant family (for coarse look-ups).
    region : str | None
        Broad geographic region (e.g. ``"tropical_moist"``, ``"boreal"``).
    age : float | None
        Stand or tree age (years).  ``None`` when unknown.
    agb : float | None
        Above-ground biomass (kg dry mass).  ``None`` when unknown.
    bgb : float | None
        Below-ground biomass (kg dry mass).  ``None`` when unknown.
    notes : dict
        Free-form key-value metadata (plot ID, measurement date, …).
    """

    dbh: Optional[float] = None
    height: Optional[float] = None
    crown_area: Optional[float] = None
    crown_height: Optional[float] = None
    wood_density: Optional[float] = None
    species: Optional[str] = None
    genus: Optional[str] = None
    family: Optional[str] = None
    region: Optional[str] = None
    age: Optional[float] = None
    agb: Optional[float] = None
    bgb: Optional[float] = None
    notes: dict = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Derived properties
    # ------------------------------------------------------------------

    @property
    def basal_area(self) -> Optional[float]:
        """Single-tree basal area (m²)."""
        if self.dbh is None:
            return None
        import math

        return math.pi * (self.dbh / 200.0) ** 2  # DBH in cm → radius in m

    @property
    def d2h(self) -> Optional[float]:
        """DBH² × height (cm² m), a common biomass predictor."""
        if self.dbh is None or self.height is None:
            return None
        return self.dbh**2 * self.height

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        sp = self.species or "sp."
        dbh_str = f"{self.dbh:.1f} cm" if self.dbh is not None else "DBH=?"
        h_str = f"{self.height:.1f} m" if self.height is not None else "H=?"
        return f"Tree({sp}, {dbh_str}, {h_str})"
