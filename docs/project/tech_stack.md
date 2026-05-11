# Technology Stack: pylometree

**Document Version:** 1.0
**Date:** 2026-05-11
**Status:** Active

<!-- SCOPE: Technology stack (specific versions, libraries, frameworks), development tools, naming conventions ONLY. -->
<!-- DOC_KIND: reference -->
<!-- DOC_ROLE: canonical -->
<!-- READ_WHEN: Read when you need exact technologies, versions, tooling, or dependency choices. -->
<!-- SKIP_WHEN: Skip when you only need business scope, runtime procedures, or allometric formula details. -->
<!-- PRIMARY_SOURCES: pyproject.toml, src/pylometree/, docs/project/architecture.md -->

## Quick Navigation

- [Docs Hub](../README.md)
- [Requirements](requirements.md)
- [Architecture](architecture.md)
- [API Reference](../api-reference.md)

## Agent Entry

| Signal | Value |
|--------|-------|
| Purpose | Lists the actual stack, versions, tooling, and rationale for selected technologies in pylometree. |
| Read When | You need exact library, runtime, or tool choices and their versions. |
| Skip When | You only need workflow instructions or feature scope. |
| Canonical | Yes |
| Next Docs | [Architecture](architecture.md), [Requirements](requirements.md) |
| Primary Sources | `pyproject.toml`, `src/pylometree/` |

---

## 1. Introduction

### 1.1 Purpose

This document specifies the technology stack, dependencies, tooling, and naming conventions used in **pylometree** v0.1.0.

### 1.2 Scope

**IN SCOPE:** Python runtime, required and optional dependencies, dev tooling, naming conventions.
**OUT OF SCOPE:** Infrastructure provisioning, deployment procedures, API contracts, yield-table provider runtime setup (covered in tutorials).

---

## 2. Technology Stack

### 2.1 Stack Overview

| Layer | Technology | Version | Rationale |
|-------|------------|---------|-----------|
| **Language** | Python | 3.12+ (3.13 also supported) | Modern typing, `match` statements, performance improvements |
| **Build system** | setuptools | ≥61 | Standard PEP 517 build; src layout support |
| **Build backend** | wheel | latest | Standard wheel packaging |
| **Numerical math** | NumPy | ≥1.24 | Vectorized array operations in all model functions |
| **Curve fitting** | SciPy | ≥1.10 | `scipy.optimize.curve_fit` with covariance; `scipy.stats` for CIs |
| **Data wrangling** | pandas | ≥2.0 | DataFrame I/O adapters; yield-table normalization |
| **ML model selection** | scikit-learn | ≥1.3 | Optional `[ml]` extra — ML-augmented model selection |
| **Statistical models** | statsmodels | ≥0.14 | Optional `[stats]` extra — OLS/WLS evaluation |
| **Testing** | pytest | ≥7.4 | Unit and integration tests; `dev` extra |
| **Test coverage** | pytest-cov | ≥4.1 | Coverage reports; `dev` extra |
| **Package manager** | pip / uv | — | `pip install -e ".[dev]"` or uv-compatible |

### 2.2 Dependency Matrix

**Required (always installed):**

| Package | Version | Used In |
|---------|---------|---------|
| numpy | ≥1.24 | `models/`, `fitting/`, `metrics/`, `yield_tables/` |
| scipy | ≥1.10 | `fitting/nonlinear.py` (curve_fit, bootstrap) |
| pandas | ≥2.0 | `io/`, `yield_tables/providers.py`, `yield_tables/loaders.py` |

**Optional extras:**

| Extra | Package | Version | When Needed |
|-------|---------|---------|-------------|
| `[ml]` | scikit-learn | ≥1.3 | ML-augmented model selection |
| `[stats]` | statsmodels | ≥0.14 | OLS/WLS metric evaluation |
| `[dev]` | pytest | ≥7.4 | Running test suite |
| `[dev]` | pytest-cov | ≥4.1 | Coverage reports |
| `[all]` | all of the above | — | Full install |

**Yield-table provider runtime deps (not installed by pylometree):**

| Provider | Runtime Dependency | Install Responsibility |
|----------|--------------------|----------------------|
| ForestElementsR (14 spp) | R + `ForestElementsR` package | User |
| et.nwfva (5 spp) | R + `et.nwfva` package | User |
| carbon_et_xlsx | openpyxl | User (or `pip install openpyxl`) |
| UK FC Bulletin 75, USDA PDF | tabula-py + Java 8+ | User |

---

## 3. Development Environment

### 3.1 Required Tools

| Tool | Version | Purpose | Installation |
|------|---------|---------|--------------|
| Python | 3.12+ | Runtime | https://www.python.org/downloads/ |
| pip | latest | Package install | bundled with Python |
| uv | latest (optional) | Fast package install | https://docs.astral.sh/uv/ |
| Git | 2.40+ | Version control | https://git-scm.com/ |

