"""Tests for taxonomy module."""

import pandas as pd
import pytest

from pylometree.taxonomy import Taxa, Taxon, search_by_taxon, search_by_taxonomic_level


class TestTaxon:
    """Test Taxon class."""

    def test_create_taxon(self):
        """Test creating a Taxon."""
        taxon = Taxon(family="Pinaceae", genus="Pinus", species="sylvestris")
        assert taxon.family == "Pinaceae"
        assert taxon.genus == "Pinus"
        assert taxon.species == "sylvestris"

    def test_taxon_hashable(self):
        """Test that Taxon is hashable."""
        taxon = Taxon(family="Pinaceae", genus="Pinus", species="sylvestris")
        taxon_set = {taxon}
        assert taxon in taxon_set

    def test_taxon_equality(self):
        """Test Taxon equality."""
        taxon1 = Taxon(family="Pinaceae", genus="Pinus", species="sylvestris")
        taxon2 = Taxon(family="Pinaceae", genus="Pinus", species="sylvestris")
        taxon3 = Taxon(family="Fagaceae", genus="Fagus", species="sylvatica")
        assert taxon1 == taxon2
        assert taxon1 != taxon3

    def test_taxon_repr(self):
        """Test Taxon repr."""
        taxon = Taxon(family="Pinaceae", genus="Pinus", species="sylvestris")
        repr_str = repr(taxon)
        assert "Pinaceae" in repr_str
        assert "Pinus" in repr_str
        assert "sylvestris" in repr_str


class TestTaxa:
    """Test Taxa class."""

    def test_create_taxa(self):
        """Test creating a Taxa."""
        taxon1 = Taxon(family="Pinaceae", genus="Pinus", species="sylvestris")
        taxon2 = Taxon(family="Fagaceae", genus="Fagus", species="sylvatica")
        taxa = Taxa([taxon1, taxon2])
        assert len(taxa) == 2

    def test_taxa_uniqueness(self):
        """Test that Taxa allows duplicates (silently skips them)."""
        taxon1 = Taxon(family="Pinaceae", genus="Pinus", species="sylvestris")
        taxon2 = Taxon(family="Pinaceae", genus="Pinus", species="sylvestris")
        taxa = Taxa([taxon1, taxon2])
        assert len(taxa) == 1

    def test_taxa_iterable(self):
        """Test that Taxa is iterable."""
        taxon1 = Taxon(family="Pinaceae", genus="Pinus", species="sylvestris")
        taxon2 = Taxon(family="Fagaceae", genus="Fagus", species="sylvatica")
        taxa = Taxa([taxon1, taxon2])
        taxa_list = list(taxa)
        assert len(taxa_list) == 2
        assert taxa_list[0] == taxon1
        assert taxa_list[1] == taxon2

    def test_taxa_repr(self):
        """Test Taxa repr."""
        taxon = Taxon(family="Pinaceae", genus="Pinus", species="sylvestris")
        taxa = Taxa([taxon])
        repr_str = repr(taxa)
        assert "Taxa" in repr_str
        assert "Pinaceae" in repr_str

    def test_taxa_empty(self):
        """Test creating empty Taxa."""
        taxa = Taxa([])
        assert len(taxa) == 0

    def test_taxa_add(self):
        """Test adding Taxon to Taxa."""
        taxon1 = Taxon(family="Pinaceae", genus="Pinus", species="sylvestris")
        taxon2 = Taxon(family="Fagaceae", genus="Fagus", species="sylvatica")
        taxa = Taxa([taxon1])
        taxa.add(taxon2)
        assert len(taxa) == 2

    def test_taxa_add_duplicate(self):
        """Test adding duplicate Taxon to Taxa."""
        taxon1 = Taxon(family="Pinaceae", genus="Pinus", species="sylvestris")
        taxon2 = Taxon(family="Pinaceae", genus="Pinus", species="sylvestris")
        taxa = Taxa([taxon1])
        taxa.add(taxon2)
        assert len(taxa) == 1


