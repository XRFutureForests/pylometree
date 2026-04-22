"""Tests for I/O utilities (io/__init__.py)."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from pylometree.data.stand import Stand
from pylometree.data.tree import Tree
from pylometree.io import read_csv, stand_from_csv, stand_to_dataframe


class TestReadCsv:
    def test_basic_read(self, tmp_path: Path):
        csv_path = tmp_path / "test.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["dbh", "height", "species"])
            writer.writerow([20.0, 18.0, "Fagus sylvatica"])
            writer.writerow([30.0, 25.0, "Pinus sylvestris"])

        stand = read_csv(csv_path)
        assert len(stand.trees) == 2
        assert stand.trees[0].dbh == 20.0
        assert stand.trees[0].height == 18.0
        assert stand.trees[0].species == "Fagus sylvatica"

    def test_optional_columns(self, tmp_path: Path):
        csv_path = tmp_path / "test.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["dbh", "height", "species", "crown_area"])
            writer.writerow([20.0, 18.0, "Fagus", 50.0])

        stand = read_csv(csv_path, crown_area="crown_area")
        assert stand.trees[0].crown_area == 50.0

    def test_missing_values(self, tmp_path: Path):
        csv_path = tmp_path / "test.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["dbh", "height", "species"])
            writer.writerow([20.0, "", "Fagus"])  # missing height

        stand = read_csv(csv_path)
        assert stand.trees[0].dbh == 20.0
        assert stand.trees[0].height is None

    def test_plot_area(self, tmp_path: Path):
        csv_path = tmp_path / "test.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["dbh", "height"])
            writer.writerow([20.0, 18.0])
            writer.writerow([30.0, 25.0])

        stand = read_csv(csv_path, plot_area=0.1)  # 1000 m² = 0.1 ha
        assert stand.plot_area == 0.1

    def test_extra_columns(self, tmp_path: Path):
        csv_path = tmp_path / "test.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["dbh", "height", "plot_id", "date"])
            writer.writerow([20.0, 18.0, "P001", "2024-01-01"])

        stand = read_csv(csv_path)
        assert stand.trees[0].notes == {}

    def test_empty_file_returns_empty_stand(self, tmp_path: Path):
        csv_path = tmp_path / "empty.csv"
        csv_path.touch()

        stand = read_csv(csv_path)
        assert len(stand.trees) == 0

    def test_custom_column_names(self, tmp_path: Path):
        csv_path = tmp_path / "test.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["d", "h", "sp"])
            writer.writerow([22.0, 19.0, "Betula pendula"])

        stand = read_csv(csv_path, dbh_col="d", height_col="h", species_col="sp")
        assert stand.trees[0].dbh == pytest.approx(22.0)
        assert stand.trees[0].species == "Betula pendula"

    def test_species_col_none(self, tmp_path: Path):
        csv_path = tmp_path / "test.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["dbh", "height"])
            writer.writerow([12.0, 10.0])

        stand = read_csv(csv_path, species_col=None)
        assert stand.trees[0].species is None

    def test_string_path_accepted(self, tmp_path: Path):
        csv_path = tmp_path / "test.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["dbh", "height"])
            writer.writerow([15.0, 12.0])

        stand = read_csv(str(csv_path))
        assert len(stand.trees) == 1


class TestStandFromCsvAlias:
    def test_is_same_function(self):
        assert stand_from_csv is read_csv


class TestStandToDataframe:
    def test_returns_dataframe(self):
        pd = pytest.importorskip("pandas")
        stand = Stand(
            trees=[
                Tree(dbh=20.0, height=18.0, species="Fagus sylvatica"),
                Tree(dbh=30.0, height=25.0, species="Picea abies"),
            ]
        )
        df = stand_to_dataframe(stand)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2

    def test_expected_columns(self):
        pd = pytest.importorskip("pandas")
        stand = Stand(trees=[Tree(dbh=15.0, height=12.0)])
        df = stand_to_dataframe(stand)
        for col in ("species", "dbh", "height", "crown_area", "wood_density", "age"):
            assert col in df.columns

    def test_values_correct(self):
        pd = pytest.importorskip("pandas")
        stand = Stand(trees=[Tree(dbh=15.0, height=12.0, species="Betula pendula")])
        df = stand_to_dataframe(stand)
        assert df.iloc[0]["dbh"] == pytest.approx(15.0)
        assert df.iloc[0]["species"] == "Betula pendula"

    def test_empty_stand_returns_empty_df(self):
        pd = pytest.importorskip("pandas")
        df = stand_to_dataframe(Stand())
        assert len(df) == 0
