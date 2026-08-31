# Changelog

All notable user-facing changes to this project are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-08-31

### Added

- Five generalized European aboveground biomass equations from Forrester et al.
  (2017), *Forest Ecology and Management* 396:160–175
  (doi:10.1016/j.foreco.2017.04.011), transcribed from Table A.5 of the authors'
  published database (doi:10.17632/4jytx9s44j.1):
  *Abies alba*, *Fagus sylvatica*, *Larix decidua*, *Picea abies*,
  *Quercus robur*.

  Diameter-only form (the paper's equation 3):

  ```
  ln(B) = ln(b0) + beta · ln(d)   =>   B = exp(ln_b0) · CF · d^beta
  ```

  The Baskerville correction factor `CF` is folded into `a` so each entry is a
  plain power law usable through `m1_dbh`; `parameters` keeps `ln_b0`, `beta`
  and `cf` alongside it so every value can be checked against the source.

  These are preferable to the Zianis entries for the species they share. They
  are fitted over far wider diameter ranges (*Picea* 1–82 cm against Zianis'
  11–47 cm) on much larger samples (*Picea* n=576 against n=17), and they cover
  *Abies alba*, *Larix decidua* and *Quercus robur*, for which Zianis has no
  aboveground equation at all.

  *Quercus petraea* and *Pseudotsuga menziesii* have no diameter-only
  aboveground row in Table A.5; Douglas fir remains available via Zianis eq. 526.

## [0.2.0] - 2026-08-31

### Added

- Nine total-aboveground-biomass equations for European species from Zianis et
  al. (2005), *Biomass and stem volume equations for tree species in Europe*,
  Silva Fennica Monographs 4 (doi:10.14214/sf.sfm4). Until now every biomass
  entry in the registry was pantropical (Chave 2014, Jucker 2017) or a banana
  model, so there was nothing usable for a Central European forest.

  | Species | Appendix A equations |
  |---|---|
  | *Fagus sylvatica* | 88, 90, 91, 92 |
  | *Picea abies* | 141, 151 |
  | *Pinus sylvestris* | 328, 334 |
  | *Pseudotsuga menziesii* | 526 |

  Only equations for component **AB** (total aboveground biomass) in form M1
  (`a·D^b`) or M4 (`a·D^b·H^c`), with biomass in kg, D in cm and H in m, were
  taken. Each `model_id` embeds its Appendix A equation number so an entry can
  be checked against the source, and `notes` carries sample size, r², the
  fitted DBH range and the country — the DBH range being what decides whether
  an equation may be applied to a given stand.

  *Quercus robur*, *Quercus petraea*, *Abies alba* and *Larix decidua* have no
  qualifying equation in the monograph and are deliberately absent rather than
  approximated by a congener. The two *Pinus sylvestris* entries were fitted on
  2–16 cm saplings and are noted as unsuitable for mature stands.

### Fixed

- The `dev` branch had not received the 0.1.2 release made on `main`, leaving
  its `pyproject.toml` on 0.1.1 while `CITATION.cff` read 0.1.2. Reconciled in
  this merge; all three sources now agree.

## [0.1.2] - 2026-07-29

### Removed

- `.github/copilot-instructions.md`, `AGENTS.md`, and `CLAUDE.md` from
  `main` — dev-workflow tooling, not project documentation; they now live
  on a `dev` branch instead.
- A tracked personal `.vscode/settings.json` that hardcoded the
  maintainer's local Windows username and conda path; untracked and
  widened `.gitignore` to the whole `.vscode/` directory.


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