### 3.2 Setup Commands

| Task | Command |
|------|---------|
| Install dev deps | `pip install -e ".[dev]"` |
| Install all extras | `pip install -e ".[all]"` |
| Run tests | `pytest` |
| Run tests (verbose) | `pytest -v --tb=short` |
| Check yield-table CLI | `pylometree-ingest --help` |

### 3.3 Code Quality Tools

| Tool | Purpose | Config File | Command |
|------|---------|-------------|---------|
| Black | Code formatting (88-char line width) | `pyproject.toml` | `black src/ tests/` |
| ruff | Linting | `pyproject.toml` | `ruff check .` |
| basedpyright / mypy | Type checking | — | `basedpyright` or `mypy src/` |
| pytest-cov | Coverage | `pyproject.toml` | `pytest --cov=pylometree` |

pytest configuration in `pyproject.toml`:
- `testpaths = ["tests"]`
- `addopts = "-v"`

---

## 4. Package Layout

### 4.1 Src Layout

pylometree uses a src layout. The installable package lives entirely under `src/pylometree/`:

| Path | Contents |
|------|----------|
| `src/pylometree/models/` | Pure equation functions: `hd.py`, `biomass.py`, `crown.py`, `volume.py` |
| `src/pylometree/fitting/` | `nonlinear.py` — curve_fit wrapper, bootstrap, `select_model` |
| `src/pylometree/metrics/` | R², RMSE, MAE, AIC, AICc, MSA, SSPB |
| `src/pylometree/registry/` | `base.py` (ModelEntry, ModelRegistry), `published.py` |
| `src/pylometree/data/` | `tree.py`, `stand.py`, `constants.py` |
| `src/pylometree/io/` | CSV/DataFrame → Tree/Stand adapters |
| `src/pylometree/yield_tables/` | Full ingestion/resolution subsystem + CLI |

### 4.2 Test Layout

| Path | Contents |
|------|----------|
| `tests/test_hd_models.py` | H-D equation correctness |
| `tests/test_biomass.py` | AGB equation correctness |
| `tests/test_crown_models.py` | Crown AGB equations |
| `tests/test_volume_models.py` | Stem volume equations |
| `tests/test_fitting.py` | curve_fit wrapper, bootstrap, select_model |
| `tests/test_metrics.py` | Metric function correctness |
| `tests/test_registry.py` | Registry register/get/query |
| `tests/test_data.py` | Tree/Stand dataclass behavior |
| `tests/test_io.py` | CSV/DataFrame ingestion |

---

## 5. Naming Conventions

### 5.1 Variable Naming

| Convention | Scope | Example |
|------------|-------|---------|
| allometric R convention | Public function parameters | `dsob`, `hst`, `vsia`, `agb`, `bgb` |
| snake_case | All Python identifiers | `fit_model`, `model_entry`, `select_model` |
| UPPER_SNAKE_CASE | Module-level constants | `CARBON_FRACTION`, `_MODELS` (private) |
| PascalCase | Classes | `ModelEntry`, `ModelRegistry`, `YieldProvider` |

### 5.2 File Naming

| Convention | Scope | Example |
|------------|-------|---------|
| snake_case | All Python modules | `nonlinear.py`, `published.py` |
| Singular noun | Module names | `tree.py`, `stand.py` (not `trees.py`) |

### 5.3 Model Identifiers

ModelEntry `model_id` follows the pattern: `{first_author}{year}_{descriptor}`:

| Pattern | Example |
|---------|---------|
| `{author}{year}_{descriptor}` | `chave2014_pantropical`, `jucker2017_crown_agb` |
| `{descriptor}_generic_{type}` | `chapman_richards_generic_hd` |
| `pretzsch{year}_{species}_{type}` | `pretzsch2025_picea_height_age` |

### 5.4 model_type Values

Strict strings used in `ModelEntry.model_type` and `registry.query(model_type=...)`:

| Value | Equation category |
|-------|-----------------|
| `"hd"` | Height–diameter |
| `"agb"` | Above-ground biomass |
| `"bgb"` | Below-ground biomass |
| `"volume"` | Stem volume |
| `"crown_agb"` | Crown-area/height → AGB |
| `"crown_dbh"` | Crown area → DBH |
| `"age_height"` | Height–age growth |

Note: `"agb"` does NOT match `"crown_agb"`. Use `registry.query(response="agb")` for looser matching.

---

## Maintenance

**Last Updated:** 2026-05-11

**Update Triggers:**
- Dependency version bumps in `pyproject.toml`
- New optional extra added
- New yield-table provider runtime dep documented
- Code quality tool added or replaced

**Verification:**
- [ ] All versions match `pyproject.toml`
- [ ] Optional extras table matches `[project.optional-dependencies]` in `pyproject.toml`
- [ ] `model_type` values table matches values used in `src/pylometree/registry/published.py`

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-05-11 | ln-112-project-core-creator | Initial version |
