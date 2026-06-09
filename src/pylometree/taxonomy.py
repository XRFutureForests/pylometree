"""Taxonomic searching and species management for allometric models.

This module provides taxonomic searching functionality inspired by the allometric R package,
enabling rigorous species and higher taxonomic group searching.

Example:
    >>> from pylometree.taxonomy import Taxon, Taxa, search_by_taxon
    >>> # Create a taxon for a specific species
    >>> douglas_fir = Taxon(family="Pinaceae", genus="Pseudotsuga", species="menziesii")
    >>> # Create taxa for multiple species
    >>> conifers = Taxa([
    ...     Taxon(family="Pinaceae", genus="Pseudotsuga", species="menziesii"),
    ...     Taxon(family="Pinaceae", genus="Pinus", species="ponderosa")
    ... ])
    >>> # Search models by taxon
    >>> models = search_by_taxon(allometric_models, douglas_fir)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Union

import pandas as pd
from pandas import DataFrame


@dataclass(frozen=True)
class Taxon:
    """Represents a single taxonomic classification.

    A Taxon is an immutable object representing a species or higher taxonomic
    group (family, genus, species) with validation to ensure taxonomic integrity.

    Attributes
    ----------
    family : str, optional
        Family name (e.g., "Pinaceae")
    genus : str, optional
        Genus name (e.g., "Pseudotsuga")
    species : str, optional
        Species name (e.g., "menziesii")

    Examples
    --------
    >>> douglas_fir = Taxon(family="Pinaceae", genus="Pseudotsuga", species="menziesii")
    >>> print(douglas_fir)
    Taxon(family='Pinaceae', genus='Pseudotsuga', species='menziesii')
    """

    family: str | None = None
    genus: str | None = None
    species: str | None = None

    def __post_init__(self) -> None:
        """Validate taxon after initialization."""
        # Check that at least one taxonomic level is specified
        if self.family is None and self.genus is None and self.species is None:
            raise ValueError(
                "At least one taxonomic level (family, genus, species) must be specified"
            )

        # Validate that species requires genus, and genus requires family
        if self.species is not None and self.genus is None:
            raise ValueError("Species requires genus to be specified")
        if self.genus is not None and self.family is None:
            raise ValueError("Genus requires family to be specified")

    def __str__(self) -> str:
        """Return string representation."""
        parts = [p for p in [self.family, self.genus, self.species] if p is not None]
        return f"Taxon({', '.join(parts)})"

    def __repr__(self) -> str:
        """Return detailed string representation."""
        return f"Taxon(family={self.family!r}, genus={self.genus!r}, species={self.species!r})"

    def matches(self, other: Taxon) -> bool:
        """Check if this taxon matches another (more specific taxon matches less specific).

        Args:
            other: Another Taxon to compare against

        Returns:
            True if this taxon matches or is more specific than other

        Examples
        --------
        >>> t1 = Taxon(family="Pinaceae")
        >>> t2 = Taxon(family="Pinaceae", genus="Pseudotsuga")
        >>> t1.matches(t2)  # t1 is less specific, matches all of t2
        True
        >>> t2.matches(t1)  # t2 is more specific, doesn't match general t1
        False
        """
        # Check family
        if self.family is not None:
            if other.family is None or self.family != other.family:
                return False

        # Check genus
        if self.genus is not None:
            if other.genus is None or self.genus != other.genus:
                return False

        # Check species
        if self.species is not None:
            if other.species is None or self.species != other.species:
                return False

        return True

    def is_more_specific_than(self, other: Taxon) -> bool:
        """Check if this taxon is more specific than another.

        Args:
            other: Another Taxon to compare against

        Returns:
            True if this taxon has more taxonomic levels specified

        Examples
        --------
        >>> t1 = Taxon(family="Pinaceae")
        >>> t2 = Taxon(family="Pinaceae", genus="Pseudotsuga")
        >>> t2.is_more_specific_than(t1)
        True
        """
        self_levels = sum(
            1 for p in [self.family, self.genus, self.species] if p is not None
        )
        other_levels = sum(
            1 for p in [other.family, other.genus, other.species] if p is not None
        )
        return self_levels > other_levels


@dataclass
class Taxa:
    """Represents a collection of Taxon objects.

    Taxa is a container for multiple taxonomic classifications, enforcing
    uniqueness and providing utility methods for taxonomic operations.

    Attributes
    ----------
    taxa : list[Taxon]
        List of Taxon objects

    Examples
    --------
    >>> taxa = Taxa([
    ...     Taxon(family="Pinaceae", genus="Pseudotsuga", species="menziesii"),
    ...     Taxon(family="Pinaceae", genus="Pinus", species="ponderosa")
    ... ])
    >>> print(len(taxa))
    2
    """

    taxa: list[Taxon] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate taxa after initialization."""
        # Check for duplicate taxa and remove them
        unique_taxa = []
        seen = set()
        for taxon in self.taxa:
            taxon_tuple = (taxon.family, taxon.genus, taxon.species)
            if taxon_tuple not in seen:
                unique_taxa.append(taxon)
                seen.add(taxon_tuple)
        self.taxa = unique_taxa

    def __len__(self) -> int:
        """Return number of taxa."""
        return len(self.taxa)

    def __iter__(self):
        """Iterate over taxa."""
        return iter(self.taxa)

    def __getitem__(self, index):
        """Get taxon by index."""
        return self.taxa[index]

    def __contains__(self, taxon: Taxon) -> bool:
        """Check if a taxon is in this collection."""
        for t in self.taxa:
            if (
                t.family == taxon.family
                and t.genus == taxon.genus
                and t.species == taxon.species
            ):
                return True
        return False

    def add(self, taxon: Taxon) -> None:
        """Add a taxon to the collection.

        Args:
            taxon: Taxon to add
        """
        if taxon not in self:
            self.taxa.append(taxon)

    def to_dict(self) -> list[dict]:
        """Convert to list of dictionaries.

        Returns:
            List of dictionaries with family, genus, species keys
        """
        return [
            {"family": t.family, "genus": t.genus, "species": t.species}
            for t in self.taxa
        ]

    @classmethod
    def from_dict(cls, data: list[dict]) -> Taxa:
        """Create Taxa from list of dictionaries.

        Args:
            data: List of dictionaries with family, genus, species keys

        Returns:
            Taxa instance
        """
        taxa = [
            Taxon(
                family=d.get("family"), genus=d.get("genus"), species=d.get("species")
            )
            for d in data
        ]
        return cls(taxa=taxa)


