# Changelog

All notable user-facing changes to this project are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2026-07-27

### Added

- `.github/workflows/ci.yml` — there was no CI.

### Fixed

- `store.py` annotated `add(record: "YieldTableRecord")` but only imported
  the name inside the function body, leaving it unresolved at module scope
  (ruff F821). Moved to a `TYPE_CHECKING` import.
- `test_mixed_effects.py` imported `patsy`/`statsmodels` at module scope
  with no guard; those live in the optional `[stats]` extra, so a base
  install turned a missing optional dependency into a collection error that
  aborted the entire suite (exit 2, zero tests run) instead of skipping one
  module. Now uses `pytest.importorskip`.

### Changed

- README's Zenodo DOI badge switched to a static shields.io badge — the
  dynamic badge endpoint was intermittently failing GitHub's image proxy.

## [0.1.0] - 2026-07-23

Initial release: H–D model forms, biomass and crown equations, fitting with
AIC/AICc model selection, published-equation registry, `Tree`/`Stand`
dataclasses, multi-source yield-table ingestion and offline resolution.

### Added

- MIT `LICENSE` file.
- `[project.scripts]` entry for the `pylometree-ingest` CLI so it is
  installed on `pip install`.
- `docs/` expanded: architecture overview, full API reference, and tutorials
  for H–D fitting, biomass estimation, and yield tables.
- `.editorconfig` for cross-editor consistency.
- `CONTRIBUTING.md` with contribution workflow.
- `CHANGELOG.md` (this file).
- `tests/test_io.py`: extended to 14 tests covering `stand_from_csv` alias,
  `stand_to_dataframe`, custom column names, `species_col=None`, and string
  path inputs.
- `tests/test_crown_models.py`: 13 tests for crown-based allometric models
  (`agb_from_crown`, Jucker 2017, DBH-from-crown, geometry conversions,
  crown ratio, and catalogue smoke-test).
- `tests/test_volume_models.py`: 18 tests for volume models (cylinder,
  form-factor, power-law, conoid frustum, volume→AGB) and Chapman-Richards
  height-age with inverse roundtrip.
- `tests/test_registry.py`: 16 additional tests covering `to_dict`
  serialisation, missing-covariate `ValueError`, registry `__call__`
  shortcut, `pub_year_min` / `response` filters, isolated `ModelRegistry`
  operations (register_many, summary, summary_df).

### Changed

- Internal phases roadmap moved from repo root to
  `docs/internal-phases-roadmap.md`.
- Python version requirement from `>=3.10` to `>=3.12`.

### Removed

- Empty `build/` directory removed from version control.
- Local `.mypy_cache/` and `.pytest_cache/` directories removed.