class TestSearchByTaxon:
    """Test search_by_taxon function."""

    def test_search_exact_match(self):
        """Test searching for exact taxon match."""
        df = pd.DataFrame(
            {
                "family": ["Pinaceae", "Fagaceae", "Pinaceae"],
                "genus": ["Pinus", "Fagus", "Picea"],
                "species": ["sylvestris", "sylvatica", "abies"],
            }
        )
        taxon = Taxon(family="Pinaceae", genus="Pinus", species="sylvestris")
        result = search_by_taxon(df, taxon, taxon_column=None)
        assert len(result) == 1
        assert result.iloc[0]["species"] == "sylvestris"

    def test_search_partial_match(self):
        """Test searching with partial taxon (only family)."""
        df = pd.DataFrame(
            {
                "family": ["Pinaceae", "Fagaceae", "Pinaceae"],
                "genus": ["Pinus", "Fagus", "Picea"],
                "species": ["sylvestris", "sylvatica", "abies"],
            }
        )
        taxon = Taxon(family="Pinaceae", genus=None, species=None)
        result = search_by_taxon(df, taxon, taxon_column=None)
        assert len(result) == 2

    def test_search_no_match(self):
        """Test searching for non-existent taxon."""
        df = pd.DataFrame(
            {
                "family": ["Pinaceae", "Fagaceae"],
                "genus": ["Pinus", "Fagus"],
                "species": ["sylvestris", "sylvatica"],
            }
        )
        taxon = Taxon(family="Betulaceae", genus="Betula", species="alba")
        result = search_by_taxon(df, taxon, taxon_column=None)
        assert len(result) == 0

    def test_search_with_taxon_column(self):
        """Test searching with pre-parsed taxon column."""
        df = pd.DataFrame(
            {
                "taxon": [
                    Taxon(family="Pinaceae", genus="Pinus", species="sylvestris"),
                    Taxon(family="Fagaceae", genus="Fagus", species="sylvatica"),
                ]
            }
        )
        taxon = Taxon(family="Pinaceae", genus="Pinus", species="sylvestris")
        result = search_by_taxon(df, taxon, taxon_column="taxon")
        assert len(result) == 1


class TestSearchByTaxonomicLevel:
    """Test search_by_taxonomic_level function."""

    def test_search_by_family(self):
        """Test searching by family only."""
        df = pd.DataFrame(
            {
                "family": ["Pinaceae", "Fagaceae", "Pinaceae"],
                "genus": ["Pinus", "Fagus", "Picea"],
                "species": ["sylvestris", "sylvatica", "abies"],
            }
        )
        result = search_by_taxonomic_level(df, family="Pinaceae")
        assert len(result) == 2

    def test_search_by_family_genus(self):
        """Test searching by family and genus."""
        df = pd.DataFrame(
            {
                "family": ["Pinaceae", "Fagaceae", "Pinaceae"],
                "genus": ["Pinus", "Fagus", "Picea"],
                "species": ["sylvestris", "sylvatica", "abies"],
            }
        )
        result = search_by_taxonomic_level(df, family="Pinaceae", genus="Pinus")
        assert len(result) == 1
        assert result.iloc[0]["species"] == "sylvestris"

    def test_search_by_all_levels(self):
        """Test searching by all taxonomic levels."""
        df = pd.DataFrame(
            {
                "family": ["Pinaceae", "Fagaceae", "Pinaceae"],
                "genus": ["Pinus", "Fagus", "Picea"],
                "species": ["sylvestris", "sylvatica", "abies"],
            }
        )
        result = search_by_taxonomic_level(
            df, family="Pinaceae", genus="Pinus", species="sylvestris"
        )
        assert len(result) == 1
        assert result.iloc[0]["species"] == "sylvestris"

    def test_search_no_match(self):
        """Test searching for non-existent taxon."""
        df = pd.DataFrame(
            {
                "family": ["Pinaceae", "Fagaceae"],
                "genus": ["Pinus", "Fagus"],
                "species": ["sylvestris", "sylvatica"],
            }
        )
        result = search_by_taxonomic_level(df, family="Betulaceae")
        assert len(result) == 0