def search_by_taxon(
    df: DataFrame,
    taxon: Taxon,
    taxon_column: str | None = None,
) -> DataFrame:
    """Search a DataFrame for models matching a taxon.

    Args:
        df: DataFrame with taxonomic information
        taxon: Taxon to search for
        taxon_column: Column name containing Taxa objects. If None, searches family/genus/species columns.

    Returns:
        Filtered DataFrame with matching models

    Examples
    --------
    >>> import pandas as pd
    >>> from pylometree.taxonomy import Taxon, Taxa
    >>> # Create sample data
    >>> df = pd.DataFrame({
    ...     "model_id": ["m1", "m2", "m3"],
    ...     "taxa": [
    ...         Taxa([Taxon(family="Pinaceae", genus="Pseudotsuga", species="menziesii")]),
    ...         Taxa([Taxon(family="Pinaceae", genus="Pinus", species="ponderosa")]),
    ...         Taxa([Taxon(family="Fagaceae", genus="Quercus", species="robur")])
    ...     ]
    ... })
    >>> # Search for Douglas-fir
    >>> douglas_fir = Taxon(family="Pinaceae", genus="Pseudotsuga", species="menziesii")
    >>> result = search_by_taxon(df, douglas_fir)
    >>> len(result)
    1
    """
    matching_rows = []

    if taxon_column is None:
        # Search by family/genus/species columns
        for idx, row in df.iterrows():
            row_taxon = Taxon(
                family=row.get("family"),
                genus=row.get("genus"),
                species=row.get("species"),
            )
            if taxon.matches(row_taxon):
                matching_rows.append(idx)
    else:
        for idx, row in df.iterrows():
            row_taxa = row[taxon_column]
            if isinstance(row_taxa, Taxa):
                for row_taxon in row_taxa.taxa:
                    if taxon.matches(row_taxon):
                        matching_rows.append(idx)
                        break
            elif isinstance(row_taxa, Taxon):
                if taxon.matches(row_taxa):
                    matching_rows.append(idx)

    return df.loc[matching_rows]


