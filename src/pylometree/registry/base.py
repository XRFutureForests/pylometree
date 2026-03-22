"""Model registry – stores and retrieves published allometric equations.

Design principles
-----------------
* Inspired by the R ``allometric`` package's tibble-of-models pattern but
  adapted for Python: each entry is a ``ModelEntry`` dataclass; the registry
  is a filtered, searchable collection.
* Models are callable ( ``entry(dbh=20)`` ) via a stored function reference.
* Variable naming follows allometric's convention where relevant:
    ``dsob``  – diameter outside bark at breast height (cm)
    ``hst``   – total stem height (m)
    ``vsia``  – stem volume inside bark (m³)
    ``agb``   – above-ground biomass (kg)
    ``bgb``   – below-ground biomass (kg)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

import numpy as np

# ---------------------------------------------------------------------------
# ModelEntry
# ---------------------------------------------------------------------------


@dataclass
class ModelEntry:
    """A single published allometric model with associated metadata.

    Attributes
    ----------
    model_id : str
        Unique identifier (e.g. ``"chave2014_pantropical"``).
    model_type : str
        Category: ``"hd"`` | ``"agb"`` | ``"bgb"`` | ``"volume"`` |
        ``"crown_agb"`` | ``"crown_dbh"`` | ``"age_height"``.
    equation_form : str
        Human-readable equation string (e.g. ``"agb = a*(rho*dbh**2*h)**b"``).
    response : str
        Name of the response variable (allometric variable name).
    covariates : list[str]
        Names of the predictor variables (allometric variable names).
    parameters : dict[str, float]
        Fitted parameter values keyed by parameter name.
    fn : Callable
        Python function implementing the equation.  Signature must accept
        keyword arguments matching ``covariates`` plus ``**params``.
    species : list[str]
        List of species or genera to which the equation applies.
        Empty list means equation is generic / pan-tropical.
    region : list[str]
        Geographic regions (e.g. ``["pantropical"]``, ``["temperate_europe"]``).
    reference : str
        Full citation string.
    pub_year : int | None
        Year of publication.
    units : dict[str, str]
        Units of response and covariate variables (keyed by variable name).
    notes : str
        Additional remarks (sample size, applicability limits, etc.).
    """

    model_id: str
    model_type: str
    equation_form: str
    response: str
    covariates: list[str]
    parameters: dict[str, float]
    fn: Callable
    species: list[str] = field(default_factory=list)
    region: list[str] = field(default_factory=list)
    reference: str = ""
    pub_year: Optional[int] = None
    units: dict[str, str] = field(default_factory=dict)
    notes: str = ""

    # ------------------------------------------------------------------
    # Prediction interface
    # ------------------------------------------------------------------

    def predict(self, **covt_values: float) -> float:
        """Predict the response for given covariate values.

        Parameters
        ----------
        **covt_values
            Keyword arguments whose names match ``self.covariates``.

        Returns
        -------
        float
            Predicted value in the units given by ``self.units[self.response]``.

        Examples
        --------
        >>> entry.predict(dsob=20.0, hst=18.0)
        """
        missing = set(self.covariates) - set(covt_values)
        if missing:
            raise ValueError(f"Missing covariate(s): {missing}")
        return self.fn(
            **{k: covt_values[k] for k in self.covariates}, **self.parameters
        )

    def __call__(self, **covt_values: float) -> float:
        return self.predict(**covt_values)

    def __repr__(self) -> str:
        sp = (
            (", ".join(self.species[:2]) + ("…" if len(self.species) > 2 else ""))
            if self.species
            else "generic"
        )
        return (
            f"ModelEntry(id={self.model_id!r}, type={self.model_type!r}, "
            f"species={sp!r}, ref={self.pub_year})"
        )

    # ------------------------------------------------------------------
    # Serialisation (parameters only – fn cannot be JSON-serialised)
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "model_id": self.model_id,
            "model_type": self.model_type,
            "equation_form": self.equation_form,
            "response": self.response,
            "covariates": self.covariates,
            "parameters": self.parameters,
            "species": self.species,
            "region": self.region,
            "reference": self.reference,
            "pub_year": self.pub_year,
            "units": self.units,
            "notes": self.notes,
        }


# ---------------------------------------------------------------------------
# ModelRegistry
# ---------------------------------------------------------------------------


class ModelRegistry:
    """A searchable collection of ``ModelEntry`` objects.

    Usage
    -----
    >>> from pylometree.registry import registry
    >>> models = registry.query(model_type="agb", region="pantropical")
    >>> chave = registry.get("chave2014_pantropical")
    >>> chave.predict(dsob=25.0, hst=22.0, rho=0.60)
    """

    def __init__(self) -> None:
        self._entries: dict[str, ModelEntry] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, entry: ModelEntry) -> None:
        """Add a ``ModelEntry`` to the registry."""
        self._entries[entry.model_id] = entry

    def register_many(self, entries: list[ModelEntry]) -> None:
        for e in entries:
            self.register(e)

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def get(self, model_id: str) -> ModelEntry:
        """Retrieve a model by its unique ID."""
        try:
            return self._entries[model_id]
        except KeyError:
            raise KeyError(f"No model registered with id={model_id!r}") from None

    def query(
        self,
        *,
        model_type: Optional[str] = None,
        species: Optional[str] = None,
        region: Optional[str] = None,
        response: Optional[str] = None,
        pub_year_min: Optional[int] = None,
    ) -> list[ModelEntry]:
        """Filter registry entries.

        All provided filters are applied with AND logic.  String matches are
        case-insensitive substring checks.

        Parameters
        ----------
        model_type : str, optional
            E.g. ``"agb"``, ``"hd"``, ``"volume"``.
        species : str, optional
            Genus or species name (partial match against ``entry.species``).
        region : str, optional
            Geographic region (partial match against ``entry.region``).
        response : str, optional
            Response variable name.
        pub_year_min : int, optional
            Only return models published >= this year.
        """
        results = list(self._entries.values())
        if model_type is not None:
            mt = model_type.lower()
            results = [e for e in results if e.model_type.lower() == mt]
        if species is not None:
            sp = species.lower()
            results = [
                e
                for e in results
                if not e.species or any(sp in s.lower() for s in e.species)
            ]
        if region is not None:
            reg = region.lower()
            results = [
                e
                for e in results
                if not e.region or any(reg in r.lower() for r in e.region)
            ]
        if response is not None:
            rv = response.lower()
            results = [e for e in results if rv in e.response.lower()]
        if pub_year_min is not None:
            results = [
                e for e in results if e.pub_year is None or e.pub_year >= pub_year_min
            ]
        return results

    def list_ids(self) -> list[str]:
        return sorted(self._entries.keys())

    def summary(self) -> dict[str, Any]:
        """Return a summary dict of all registered models."""
        types: dict[str, int] = {}
        for e in self._entries.values():
            types[e.model_type] = types.get(e.model_type, 0) + 1
        return {"total": len(self._entries), "by_type": types}

    def summary_df(self):
        """Return a pandas DataFrame summarising all registered models.

        Requires ``pandas`` to be installed.
        """
        try:
            import pandas as pd
        except ImportError as exc:
            raise ImportError("pandas is required for summary_df.") from exc

        records = []
        for e in self._entries.values():
            records.append(
                {
                    "model_id": e.model_id,
                    "model_type": e.model_type,
                    "response": e.response,
                    "covariates": e.covariates,
                    "species": e.species,
                    "region": e.region,
                    "pub_year": e.pub_year,
                    "reference": e.reference,
                }
            )
        return pd.DataFrame(records)

    def __call__(self, model_id: str, **covt_values: float) -> float:
        """Shortcut: ``registry("id", dsob=30)`` ≡ ``registry.get("id").predict(dsob=30)``."""
        return self.get(model_id).predict(**covt_values)

    def __len__(self) -> int:
        return len(self._entries)

    def __repr__(self) -> str:
        return f"ModelRegistry({len(self)} entries)"


# ---------------------------------------------------------------------------
# Module-level singleton – populated by the models subpackages on import
# ---------------------------------------------------------------------------

registry = ModelRegistry()
