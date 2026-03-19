"""Tests for Tree and Stand data classes."""

import math

import pytest

from pylometree.data.stand import Stand
from pylometree.data.tree import Tree


class TestTree:
    def test_repr_with_values(self):
        t = Tree(dbh=20.0, height=18.0, species="Fagus sylvatica")
        r = repr(t)
        assert "Fagus" in r
        assert "20.0" in r

    def test_basal_area(self):
        t = Tree(dbh=20.0)
        expected = math.pi * (0.10) ** 2  # radius = 10 cm = 0.10 m
        assert abs(t.basal_area - expected) < 1e-10

    def test_d2h(self):
        t = Tree(dbh=10.0, height=15.0)
        assert abs(t.d2h - 1500.0) < 1e-10  # 10² × 15

    def test_none_when_missing(self):
        t = Tree()
        assert t.basal_area is None
        assert t.d2h is None


class TestStand:
    def _make_stand(self):
        trees = [
            Tree(dbh=10.0, height=10.0, agb=50.0),
            Tree(dbh=20.0, height=18.0, agb=200.0),
            Tree(dbh=15.0, height=14.0, agb=100.0),
        ]
        return Stand(trees=trees, plot_area=0.05)  # 500 m² plot

    def test_len(self):
        s = self._make_stand()
        assert len(s) == 3

    def test_basal_area_positive(self):
        s = self._make_stand()
        assert s.basal_area > 0

    def test_density_per_ha(self):
        s = self._make_stand()
        # 3 trees / 0.05 ha = 60 stems/ha
        assert abs(s.density_per_ha - 60.0) < 1e-10

    def test_agb_per_ha_units(self):
        s = self._make_stand()
        # total AGB = 350 kg; per ha = 350 / 0.05 / 1000 = 7.0 Mg/ha
        assert abs(s.agb_per_ha - 7.0) < 1e-10

    def test_carbon_stock(self):
        s = self._make_stand()
        assert 0 < s.carbon_stock_per_ha < s.agb_per_ha

    def test_requires_area(self):
        s = Stand(trees=[Tree(dbh=10.0)], plot_area=None)
        with pytest.raises(ValueError):
            _ = s.density_per_ha

    def test_qmd(self):
        s = self._make_stand()
        qmd = s.qmd
        # QMD ≥ mean DBH (Jensen's inequality)
        assert qmd >= s.mean_dbh

    def test_from_dataframe(self):
        pytest.importorskip("pandas")
        import pandas as pd

        df = pd.DataFrame(
            {
                "dbh": [10.0, 20.0],
                "height": [12.0, 18.0],
                "species": ["Pinus sp.", "Quercus sp."],
            }
        )
        stand = Stand.from_dataframe(df, plot_area=0.1)
        assert len(stand) == 2
        assert stand.trees[0].species == "Pinus sp."
        assert stand.trees[0].species == "Pinus sp."
