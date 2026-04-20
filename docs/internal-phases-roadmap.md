# pylometree — Implementation Plan: Phases 3–7 (Detailed Task Breakdown)

This document provides actionable, self-contained tasks for each remaining phase of the pylometree improvement plan. Each phase is broken down into sub-tasks with clear objectives, file/module targets, and acceptance criteria. Use this as a handoff or checklist for individual or parallel implementation.

---

## Phase 3: Test Coverage Expansion

**Goal:** Achieve comprehensive test coverage for all major modules, especially crown, volume, io, and registry. Target ≥140 tests.

### 3.1 Add `tests/test_crown.py`

- **Target:** `src/pylometree/models/crown.py`
- **Tasks:**
  - Parametrize over `CROWN_MODELS.items()`
  - `TestMonotonicity`: AGB increases with H and CA
  - `TestOutputShape`: output shape matches input
  - `TestSpecific`: known value for `jucker2017_agb`, roundtrip for `crown_area_from_diameter`/`crown_diameter_from_area`, `crown_ratio` in [0,1]
- **Acceptance:** All crown model functions are tested for monotonicity, shape, and correctness.

### 3.2 Add `tests/test_volume.py`

- **Target:** `src/pylometree/models/volume.py`
- **Tasks:**
  - `TestVolumeCylinder`: known values (DBH=20cm, H=15m)
  - `TestFormFactor`: output < cylinder, form_factor=1.0 equals cylinder
  - `TestConoidFrustum`: known geometry
  - `TestVolumeToAGB`: unit conversion correctness
  - `TestHeightAge`: `height_from_age_cr` asymptote, `age_from_height_cr` inverse roundtrip
  - `TestCRSpeciesParams`: all 5 species in `CR_SPECIES_PARAMS` produce valid heights
- **Acceptance:** All volume and height-age functions are covered with correctness and edge-case tests.

### 3.3 Add `tests/test_io.py`

- **Target:** `src/pylometree/io/__init__.py`
- **Tasks:**
  - Create a small temp CSV, load with `read_csv`, verify Stand has correct trees
  - Test missing columns, empty file, extra columns
  - Test `stand_to_dataframe` roundtrip
- **Acceptance:** All I/O helpers are tested for normal and edge cases.

### 3.4 Add `tests/test_published_registry.py`

- **Target:** `src/pylometree/registry/published.py`
- **Tasks:**
  - Parametrize over `registry.list_ids()`
  - For each entry: call `.predict()` with reasonable covariate values, assert output is positive and finite
- **Acceptance:** All published registry entries are validated for predictability and output sanity.

### 3.5 Expand existing tests

- **Targets:** `tests/test_fitting.py`, `tests/test_biomass.py`, `tests/test_data.py`
- **Tasks:**
  - Add tests for `select_model` with `criterion="r2"`, `criterion="bic"`; test non-convergence; test empty array input
  - Add `m2_height` test, parametrize monotonicity over `BIOMASS_MODELS.items()`
  - Add empty Stand tests, fix any missed assertions
- **Acceptance:** All core fitting, biomass, and data classes have robust, edge-case-aware tests.

### Verification

- Run `pytest -v --tb=short` — all tests pass
- Run `pytest --co -q` — target ≥140 tests

---

## Phase 4: Architecture Improvements

**Goal:** Improve maintainability and type safety of the codebase.

### 4.1 Split `providers.py` into a package

- **Target:** `src/pylometree/yield_tables/providers/`
- **Tasks:**
  - Move each provider class to its own module (see plan for file breakdown)
  - Move shared helpers to `_base.py`
  - Preserve all imports in `__init__.py` for backward compatibility
- **Acceptance:** All provider logic is modularized, imports are backward compatible, and tests pass.

### 4.2 Type the model catalogues

- **Target:** `src/pylometree/models/_types.py`, all model catalogue modules
- **Tasks:**
  - Create `CatalogueEntry` TypedDict
  - Update type annotations on `HD_MODELS`, `BIOMASS_MODELS`, `CROWN_MODELS`
  - Update `select_model` signature to accept `dict[str, CatalogueEntry]`
