"""Tests for I/O utilities (io/__init__.py)."""

from __future__ import annotations

import csv
import tempfile
from pathlib import Path

import pytest

from pylometree.io import read_csv


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
