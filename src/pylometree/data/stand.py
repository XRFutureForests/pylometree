"""Stand dataclass – a collection of trees in a defined plot."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from pylometree.data.tree import Tree


@dataclass
class Stand:
    """A fixed-area forest plot containing one or more trees.

    Parameters
    ----------
    trees : list[Tree]
        Individual tree records measured in the plot.
    plot_area : float
        Plot area in hectares.  Used to scale per-tree metrics to per-ha.
    name : str | None
        Optional label for the stand (plot ID, site name, …).

    Notes
    -----
    All ``per_ha`` properties raise ``ValueError`` when ``plot_area`` is
    not set (``None``).
    """

    trees: list[Tree] = field(default_factory=list)
    plot_area: Optional[float] = None  # ha
    name: Optional[str] = None

    # ------------------------------------------------------------------
    # Basic queries
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self.trees)

    def __iter__(self):
        return iter(self.trees)

    def __repr__(self) -> str:
        area_str = f"{self.plot_area} ha" if self.plot_area else "area=?"
        return f"Stand(n={len(self.trees)}, {area_str})"

    # ------------------------------------------------------------------
    # Stand-level metrics
    # ------------------------------------------------------------------

    @property
    def basal_area(self) -> float:
        """Total basal area of all trees in the plot (m²)."""
        return sum(t.basal_area for t in self.trees if t.basal_area is not None)

    @property
    def basal_area_per_ha(self) -> float:
        """Basal area per hectare (m² ha⁻¹)."""
        self._require_area()
        return self.basal_area / self.plot_area  # type: ignore[operator]

    @property
    def density_per_ha(self) -> float:
        """Number of stems per hectare."""
        self._require_area()
        return len(self.trees) / self.plot_area  # type: ignore[operator]

    @property
    def mean_dbh(self) -> Optional[float]:
        """Arithmetic mean DBH of all trees with a measured diameter (cm)."""
        vals = [t.dbh for t in self.trees if t.dbh is not None]
        return float(np.mean(vals)) if vals else None

    @property
    def qmd(self) -> Optional[float]:
        """Quadratic mean diameter (cm).

        QMD = sqrt( Σ DBH² / N )
        """
        vals = [t.dbh for t in self.trees if t.dbh is not None]
        if not vals:
            return None
        return float(math.sqrt(np.mean(np.square(vals))))

    @property
    def mean_height(self) -> Optional[float]:
        """Arithmetic mean height of all trees with a measured height (m)."""
        vals = [t.height for t in self.trees if t.height is not None]
        return float(np.mean(vals)) if vals else None

    @property
    def agb_total(self) -> float:
        """Sum of individual-tree AGB values in the plot (kg dry mass)."""
        return sum(t.agb for t in self.trees if t.agb is not None)

    @property
    def agb_per_ha(self) -> float:
        """AGB per hectare (Mg ha⁻¹, i.e. t ha⁻¹)."""
        self._require_area()
        return self.agb_total / self.plot_area / 1000  # kg → Mg, per ha

    @property
    def carbon_stock_per_ha(self) -> float:
        """Carbon stock per hectare (Mg C ha⁻¹) using 0.47 carbon fraction."""
        from pylometree.data.constants import CARBON_FRACTION

        return self.agb_per_ha * CARBON_FRACTION

    # --- Convenience aliases (match README / common forestry shorthand) ---

    @property
    def plot_area_ha(self) -> Optional[float]:
        """Alias for ``plot_area`` (hectares)."""
        return self.plot_area

    @plot_area_ha.setter
    def plot_area_ha(self, value: Optional[float]) -> None:
        self.plot_area = value

    @property
    def agb_mg_ha(self) -> float:
        """Alias for ``agb_per_ha`` (Mg ha⁻¹)."""
        return self.agb_per_ha

    @property
    def carbon_stock_mg_ha(self) -> float:
        """Alias for ``carbon_stock_per_ha`` (Mg C ha⁻¹)."""
        return self.carbon_stock_per_ha

    def summary_df(self):
        """Per-tree summary as a pandas DataFrame.

        Requires ``pandas`` to be installed.
        """
        try:
            import pandas as pd
        except ImportError as exc:
            raise ImportError("pandas is required for summary_df.") from exc

        records = []
        for t in self.trees:
            records.append(
                {
                    "species": t.species,
                    "dbh": t.dbh,
                    "height": t.height,
                    "basal_area": t.basal_area,
                    "agb": t.agb,
                    "crown_area": t.crown_area,
                    "wood_density": t.wood_density,
                }
            )
        return pd.DataFrame(records)

    # ------------------------------------------------------------------
    # Stand Density Index  (Reineke 1933)
    # ------------------------------------------------------------------

    def reineke_sdi(self, reference_dbh: float = 25.0) -> Optional[float]:
        """Stand Density Index after Reineke (1933).

        SDI = N × (QMD / reference_dbh)^1.605

        Parameters
        ----------
        reference_dbh : float
            Reference diameter in cm (default 25 cm).
        """
        qmd = self.qmd
        if qmd is None:
            return None
        self._require_area()
        n_per_ha = self.density_per_ha
        return float(n_per_ha * (qmd / reference_dbh) ** 1.605)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _require_area(self) -> None:
        if self.plot_area is None:
            raise ValueError("plot_area must be set to compute per-ha metrics.")

    @classmethod
    def from_dataframe(
        cls,
        df,
        dbh_col: str = "dbh",
        height_col: str = "height",
        species_col: Optional[str] = "species",
        plot_area: Optional[float] = None,
        **kwargs,
    ) -> "Stand":
        """Construct a Stand from a pandas DataFrame.

        Parameters
        ----------
        df : pandas.DataFrame
        dbh_col, height_col, species_col : str
            Column names in *df* for DBH (cm), height (m), and species.
        plot_area : float | None
            Plot area in hectares.
        **kwargs
            Extra column → Tree-attribute mappings, e.g. ``crown_area="ca"``.
        """
        trees = []
        extra_cols = {attr: col for attr, col in kwargs.items()}
        for _, row in df.iterrows():
            kw: dict = {}
            kw["dbh"] = row[dbh_col] if dbh_col in df.columns else None
            kw["height"] = row[height_col] if height_col in df.columns else None
            if species_col and species_col in df.columns:
                kw["species"] = str(row[species_col])
            for attr, col in extra_cols.items():
                if col in df.columns:
                    kw[attr] = row[col]
            trees.append(Tree(**kw))
        return cls(trees=trees, plot_area=plot_area)