- **Acceptance:** All model catalogues are type-annotated, and mypy passes with no new errors.

### Verification

- Run `pytest -v` — no regressions
- Run `mypy src/pylometree/ --ignore-missing-imports` — no new errors

---

## Phase 5: Workspace Hygiene

**Goal:** Ensure the repository is clean, well-documented, and ready for distribution.

### 5.1 Add LICENSE file

- **Target:** `LICENSE` in repo root
- **Tasks:**
  - Add MIT license text, copyright holder from pyproject.toml
- **Acceptance:** LICENSE file exists and is correct

### 5.2 Add CHANGELOG.md

- **Target:** `CHANGELOG.md` in repo root
- **Tasks:**
  - Create with `## [0.1.0] - Unreleased` section listing current features
- **Acceptance:** CHANGELOG.md exists and is up to date

### 5.3 Add py.typed marker

- **Target:** `src/pylometree/py.typed`
- **Tasks:**
  - Create empty file for PEP 561 compliance
- **Acceptance:** py.typed exists and is included in sdist/wheel

### 5.4 Add yield_tables R scripts README

- **Target:** `src/pylometree/yield_tables/r_scripts/README.md`
- **Tasks:**
  - Document what each R script does and when invoked
- **Acceptance:** README exists and is clear

### 5.5 Review .gitignore

- **Target:** `.gitignore` in repo root
- **Tasks:**
  - Ensure all build, test, and data artifacts are ignored
- **Acceptance:** .gitignore is up to date

### Verification

- `ls LICENSE CHANGELOG.md src/pylometree/py.typed` all exist
- `pip install -e .` still works

---

## Phase 6: Documentation Polish

**Goal:** Ensure all docstrings and documentation are complete, accurate, and consistent.

### 6.1 Add missing Returns sections to docstrings

- **Targets:** `src/pylometree/models/volume.py`, `src/pylometree/models/crown.py`, all model files
- **Tasks:**
  - Add `Returns` sections to all public functions
- **Acceptance:** All model functions have complete docstrings

### 6.2 Fix inconsistent docstrings

- **Targets:** `src/pylometree/models/hd.py`, `src/pylometree/models/volume.py`
- **Tasks:**
  - Remove incorrect alternative form from `hyperbolic` (already done)
  - Clarify confusing note in `volume_to_agb`
- **Acceptance:** All docstrings are accurate and clear

### 6.3 Update species-reference.md

- **Target:** `docs/species-reference.md`
- **Tasks:**
  - Verify all registry entries are reflected
  - Add Pretzsch height-age entries to the allometric equations table
- **Acceptance:** species-reference.md is up to date

---

## Phase 7: New Features

**Goal:** Add new capabilities and user-facing features.

### 7.1 Stand.apply_model()

- **Target:** `src/pylometree/data/stand.py`
- **Tasks:**
  - Add method to apply a model to all trees in the stand
- **Acceptance:** Stand.apply_model() works and is tested

### 7.2 Plotting utilities

- **Target:** New module or `metrics/`
- **Tasks:**
  - Add basic plotting for model fits, residuals, etc.
- **Acceptance:** Plotting functions exist and are documented

### 7.3 Species auto-matching

- **Target:** `yield_tables/species.py` or registry
- **Tasks:**
  - Implement fuzzy species matching for registry and yield tables
- **Acceptance:** Species can be matched by common/Latin names

### 7.4 CLI improvements

- **Target:** `yield_tables/cli.py`
- **Tasks:**
  - Add new CLI commands or improve UX
- **Acceptance:** CLI is more user-friendly

### 7.5 Wood density database integration

- **Target:** New module or registry
- **Tasks:**
  - Integrate global wood density database for auto-filling `rho`
- **Acceptance:** Wood density lookup works

### Verification

- All new features are covered by tests and documented in README

---

**End of Plan**
