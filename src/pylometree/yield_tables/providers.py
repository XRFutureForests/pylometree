"""Yield table provider interface and implementations.

Ingestion-time providers that extract yield tables from external sources
(R packages, XLSX files, PDFs, parametric models) and normalize them into
a common schema.

Providers run offline via the ingest CLI, not during resolution.
Ingested tables are stored as CSV files that slot into the store resolution path.
"""

import importlib.resources
import logging
import shutil
import subprocess
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import numpy as np
import pandas as pd

from pylometree.yield_tables.record import YieldTableRecord
from pylometree.yield_tables.species import SpeciesMapping, load_species_mapping

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Provider abstract base class
# ---------------------------------------------------------------------------


class YieldProvider(ABC):
    """Abstract base class for yield table data sources."""

    name: str = "base"
    description: str = ""

    @abstractmethod
    def available(self) -> bool:
        """Check whether this provider can run (dependencies installed, files present)."""

    @abstractmethod
    def iter_tables(
        self,
        species_mapping: Optional[SpeciesMapping] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Iterable[YieldTableRecord]:
        """Yield normalized table records from this source.

        Args:
            species_mapping: Species name mapping. If None, loads bundled default.
            config: Provider-specific settings (file paths, etc.).
        """

    def status_message(self) -> str:
        """Human-readable availability status."""
        if self.available():
            return "available"
        return "not available"


# ---------------------------------------------------------------------------
# Internal helpers: dependency checks
# ---------------------------------------------------------------------------


def _r_package_available(package_name: str) -> bool:
    """Check whether R and a specific R package are installed."""
    rscript = shutil.which("Rscript")
    if not rscript:
        return False
    try:
        result = subprocess.run(
            [rscript, "-e", f"library({package_name})"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def _tabula_available() -> bool:
    """Check whether tabula-py is installed."""
    try:
        import tabula  # noqa: F401
        return True
    except ImportError:
        return False


def _get_bundled_r_script(name: str) -> Path:
    """Locate a bundled R script in the package data."""
    ref = importlib.resources.files("pylometree.yield_tables") / "r_scripts" / name
    p = Path(str(ref))
    if p.exists():
        return p
    return ref  # type: ignore[return-value]


def _ensure_mapping(mapping: Optional[SpeciesMapping]) -> SpeciesMapping:
    """Return the given mapping or load the bundled default."""
    if mapping is not None:
        return mapping
    return load_species_mapping()


# ---------------------------------------------------------------------------
# Internal helpers: R extraction
# ---------------------------------------------------------------------------


def _run_r_extraction(
    r_script: Path,
    source_name: str,
    species_map: SpeciesMapping,
) -> Iterable[YieldTableRecord]:
    """Run an R script and parse its CSV output into YieldTableRecords."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_csv = Path(tmpdir) / "output.csv"
        try:
            result = subprocess.run(
                ["Rscript", str(r_script), str(output_csv)],
                capture_output=True,
                text=True,
                timeout=300,
            )
        except subprocess.TimeoutExpired:
            logger.error("R script timed out: %s", r_script)
            return
        except FileNotFoundError:
            logger.error("Rscript not found on PATH")
            return

        if result.returncode != 0:
            logger.error(
                "R script failed (exit %d): %s\n%s",
                result.returncode, r_script, result.stderr[:2000],
            )
            return

        if not output_csv.exists():
            logger.error("R script produced no output: %s", r_script)
            return

        df = pd.read_csv(output_csv)

        required = {"species_latin", "age", "site_index"}
        if not required.issubset(df.columns):
            logger.error(
                "R output missing columns: %s (has: %s)",
                required - set(df.columns), list(df.columns),
            )
            return

        group_cols = ["species_latin"]
        for col in ["region", "management", "site_index", "table_id"]:
            if col in df.columns:
                group_cols.append(col)

        for group_key, group_df in df.groupby(group_cols):
            if not isinstance(group_key, tuple):
                group_key = (group_key,)

            group_df = group_df.sort_values("age").reset_index(drop=True)
            latin = str(group_key[0])
            region = str(group_key[group_cols.index("region")]) if "region" in group_cols else ""
            management = str(group_key[group_cols.index("management")]) if "management" in group_cols else "normal"
            si = float(group_key[group_cols.index("site_index")]) if "site_index" in group_cols else 0.0
            tid = str(group_key[group_cols.index("table_id")]) if "table_id" in group_cols else ""

            mapped = species_map.get(latin)
            common_name = mapped.get("common_name", "")
            std_name = mapped.get("standardized_name", "")

            heights = group_df["height"].tolist() if "height" in group_df.columns else [0.0] * len(group_df)
            dbhs = group_df["dbh"].tolist() if "dbh" in group_df.columns else [0.0] * len(group_df)
            volumes = group_df["volume"].tolist() if "volume" in group_df.columns else []

            record = YieldTableRecord(
                species_latin=latin,
                species_common=common_name,
                standardized_name=std_name,
                region=region,
                management=management,
                site_index=si,
                source=source_name,
                table_id=tid,
                ages=group_df["age"].tolist(),
                heights=heights,
                dbhs=dbhs,
                volumes=volumes,
            )

            issues = record.validate()
            if issues:
                logger.warning(
                    "Skipping %s/%s (si=%.0f): %s",
                    source_name, latin, si, "; ".join(issues),
                )
                continue

            yield record


# ---------------------------------------------------------------------------
# Internal helpers: XLSX parsing
# ---------------------------------------------------------------------------

_CARBON_ET_SPECIES = {
    "fichte": "Picea abies",
    "kiefer": "Pinus sylvestris",
    "buche": "Fagus sylvatica",
    "eiche": "Quercus robur",
    "douglasie": "Pseudotsuga menziesii",
    "spruce": "Picea abies",
    "pine": "Pinus sylvestris",
    "beech": "Fagus sylvatica",
    "oak": "Quercus robur",
    "douglas fir": "Pseudotsuga menziesii",
    "douglas-fir": "Pseudotsuga menziesii",
}


def _parse_carbon_et_xlsx(
    xlsx_path: Path,
    species_map: SpeciesMapping,
) -> Iterable[YieldTableRecord]:
    """Parse yield tables from C_ET_pub.xlsx (Kohlenstoff-Ertragstafeln)."""
    try:
        xl = pd.ExcelFile(xlsx_path, engine="openpyxl")
    except Exception as e:
        logger.error("Failed to open XLSX: %s -- %s", xlsx_path, e)
        return

    for sheet_name in xl.sheet_names:
        sheet_lower = sheet_name.lower().strip()

        latin = None
        for key, value in _CARBON_ET_SPECIES.items():
            if key in sheet_lower:
                latin = value
                break
        if not latin:
            logger.debug("Skipping unrecognised sheet: %s", sheet_name)
            continue

        try:
            df = xl.parse(sheet_name)
        except Exception as e:
            logger.warning("Error parsing sheet %s: %s", sheet_name, e)
            continue

        df.columns = [str(c).strip().lower() for c in df.columns]

        age_col = None
        for candidate in ["alter", "age", "a"]:
            if candidate in df.columns:
                age_col = candidate
                break
        if age_col is None:
            logger.debug("No age column in sheet %s", sheet_name)
            continue

        height_col = None
        for candidate in ["ho", "h100", "h_q_m", "hg", "height", "h"]:
            if candidate in df.columns:
                height_col = candidate
                break

        dbh_col = None
        for candidate in ["dg", "d_q_cm", "dbh", "d"]:
            if candidate in df.columns:
                dbh_col = candidate
                break

        vol_col = None
        for candidate in ["vfm", "v", "volume", "v_m3_ha"]:
            if candidate in df.columns:
                vol_col = candidate
                break

        if height_col is None and dbh_col is None:
            logger.debug("No height or DBH column in sheet %s", sheet_name)
            continue

        site_index = 0.0
        ek_col = None
        for candidate in ["ek", "ekl", "ertragsklasse", "yield_class", "si"]:
            if candidate in df.columns:
                ek_col = candidate
                break

        df = df.dropna(subset=[age_col])
        df[age_col] = pd.to_numeric(df[age_col], errors="coerce")
        df = df.dropna(subset=[age_col])

        if ek_col:
            for ek_val, ek_df in df.groupby(ek_col):
                ek_df = ek_df.sort_values(age_col).reset_index(drop=True)
                si = float(ek_val) if pd.notna(ek_val) else 0.0
                record = _build_xlsx_record(
                    ek_df, age_col, height_col, dbh_col, vol_col,
                    latin, si, sheet_name, species_map,
                )
                if record:
                    yield record
        else:
            df = df.sort_values(age_col).reset_index(drop=True)
            record = _build_xlsx_record(
                df, age_col, height_col, dbh_col, vol_col,
                latin, site_index, sheet_name, species_map,
            )
            if record:
                yield record


def _build_xlsx_record(
    df: pd.DataFrame,
    age_col: str,
    height_col: Optional[str],
    dbh_col: Optional[str],
    vol_col: Optional[str],
    species_latin: str,
    site_index: float,
    sheet_name: str,
    species_map: SpeciesMapping,
) -> Optional[YieldTableRecord]:
    """Build a YieldTableRecord from a single XLSX table block."""
    ages = df[age_col].tolist()
    heights = df[height_col].tolist() if height_col else [0.0] * len(ages)
    dbhs = df[dbh_col].tolist() if dbh_col else [0.0] * len(ages)
    volumes = df[vol_col].tolist() if vol_col else []

    heights = [float(h) if pd.notna(h) else 0.0 for h in heights]
    dbhs = [float(d) if pd.notna(d) else 0.0 for d in dbhs]
    ages = [float(a) for a in ages]

    mapped = species_map.get(species_latin)

    record = YieldTableRecord(
        species_latin=species_latin,
        species_common=mapped.get("common_name", ""),
        standardized_name=mapped.get("standardized_name", ""),
        region="DE",
        management="normal",
        site_index=site_index,
        source="carbon_et_xlsx",
        table_id=f"C_ET_{sheet_name}",
        ages=ages,
        heights=heights,
        dbhs=dbhs,
        volumes=volumes,
    )

    issues = record.validate()
    if issues:
        logger.debug(
            "Skipping XLSX %s (si=%.0f): %s",
            species_latin, site_index, "; ".join(issues),
        )
        return None

    return record


# ---------------------------------------------------------------------------
# Internal helpers: PDF parsing
# ---------------------------------------------------------------------------


def _parse_forest_yield_pdf(
    pdf_path: Path,
    species_map: SpeciesMapping,
) -> Iterable[YieldTableRecord]:
    """Parse UK Forest Yield (FC Booklet 48) PDF."""
    try:
        import tabula
    except ImportError:
        logger.error("tabula-py not installed")
        return

    logger.info("Extracting tables from Forest Yield PDF (this may take a minute)...")

    try:
        tables = tabula.read_pdf(
            str(pdf_path), pages="all", multiple_tables=True, lattice=True,
        )
    except Exception as e:
        logger.error("Failed to extract tables from PDF: %s", e)
        return

    _FC_SPECIES = {
        "Sitka spruce": "Picea sitchensis",
        "Norway spruce": "Picea abies",
        "Scots pine": "Pinus sylvestris",
        "Corsican pine": "Pinus nigra subsp. laricio",
        "Lodgepole pine": "Pinus contorta",
        "Grand fir": "Abies grandis",
        "Douglas fir": "Pseudotsuga menziesii",
        "Japanese larch": "Larix kaempferi",
        "European larch": "Larix decidua",
        "Western hemlock": "Tsuga heterophylla",
        "Western red cedar": "Thuja plicata",
        "Oak": "Quercus robur",
        "Beech": "Fagus sylvatica",
        "Sycamore": "Acer pseudoplatanus",
        "Ash": "Fraxinus excelsior",
        "Birch": "Betula pendula",
        "Poplar": "Populus spp.",
    }

    for table_df in tables:
        if table_df is None or table_df.empty:
            continue
        table_df.columns = [str(c).strip().lower() for c in table_df.columns]
        record = _try_parse_fc_table(table_df, _FC_SPECIES, species_map)
        if record:
            yield record


def _try_parse_fc_table(
    df: pd.DataFrame,
    fc_species: Dict[str, str],
    species_map: SpeciesMapping,
) -> Optional[YieldTableRecord]:
    """Attempt to parse a single extracted table from FC Booklet 48."""
    age_col = None
    for candidate in ["age", "age (years)", "years"]:
        if candidate in df.columns:
            age_col = candidate
            break
    if age_col is None:
        return None

    height_col = None
    for candidate in ["top height", "top ht", "height", "top height (m)", "ht"]:
        if candidate in df.columns:
            height_col = candidate
            break

    dbh_col = None
    for candidate in ["dbh", "mean dbh", "dbh (cm)", "mean dbh (cm)"]:
        if candidate in df.columns:
            dbh_col = candidate
            break

    if height_col is None and dbh_col is None:
        return None

    df = df.copy()
    df[age_col] = pd.to_numeric(df[age_col], errors="coerce")
    df = df.dropna(subset=[age_col])
    if df.empty:
        return None

    if height_col:
        df[height_col] = pd.to_numeric(df[height_col], errors="coerce")
    if dbh_col:
        df[dbh_col] = pd.to_numeric(df[dbh_col], errors="coerce")

    df = df.sort_values(age_col).reset_index(drop=True)

    ages = df[age_col].tolist()
    heights = df[height_col].fillna(0).tolist() if height_col else [0.0] * len(ages)
    dbhs = df[dbh_col].fillna(0).tolist() if dbh_col else [0.0] * len(ages)

    species_latin = "Unknown"
    for col in df.columns:
        for val in df[col].head(5).astype(str):
            for name, latin in fc_species.items():
                if name.lower() in val.lower():
                    species_latin = latin
                    break
            if species_latin != "Unknown":
                break
        if species_latin != "Unknown":
            break

    if species_latin == "Unknown":
        return None

    mapped = species_map.get(species_latin)

    record = YieldTableRecord(
        species_latin=species_latin,
        species_common=mapped.get("common_name", ""),
        standardized_name=mapped.get("standardized_name", ""),
        region="UK",
        management="normal",
        site_index=0.0,
        source="forest_yield_uk",
        table_id="FC_BK48",
        ages=ages,
        heights=heights,
        dbhs=dbhs,
    )

    issues = record.validate()
    if issues:
        return None
    return record


def _parse_pryor_pdf(
    pdf_path: Path,
    species_map: SpeciesMapping,
) -> Iterable[YieldTableRecord]:
    """Parse wild cherry yield tables from Pryor FC Bulletin 75."""
    try:
        import tabula
    except ImportError:
        logger.error("tabula-py not installed")
        return

    logger.info("Extracting tables from Pryor PDF...")

    try:
        tables = tabula.read_pdf(
            str(pdf_path), pages="all", multiple_tables=True, lattice=True,
        )
    except Exception as e:
        logger.error("Failed to extract tables from PDF: %s", e)
        return

    latin = "Prunus avium"
    mapped = species_map.get(latin)
    table_idx = 0

    for table_df in tables:
        if table_df is None or table_df.empty:
            continue

        table_df.columns = [str(c).strip().lower() for c in table_df.columns]

        age_col = None
        for candidate in ["age", "age (years)", "years"]:
            if candidate in table_df.columns:
                age_col = candidate
                break
        if age_col is None:
            continue

        height_col = None
        for candidate in ["top height", "height", "ht", "top height (m)"]:
            if candidate in table_df.columns:
                height_col = candidate
                break

        dbh_col = None
        for candidate in ["dbh", "mean dbh", "dbh (cm)"]:
            if candidate in table_df.columns:
                dbh_col = candidate
                break

        if height_col is None and dbh_col is None:
            continue

        table_df = table_df.copy()
        table_df[age_col] = pd.to_numeric(table_df[age_col], errors="coerce")
        table_df = table_df.dropna(subset=[age_col])
        if table_df.empty:
            continue
        if height_col:
            table_df[height_col] = pd.to_numeric(table_df[height_col], errors="coerce")
        if dbh_col:
            table_df[dbh_col] = pd.to_numeric(table_df[dbh_col], errors="coerce")

        table_df = table_df.sort_values(age_col).reset_index(drop=True)
        table_idx += 1

        record = YieldTableRecord(
            species_latin=latin,
            species_common=mapped.get("common_name", ""),
            standardized_name=mapped.get("standardized_name", ""),
            region="UK",
            management="normal",
            site_index=0.0,
            source="pryor_cherry",
            table_id=f"FC_B75_t{table_idx}",
            ages=table_df[age_col].tolist(),
            heights=table_df[height_col].fillna(0).tolist() if height_col else [0.0] * len(table_df),
            dbhs=table_df[dbh_col].fillna(0).tolist() if dbh_col else [0.0] * len(table_df),
        )

        issues = record.validate()
        if not issues:
            yield record


def _parse_nova_scotia_pdf(
    pdf_path: Path,
    species_map: SpeciesMapping,
) -> Iterable[YieldTableRecord]:
    """Parse Nova Scotia softwood yield tables."""
    try:
        import tabula
    except ImportError:
        logger.error("tabula-py not installed")
        return

    logger.info("Extracting tables from Nova Scotia PDF...")

    _NS_SPECIES = {
        "balsam fir": "Abies balsamea",
        "red spruce": "Picea rubens",
        "black spruce": "Picea mariana",
        "white spruce": "Picea glauca",
        "eastern hemlock": "Tsuga canadensis",
        "jack pine": "Pinus banksiana",
        "red pine": "Pinus resinosa",
        "eastern white pine": "Pinus strobus",
    }

    try:
        tables = tabula.read_pdf(
            str(pdf_path), pages="all", multiple_tables=True, lattice=True,
        )
    except Exception as e:
        logger.error("Failed to extract tables from PDF: %s", e)
        return

    for table_df in tables:
        if table_df is None or table_df.empty:
            continue

        table_df.columns = [str(c).strip().lower() for c in table_df.columns]

        age_col = None
        for candidate in ["age", "age (years)", "years"]:
            if candidate in table_df.columns:
                age_col = candidate
                break
        if age_col is None:
            continue

        height_col = None
        for candidate in ["height", "dom. height", "dominant height", "ht", "avg ht"]:
            if candidate in table_df.columns:
                height_col = candidate
                break

        dbh_col = None
        for candidate in ["dbh", "avg dbh", "mean dbh"]:
            if candidate in table_df.columns:
                dbh_col = candidate
                break

        if height_col is None and dbh_col is None:
            continue

        table_df = table_df.copy()
        table_df[age_col] = pd.to_numeric(table_df[age_col], errors="coerce")
        table_df = table_df.dropna(subset=[age_col])
        if table_df.empty:
            continue
        if height_col:
            table_df[height_col] = pd.to_numeric(table_df[height_col], errors="coerce")
        if dbh_col:
            table_df[dbh_col] = pd.to_numeric(table_df[dbh_col], errors="coerce")

        table_df = table_df.sort_values(age_col).reset_index(drop=True)

        species_latin = None
        for col in table_df.columns:
            for val in table_df[col].head(3).astype(str):
                for name, latin in _NS_SPECIES.items():
                    if name in val.lower():
                        species_latin = latin
                        break
                if species_latin:
                    break
            if species_latin:
                break

        if not species_latin:
            continue

        mapped = species_map.get(species_latin)

        heights_raw = table_df[height_col].fillna(0).tolist() if height_col else [0.0] * len(table_df)
        dbhs_raw = table_df[dbh_col].fillna(0).tolist() if dbh_col else [0.0] * len(table_df)

        max_h = max(heights_raw) if heights_raw else 0
        if max_h > 60:
            heights_raw = [h * 0.3048 for h in heights_raw]
        max_d = max(dbhs_raw) if dbhs_raw else 0
        if max_d > 100:
            dbhs_raw = [d / 10.0 for d in dbhs_raw]
        if 0 < max_d < 1:
            dbhs_raw = [d * 100.0 for d in dbhs_raw]

        record = YieldTableRecord(
            species_latin=species_latin,
            species_common=mapped.get("common_name", ""),
            standardized_name=mapped.get("standardized_name", ""),
            region="CA-NS",
            management="normal",
            site_index=0.0,
            source="nova_scotia",
            table_id="NS_Report22",
            ages=table_df[age_col].tolist(),
            heights=heights_raw,
            dbhs=dbhs_raw,
        )

        issues = record.validate()
        if not issues:
            yield record


def _parse_usda_pdf(
    pdf_path: Path,
    species_map: SpeciesMapping,
) -> Iterable[YieldTableRecord]:
    """Parse USDA forest stocking and yield tables."""
    try:
        import tabula
    except ImportError:
        logger.error("tabula-py not installed")
        return

    logger.info("Extracting tables from USDA stocking PDF...")

    try:
        tables = tabula.read_pdf(
            str(pdf_path), pages="all", multiple_tables=True, stream=True,
        )
    except Exception as e:
        logger.error("Failed to extract tables from PDF: %s", e)
        return

    table_idx = 0
    for table_df in tables:
        if table_df is None or table_df.empty:
            continue

        table_df.columns = [str(c).strip().lower() for c in table_df.columns]

        age_col = None
        for candidate in ["age", "age (years)", "stand age"]:
            if candidate in table_df.columns:
                age_col = candidate
                break
        if age_col is None:
            continue

        table_df = table_df.copy()
        table_df[age_col] = pd.to_numeric(table_df[age_col], errors="coerce")
        table_df = table_df.dropna(subset=[age_col])
        if table_df.empty:
            continue

        table_df = table_df.sort_values(age_col).reset_index(drop=True)

        height_col = None
        for candidate in ["height", "avg height", "site index", "ht"]:
            if candidate in table_df.columns:
                height_col = candidate
                break

        dbh_col = None
        for candidate in ["dbh", "avg dbh", "mean dbh"]:
            if candidate in table_df.columns:
                dbh_col = candidate
                break

        vol_col = None
        for candidate in ["volume", "vol", "yield", "cu ft/acre", "bd ft/acre"]:
            if candidate in table_df.columns:
                vol_col = candidate
                break

        if height_col is None and dbh_col is None and vol_col is None:
            continue

        if height_col:
            table_df[height_col] = pd.to_numeric(table_df[height_col], errors="coerce")
        if dbh_col:
            table_df[dbh_col] = pd.to_numeric(table_df[dbh_col], errors="coerce")

        heights = table_df[height_col].fillna(0).tolist() if height_col else [0.0] * len(table_df)
        dbhs = table_df[dbh_col].fillna(0).tolist() if dbh_col else [0.0] * len(table_df)
        volumes = []
        if vol_col:
            table_df[vol_col] = pd.to_numeric(table_df[vol_col], errors="coerce")
            volumes = table_df[vol_col].fillna(0).tolist()

        max_h = max(heights) if heights else 0
        if max_h > 60:
            heights = [h * 0.3048 for h in heights]
        max_d = max(dbhs) if dbhs else 0
        if max_d > 0 and max_d < 3:
            dbhs = [d * 2.54 for d in dbhs]

        table_idx += 1

        record = YieldTableRecord(
            species_latin="Unknown",
            species_common="",
            standardized_name="",
            region="US",
            management="normal",
            site_index=0.0,
            source="usda_stocking",
            table_id=f"USDA_t{table_idx}",
            ages=table_df[age_col].tolist(),
            heights=heights,
            dbhs=dbhs,
            volumes=volumes,
        )

        if height_col is None and dbh_col is None:
            logger.debug(
                "USDA table %d: volume-only (no H/D) -- mark for parametric enrichment",
                table_idx,
            )

        issues = record.validate()
        if not issues:
            yield record


# ---------------------------------------------------------------------------
# Internal helpers: Parametric model evaluation
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Internal helpers: Forstpraxis Ertragstafelauszuge PDF parsing
# ---------------------------------------------------------------------------

# The Forstpraxis Ertragstafelauszuge PDF (AFZ/FHJ Kalender) compiles German
# yield table extracts for ~20 species in standardized 10-year age intervals.
# Each species block has columns: age, height, DBH, volume (and sometimes more).
# Species are identified by German names in section headers.

_FORSTPRAXIS_SPECIES = {
    "fichte": "Picea abies",
    "kiefer": "Pinus sylvestris",
    "buche": "Fagus sylvatica",
    "eiche": "Quercus robur",
    "douglasie": "Pseudotsuga menziesii",
    "lärche": "Larix decidua",
    "laerche": "Larix decidua",
    "tanne": "Abies alba",
    "birke": "Betula pendula",
    "erle": "Alnus glutinosa",
    "esche": "Fraxinus excelsior",
    "hainbuche": "Carpinus betulus",
    "winterlinde": "Tilia cordata",
    "linde": "Tilia cordata",
    "roteiche": "Quercus rubra",
    "robinie": "Robinia pseudoacacia",
    "schwarzkiefer": "Pinus nigra",
    "pappel": "Populus x canescens",
    "weide": "Salix alba",
    "edelkastanie": "Castanea sativa",
}


def _parse_forstpraxis_pdf(
    pdf_path: Path,
    species_map: SpeciesMapping,
) -> Iterable[YieldTableRecord]:
    """Parse German Forstpraxis Ertragstafelauszuge PDF.

    This PDF contains yield table extracts for multiple German species in a
    standardized format with 10-year age intervals.  Each species section
    typically has columns for age, height (ho or h100), DBH (dg), and volume.
    """
    try:
        import tabula
    except ImportError:
        logger.error("tabula-py not installed")
        return

    logger.info(
        "Extracting tables from Forstpraxis Ertragstafelauszuge PDF "
        "(this may take a minute)..."
    )

    try:
        tables = tabula.read_pdf(
            str(pdf_path), pages="all", multiple_tables=True, lattice=True,
        )
    except Exception as e:
        logger.error("Failed to extract tables from PDF: %s", e)
        return

    for table_df in tables:
        if table_df is None or table_df.empty:
            continue

        table_df.columns = [str(c).strip().lower() for c in table_df.columns]

        # Try to identify which species this table belongs to by scanning
        # column headers and cell values for German species names
        species_latin = _identify_forstpraxis_species(table_df)
        if not species_latin:
            continue

        # Find standard columns
        age_col = None
        for candidate in ["alter", "age", "a"]:
            if candidate in table_df.columns:
                age_col = candidate
                break
        if age_col is None:
            continue

        height_col = None
        for candidate in ["ho", "h100", "h_q_m", "hg", "height", "h",
                          "oh", "oberhöhe", "oberhoehe"]:
            if candidate in table_df.columns:
                height_col = candidate
                break

        dbh_col = None
        for candidate in ["dg", "d_q_cm", "dbh", "d", "dg cm"]:
            if candidate in table_df.columns:
                dbh_col = candidate
                break

        vol_col = None
        for candidate in ["vfm", "v", "volume", "v_m3_ha", "gwl",
                          "derbholz", "efm"]:
            if candidate in table_df.columns:
                vol_col = candidate
                break

        if height_col is None and dbh_col is None:
            continue

        # Parse and clean data
        table_df = table_df.copy()
        table_df[age_col] = pd.to_numeric(table_df[age_col], errors="coerce")
        table_df = table_df.dropna(subset=[age_col])
        if table_df.empty or len(table_df) < 2:
            continue

        if height_col:
            table_df[height_col] = pd.to_numeric(
                table_df[height_col], errors="coerce"
            )
        if dbh_col:
            table_df[dbh_col] = pd.to_numeric(
                table_df[dbh_col], errors="coerce"
            )
        if vol_col:
            table_df[vol_col] = pd.to_numeric(
                table_df[vol_col], errors="coerce"
            )

        # Check for site index / yield class column
        ek_col = None
        for candidate in ["ek", "ekl", "ertragsklasse", "yield_class", "si",
                          "bon", "bonität", "bonitaet"]:
            if candidate in table_df.columns:
                ek_col = candidate
                break

        table_df = table_df.sort_values(age_col).reset_index(drop=True)

        mapped = species_map.get(species_latin)
        common_name = mapped.get("common_name", "")
        std_name = mapped.get("standardized_name", "")

        if ek_col:
            table_df[ek_col] = pd.to_numeric(
                table_df[ek_col], errors="coerce"
            )
            for ek_val, ek_df in table_df.groupby(ek_col):
                ek_df = ek_df.sort_values(age_col).reset_index(drop=True)
                if len(ek_df) < 2:
                    continue
                si = float(ek_val) if pd.notna(ek_val) else 0.0
                record = _build_forstpraxis_record(
                    ek_df, age_col, height_col, dbh_col, vol_col,
                    species_latin, common_name, std_name, si,
                )
                if record:
                    yield record
        else:
            record = _build_forstpraxis_record(
                table_df, age_col, height_col, dbh_col, vol_col,
                species_latin, common_name, std_name, 0.0,
            )
            if record:
                yield record


def _identify_forstpraxis_species(df: pd.DataFrame) -> Optional[str]:
    """Try to identify the species from a Forstpraxis table by scanning
    column names and cell values for German species names."""
    # Check column names first
    all_text = " ".join(str(c) for c in df.columns).lower()
    for name, latin in _FORSTPRAXIS_SPECIES.items():
        if name in all_text:
            return latin

    # Check first few rows of each column
    for col in df.columns:
        for val in df[col].head(5).astype(str):
            val_lower = val.lower()
            for name, latin in _FORSTPRAXIS_SPECIES.items():
                if name in val_lower:
                    return latin
    return None


def _build_forstpraxis_record(
    df: pd.DataFrame,
    age_col: str,
    height_col: Optional[str],
    dbh_col: Optional[str],
    vol_col: Optional[str],
    species_latin: str,
    common_name: str,
    std_name: str,
    site_index: float,
) -> Optional[YieldTableRecord]:
    """Build a YieldTableRecord from a Forstpraxis table block."""
    ages = df[age_col].tolist()
    heights = (
        [float(h) if pd.notna(h) else 0.0 for h in df[height_col]]
        if height_col else [0.0] * len(ages)
    )
    dbhs = (
        [float(d) if pd.notna(d) else 0.0 for d in df[dbh_col]]
        if dbh_col else [0.0] * len(ages)
    )
    volumes = (
        [float(v) if pd.notna(v) else 0.0 for v in df[vol_col]]
        if vol_col else []
    )

    si_tag = f"_si{site_index:.0f}" if site_index else ""
    record = YieldTableRecord(
        species_latin=species_latin,
        species_common=common_name,
        standardized_name=std_name,
        region="DE",
        management="normal",
        site_index=site_index,
        source="forstpraxis_et",
        table_id=f"forstpraxis_{std_name}{si_tag}",
        ages=ages,
        heights=heights,
        dbhs=dbhs,
        volumes=volumes,
    )

    issues = record.validate()
    if issues:
        logger.debug(
            "Skipping Forstpraxis %s (si=%.0f): %s",
            species_latin, site_index, "; ".join(issues),
        )
        return None
    return record


_MODEL_TYPES = {
    "chapman_richards": lambda t, params: (
        params.get("y0", 0.0)
        + (params["A"] - params.get("y0", 0.0))
        * (1.0 - np.exp(-params["k"] * t)) ** params["p"]
    ),
    "korf": lambda t, params: (
        params["A"]
        * np.exp(-params["k"] * np.where(t > 0, t, 0.001) ** (-params["p"]))
    ),
    "lundqvist": lambda t, params: (
        params["A"]
        * np.exp(-params["k"] * np.where(t > 0, t, 0.001) ** params["p"])
    ),
}


def _evaluate_parametric_model(
    model_def: Dict[str, Any],
    species_map: SpeciesMapping,
) -> Optional[YieldTableRecord]:
    """Evaluate a parametric growth model on an age grid."""
    latin = model_def.get("species_latin", "")
    if not latin:
        logger.warning("Model missing species_latin")
        return None

    age_range = model_def.get("age_range", [0, 200])
    age_step = model_def.get("age_step", 5)
    ages = list(range(int(age_range[0]), int(age_range[1]) + 1, int(age_step)))
    ages_arr = np.array(ages, dtype=float)

    h_model = model_def.get("height_model")
    heights = [0.0] * len(ages)
    if h_model:
        model_type = h_model.get("type", "chapman_richards")
        eval_fn = _MODEL_TYPES.get(model_type)
        if eval_fn:
            params = {k: v for k, v in h_model.items() if k != "type"}
            heights = np.maximum(eval_fn(ages_arr, params), 0.0).tolist()

    d_model = model_def.get("dbh_model")
    dbhs = [0.0] * len(ages)
    if d_model:
        model_type = d_model.get("type", "chapman_richards")
        eval_fn = _MODEL_TYPES.get(model_type)
        if eval_fn:
            params = {k: v for k, v in d_model.items() if k != "type"}
            dbhs = np.maximum(eval_fn(ages_arr, params), 0.0).tolist()

    mapped = species_map.get(latin)

    record = YieldTableRecord(
        species_latin=latin,
        species_common=mapped.get("common_name", ""),
        standardized_name=mapped.get("standardized_name", ""),
        region=model_def.get("region", ""),
        management="modeled",
        site_index=model_def.get("site_index", 0.0),
        source="parametric_models",
        table_id=model_def.get("source_reference", ""),
        ages=ages,
        heights=heights,
        dbhs=dbhs,
    )

    issues = record.validate()
    if issues:
        logger.warning(
            "Parametric model for %s has issues: %s",
            latin, "; ".join(issues),
        )
        return None

    return record


# ---------------------------------------------------------------------------
# Provider implementations
# ---------------------------------------------------------------------------


class ForestElementsProvider(YieldProvider):
    """Extract yield tables from the ForestElementsR R package."""

    name = "forest_elements"
    description = "ForestElementsR: Central European classical yield tables (Wiedemann, Schober, etc.)"

    def available(self) -> bool:
        return _r_package_available("ForestElementsR")

    def iter_tables(
        self,
        species_mapping: Optional[SpeciesMapping] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Iterable[YieldTableRecord]:
        r_script = _get_bundled_r_script("extract_forest_elements.R")
        if not Path(str(r_script)).exists():
            logger.error("R script not found: %s", r_script)
            return
        mapping = _ensure_mapping(species_mapping)
        yield from _run_r_extraction(r_script, "forest_elements", mapping)

    def status_message(self) -> str:
        if self.available():
            return "available (R + ForestElementsR installed)"
        if shutil.which("Rscript"):
            return "R found but ForestElementsR package not installed"
        return "R not found on PATH"


class EtNwfvaProvider(YieldProvider):
    """Extract yield tables from the et.nwfva R package."""

    name = "et_nwfva"
    description = "et.nwfva: NW-FVA yield tables for NW Germany (spruce, pine, beech, oak, Douglas-fir)"

    def available(self) -> bool:
        return _r_package_available("et.nwfva")

    def iter_tables(
        self,
        species_mapping: Optional[SpeciesMapping] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Iterable[YieldTableRecord]:
        r_script = _get_bundled_r_script("extract_et_nwfva.R")
        if not Path(str(r_script)).exists():
            logger.error("R script not found: %s", r_script)
            return
        mapping = _ensure_mapping(species_mapping)
        yield from _run_r_extraction(r_script, "et_nwfva", mapping)

    def status_message(self) -> str:
        if self.available():
            return "available (R + et.nwfva installed)"
        if shutil.which("Rscript"):
            return "R found but et.nwfva package not installed"
        return "R not found on PATH"


class CarbonEtXlsxProvider(YieldProvider):
    """Parse Schober-based yield tables from C_ET_pub.xlsx (OpenAgrar)."""

    name = "carbon_et_xlsx"
    description = "Kohlenstoff-Ertragstafeln: Schober tables in XLSX (spruce, pine, beech, oak, Douglas-fir)"

    def available(self) -> bool:
        try:
            import openpyxl  # noqa: F401
            return True
        except ImportError:
            return False

    def iter_tables(
        self,
        species_mapping: Optional[SpeciesMapping] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Iterable[YieldTableRecord]:
        config = config or {}
        xlsx_path = Path(config.get("xlsx_path", ""))
        if not xlsx_path.is_absolute() or not xlsx_path.exists():
            logger.warning(
                "XLSX file not found: %s -- provide xlsx_path in config",
                xlsx_path,
            )
            return
        mapping = _ensure_mapping(species_mapping)
        yield from _parse_carbon_et_xlsx(xlsx_path, mapping)

    def status_message(self) -> str:
        if not self.available():
            return "openpyxl not installed (pip install openpyxl)"
        return "available (openpyxl installed)"


class ForestYieldPdfProvider(YieldProvider):
    """Extract yield tables from UK Forest Yield (FC Booklet 48) PDF."""

    name = "forest_yield_uk"
    description = "UK Forest Yield (FC Booklet 48): British species yield tables"

    def available(self) -> bool:
        return _tabula_available()

    def iter_tables(
        self,
        species_mapping: Optional[SpeciesMapping] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Iterable[YieldTableRecord]:
        config = config or {}
        pdf_path = Path(config.get("pdf_path", ""))
        if not pdf_path.is_absolute() or not pdf_path.exists():
            logger.warning(
                "PDF not found: %s -- provide pdf_path in config", pdf_path,
            )
            return
        mapping = _ensure_mapping(species_mapping)
        yield from _parse_forest_yield_pdf(pdf_path, mapping)

    def status_message(self) -> str:
        if not self.available():
            return "tabula-py not installed (pip install tabula-py; requires Java)"
        return "available (tabula-py installed)"


class PryorPdfProvider(YieldProvider):
    """Extract wild cherry yield tables from Pryor FC Bulletin 75."""

    name = "pryor_cherry"
    description = "Pryor: Wild cherry (Prunus avium) yield tables from FC Bulletin 75"

    def available(self) -> bool:
        return _tabula_available()

    def iter_tables(
        self,
        species_mapping: Optional[SpeciesMapping] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Iterable[YieldTableRecord]:
        config = config or {}
        pdf_path = Path(config.get("pdf_path", ""))
        if not pdf_path.is_absolute() or not pdf_path.exists():
            logger.warning(
                "PDF not found: %s -- provide pdf_path in config", pdf_path,
            )
            return
        mapping = _ensure_mapping(species_mapping)
        yield from _parse_pryor_pdf(pdf_path, mapping)

    def status_message(self) -> str:
        if not self.available():
            return "tabula-py not installed"
        return "available (tabula-py installed)"


class NovaScotiaPdfProvider(YieldProvider):
    """Extract yield tables from Nova Scotia softwood report PDF."""

    name = "nova_scotia"
    description = "Nova Scotia: Revised normal yield tables for Canadian softwoods"

    def available(self) -> bool:
        return _tabula_available()

    def iter_tables(
        self,
        species_mapping: Optional[SpeciesMapping] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Iterable[YieldTableRecord]:
        config = config or {}
        pdf_path = Path(config.get("pdf_path", ""))
        if not pdf_path.is_absolute() or not pdf_path.exists():
            logger.warning(
                "PDF not found: %s -- provide pdf_path in config", pdf_path,
            )
            return
        mapping = _ensure_mapping(species_mapping)
        yield from _parse_nova_scotia_pdf(pdf_path, mapping)

    def status_message(self) -> str:
        if not self.available():
            return "tabula-py not installed"
        return "available (tabula-py installed)"


class UsdaStockingPdfProvider(YieldProvider):
    """Extract yield tables from USDA stocking/yield tables PDF."""

    name = "usda_stocking"
    description = "USDA: Forest stocking and yield tables (hardwood/softwood)"

    def available(self) -> bool:
        return _tabula_available()

    def iter_tables(
        self,
        species_mapping: Optional[SpeciesMapping] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Iterable[YieldTableRecord]:
        config = config or {}
        pdf_path = Path(config.get("pdf_path", ""))
        if not pdf_path.is_absolute() or not pdf_path.exists():
            logger.warning(
                "PDF not found: %s -- provide pdf_path in config", pdf_path,
            )
            return
        mapping = _ensure_mapping(species_mapping)
        yield from _parse_usda_pdf(pdf_path, mapping)

    def status_message(self) -> str:
        if not self.available():
            return "tabula-py not installed"
        return "available (tabula-py installed)"


class ForItProvider(YieldProvider):
    """Extract volume/phytomass equations from the ForIT R package (Italian NFI).

    ForIT implements the INFC-2005 double-entry volume and phytomass equations
    for Italian forest tree species (Tabacchi et al. 2011).  It covers 50+
    species including minor broadleaves like Acer campestre.
    """

    name = "forit"
    description = "ForIT: Italian NFI volume and phytomass equations (Tabacchi et al. 2011)"

    def available(self) -> bool:
        return _r_package_available("ForIT")

    def iter_tables(
        self,
        species_mapping: Optional[SpeciesMapping] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Iterable[YieldTableRecord]:
        r_script = _get_bundled_r_script("extract_forit.R")
        if not Path(str(r_script)).exists():
            logger.error("R script not found: %s", r_script)
            return
        mapping = _ensure_mapping(species_mapping)
        yield from _run_r_extraction(r_script, "forit", mapping)

    def status_message(self) -> str:
        if self.available():
            return "available (R + ForIT installed)"
        if shutil.which("Rscript"):
            return "R found but ForIT package not installed"
        return "R not found on PATH"


class ForstpraxisPdfProvider(YieldProvider):
    """Parse German yield table extracts from Forstpraxis Ertragstafelauszuge PDF.

    The AFZ/FHJ Kalender Ertragstafelauszuge PDF compiles yield table extracts
    for ~20 German species in standardized 10-year age intervals.  This covers
    species not found in other providers, including hornbeam (Lockow 2009) and
    small-leaved linden (Bockmann 1990).
    """

    name = "forstpraxis_et"
    description = (
        "Forstpraxis Ertragstafelauszuge: German yield table extracts "
        "(hornbeam, linden, and others)"
    )

    def available(self) -> bool:
        return _tabula_available()

    def iter_tables(
        self,
        species_mapping: Optional[SpeciesMapping] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Iterable[YieldTableRecord]:
        config = config or {}
        pdf_path = Path(config.get("pdf_path", ""))
        if not pdf_path.is_absolute() or not pdf_path.exists():
            logger.warning(
                "PDF not found: %s -- provide pdf_path in config", pdf_path,
            )
            return
        mapping = _ensure_mapping(species_mapping)
        yield from _parse_forstpraxis_pdf(pdf_path, mapping)

    def status_message(self) -> str:
        if not self.available():
            return "tabula-py not installed (pip install tabula-py; requires Java)"
        return "available (tabula-py installed)"


class ParametricModelProvider(YieldProvider):
    """Generate synthetic yield tables from parametric growth model parameters.

    Reads JSON model files from a configured directory. Each file defines a
    growth function (Chapman-Richards, Korf, Lundqvist) with fitted parameters
    and a valid age range.
    """

    name = "parametric_models"
    description = "Parametric: Synthetic tables from published H-D-A growth model equations"

    def available(self) -> bool:
        return True

    def iter_tables(
        self,
        species_mapping: Optional[SpeciesMapping] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Iterable[YieldTableRecord]:
        config = config or {}
        models_dir = Path(config.get("models_dir", ""))
        if not models_dir.is_absolute() or not models_dir.exists():
            logger.info("Parametric models dir not found: %s", models_dir)
            return

        mapping = _ensure_mapping(species_mapping)
        import json

        for model_file in sorted(models_dir.glob("*.json")):
            try:
                with open(model_file) as f:
                    model_def = json.load(f)
                record = _evaluate_parametric_model(model_def, mapping)
                if record:
                    yield record
            except Exception as e:
                logger.warning("Error processing %s: %s", model_file.name, e)


# ---------------------------------------------------------------------------
# Provider registry
# ---------------------------------------------------------------------------


ALL_PROVIDERS: List[YieldProvider] = [
    ForestElementsProvider(),
    EtNwfvaProvider(),
    CarbonEtXlsxProvider(),
    ForestYieldPdfProvider(),
    PryorPdfProvider(),
    NovaScotiaPdfProvider(),
    UsdaStockingPdfProvider(),
    ForItProvider(),
    ForstpraxisPdfProvider(),
    ParametricModelProvider(),
]


def get_all_providers() -> List[YieldProvider]:
    """Return all registered providers."""
    return list(ALL_PROVIDERS)


def get_available_providers() -> List[YieldProvider]:
    """Return only providers whose dependencies are met."""
    return [p for p in ALL_PROVIDERS if p.available()]


def get_provider_by_name(name: str) -> Optional[YieldProvider]:
    """Look up a provider by its short name."""
    for p in ALL_PROVIDERS:
        if p.name == name:
            return p
    return None