def search_by_taxonomic_level(
    df: DataFrame,
    family: str | None = None,
    genus: str | None = None,
    species: str | None = None,
    taxon_column: str | None = None,
) -> DataFrame:
    """Search by taxonomic level (family, genus, or species).

    Args:
        df: DataFrame with taxonomic information
        family: Family name to filter by
        genus: Genus name to filter by
        species: Species name to filter by
        taxon_column: Column name containing Taxa objects. If None, searches family/genus/species columns.

    Returns:
        Filtered DataFrame

    Examples
    --------
    >>> # Search by family
    >>> pinaceae_models = search_by_taxonomic_level(df, family="Pinaceae")
    >>> # Search by species
    >>> ponderosa_models = search_by_taxonomic_level(df, species="ponderosa")
    """
    matching_rows = []

    if taxon_column is None:
        # Search by family/genus/species columns
        for idx, row in df.iterrows():
            row_family = row.get("family")
            row_genus = row.get("genus")
            row_species = row.get("species")
            if _taxon_matches_level_from_row(
                row_family, row_genus, row_species, family, genus, species
            ):
                matching_rows.append(idx)
    else:
        for idx, row in df.iterrows():
            row_taxa = row[taxon_column]
            if isinstance(row_taxa, Taxa):
                for row_taxon in row_taxa.taxa:
                    if _taxon_matches_level(row_taxon, family, genus, species):
                        matching_rows.append(idx)
                        break
            elif isinstance(row_taxa, Taxon):
                if _taxon_matches_level(row_taxa, family, genus, species):
                    matching_rows.append(idx)

    return df.loc[matching_rows]


def _taxon_matches_level_from_row(
    row_family: str | None,
    row_genus: str | None,
    row_species: str | None,
    family: str | None,
    genus: str | None,
    species: str | None,
) -> bool:
    """Check if a row's taxon matches the specified taxonomic levels."""
    if family is not None and row_family != family:
        return False
    if genus is not None and row_genus != genus:
        return False
    if species is not None and row_species != species:
        return False
    return True


def _taxon_matches_level(
    taxon: Taxon,
    family: str | None,
    genus: str | None,
    species: str | None,
) -> bool:
    """Check if a taxon matches the specified taxonomic levels."""
    if family is not None and taxon.family != family:
        return False
    if genus is not None and taxon.genus != genus:
        return False
    if species is not None and taxon.species != species:
        return False
    return True


def aggregate_taxa(
    df: DataFrame,
    grouping_col: str | None = None,
    taxon_column: str = "taxa",
) -> DataFrame:
    """Aggregate taxa by grouping column, creating unified Taxa objects.

    Args:
        df: DataFrame with taxonomic information
        grouping_col: Column to group by (e.g., "taxa_id")
        taxon_column: Column name containing Taxa objects

    Returns:
        DataFrame with aggregated taxa

    Examples
    --------
    >>> # Group multiple species into a single Taxa object
    >>> df_agg = aggregate_taxa(df, grouping_col="species_group")
    """
    if grouping_col is None:
        # No grouping, just ensure all are Taxa objects
        df_result = df.copy()
        df_result[taxon_column] = df_result[taxon_column].apply(
            lambda x: (
                x
                if isinstance(x, Taxa)
                else Taxa([x]) if isinstance(x, Taxon) else Taxa(x)
            )
        )
        return df_result

    # Group by specified column
    grouped = df.groupby(grouping_col)

    aggregated_rows = []

    for name, group in grouped:
        # Collect all unique taxa from the group
        all_taxa = []
        seen = set()

        for taxa in group[taxon_column]:
            if isinstance(taxa, Taxa):
                for taxon in taxa.taxa:
                    taxon_key = (taxon.family, taxon.genus, taxon.species)
                    if taxon_key not in seen:
                        all_taxa.append(taxon)
                        seen.add(taxon_key)
            elif isinstance(taxa, Taxon):
                taxon_key = (taxa.family, taxa.genus, taxa.species)
                if taxon_key not in seen:
                    all_taxa.append(taxa)
                    seen.add(taxon_key)

        # Create unified Taxa object
        unified_taxa = Taxa(all_taxa)

        # Get first row for other columns
        first_row = group.iloc[0].copy()
        first_row[taxon_column] = unified_taxa

        aggregated_rows.append(first_row)

    return pd.DataFrame(aggregated_rows)


def unnest_taxa(df: DataFrame, taxon_column: str = "taxa") -> DataFrame:
    """Unnest taxa column, expanding multiple taxa into separate rows.

    Args:
        df: DataFrame with taxonomic information
        taxon_column: Column name containing Taxa objects

    Returns:
        DataFrame with expanded rows (one per taxon)

    Examples
    --------
    >>> # Expand a row with multiple species into separate rows
    >>> df_unnested = unnest_taxa(df)
    """
    expanded_rows = []

    for idx, row in df.iterrows():
        row_taxa = row[taxon_column]
        if isinstance(row_taxa, Taxa):
            for taxon in row_taxa.taxa:
                new_row = row.copy()
                new_row[taxon_column] = taxon
                expanded_rows.append(new_row)
        elif isinstance(row_taxa, Taxon):
            expanded_rows.append(row)

    return pd.DataFrame(expanded_rows) if expanded_rows else df.copy()
