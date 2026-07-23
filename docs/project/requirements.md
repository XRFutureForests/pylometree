# Requirements Specification: pylometree

**Document Version:** 1.0
**Date:** 2026-05-11
**Status:** Active
**Standard Compliance:** ISO/IEC/IEEE 29148:2018

<!-- SCOPE: Functional requirements (FR-XXX-NNN) with MoSCoW prioritization, acceptance criteria, constraints, assumptions, traceability ONLY. -->
<!-- DOC_KIND: explanation -->
<!-- DOC_ROLE: canonical -->
<!-- READ_WHEN: Read when you need product scope, functional requirements, or acceptance boundaries. -->
<!-- SKIP_WHEN: Skip when you only need implementation details, operations, or low-level schema facts. -->
<!-- PRIMARY_SOURCES: README.md, docs/project/architecture.md, docs/project/tech_stack.md, pyproject.toml -->

## Quick Navigation

- [Docs Hub](../README.md)
- [Architecture](architecture.md)
- [Tech Stack](tech_stack.md)
- [API Reference](../api-reference.md)

## Agent Entry

| Signal | Value |
|--------|-------|
| Purpose | Defines functional scope, business expectations, and acceptance boundaries for pylometree. |
| Read When | You need feature scope, priorities, or requirement traceability. |
| Skip When | You only need implementation details, runtime procedures, or formula lookup. |
| Canonical | Yes |
| Next Docs | [Architecture](architecture.md), [Tech Stack](tech_stack.md) |
| Primary Sources | `README.md`, `docs/project/architecture.md`, `pyproject.toml` |

---

## 1. Introduction

### 1.1 Purpose

This document specifies the functional requirements for **pylometree** — a general-purpose Python toolkit for tree allometry covering fitting, evaluating, and looking up allometric equations for height–diameter relationships, above- and below-ground biomass, crown structure, stem volume, and height–age growth.

### 1.2 Scope

**IN SCOPE:** Allometric equation library (H-D, AGB, BGB, crown, volume), model fitting and selection, metrics, searchable registry of published equations, domain data classes (Tree, Stand), CSV/DataFrame I/O adapters, and a yield-table ingestion/resolution subsystem with CLI.

**OUT OF SCOPE:** Field data collection, LiDAR processing, database storage, visualization, and web APIs.

### 1.3 Intended Audience

- Forest scientists and researchers
- Python developers integrating allometric calculations
- XR Future Forests Lab — growpy and digital-twin-db consumers
- QA and test engineers

### 1.4 References

- Architecture: [architecture.md](architecture.md)
- API Reference: [../api-reference.md](../api-reference.md)
- GitLab issues: https://github.com/XRFutureForests/pylometree/issues

---

## 2. Overall Description

### 2.1 Product Perspective

pylometree is a standalone Python library. It is consumed as a git-based dependency (no PyPI release; see XRFF-131). Within the XR Future Forests Lab it is used by:

| Consumer | Usage |
|----------|-------|
| `growpy` | Yield-table-driven growth calibration |
| `digital-twin-db` | Compute derived attributes (biomass, predicted height) from stored measurements |

### 2.2 User Classes and Characteristics

| Class | Description |
|-------|-------------|
| Researcher / Data Scientist | Fits custom equations to field data; evaluates AIC, bootstrap CIs |
| Library Consumer (Python) | Imports registry entries; calls `predict()` on published models |
| DevOps / Automation | Runs `pylometree-ingest` CLI to populate the yield-table store |

### 2.3 Operating Environment

- Python 3.12 or 3.13; any OS supporting CPython (Linux, macOS, Windows)
- Yield-table providers require per-provider runtime deps (R, Java, openpyxl)
- No network access required at inference or resolution time

---

## 3. Functional Requirements

### 3.1 H-D Model Fitting and Selection

| ID | Priority | Requirement |
|----|----------|-------------|
| FR-HD-001 | MUST | Provide at least 12 height–diameter equation forms (Chapman-Richards, Korf, Michaelis-Menten, Logistic, Gompertz, Weibull, Power, Naslund, Meyer, Wykoff, Sigmoid, Hyperbola). |
| FR-HD-002 | MUST | Fit any H-D form to field data using `scipy.optimize.curve_fit` with convergence diagnostics. |
| FR-HD-003 | MUST | Return a `FitResult` with parameters, covariance matrix, and a `.predict()` method. |
| FR-HD-004 | MUST | Support AIC-based `select_model()` across all registered H-D forms. |
| FR-HD-005 | MUST | Compute bootstrap confidence intervals for fitted parameters. |

### 3.2 Biomass and Volume Equations

| ID | Priority | Requirement |
|----|----------|-------------|
| FR-BM-001 | MUST | Implement AGB power-law forms M1–M4 (DBH only; DBH+H; DBH+H+rho; DBH²H-based). |
| FR-BM-002 | MUST | Implement Chave 2014 pantropical AGB equation (DBH, H, wood density). |
| FR-BM-003 | MUST | Implement Musa NSUR AGB equations for banana (multi-response). |
| FR-BM-004 | MUST | Implement crown-area/height → AGB equations (Jucker 2017, Htoo 2025). |
| FR-BM-005 | MUST | Implement stem volume form-factor and power-law models. |
| FR-BM-006 | SHOULD | Apply Sprugel 1983 back-transformation bias correction explicitly in log-space models. |

### 3.3 Model Registry

| ID | Priority | Requirement |
|----|----------|-------------|
| FR-REG-001 | MUST | Provide `ModelEntry` dataclass bundling function, parameters, citation, units, species, and region. |
| FR-REG-002 | MUST | Provide `ModelRegistry` with `register()`, `get()`, and `query()` operations. |
| FR-REG-003 | MUST | `query()` supports filtering by `model_type`, `species`, `region`, `response`, and `pub_year_min`. |
| FR-REG-004 | MUST | Pre-load published equations on import (Chave 2014, Jucker 2017, Laskar 2020, Chapman-Richards, Pretzsch 2025, and others). |
| FR-REG-005 | MUST | Enforce strict `model_type` matching — `"agb"` does not match `"crown_agb"`. |
| FR-REG-006 | SHOULD | Allow callers to register custom equations via `registry.register(ModelEntry(...))`. |

### 3.4 Metrics

| ID | Priority | Requirement |
|----|----------|-------------|
| FR-MET-001 | MUST | Compute R², RMSE, MAE, and bias. |
| FR-MET-002 | MUST | Compute AIC and AICc for model comparison. |
| FR-MET-003 | MUST | Compute MSA (Mean Squared Accuracy, Burt & Disney) for asymmetric biomass error. |
| FR-MET-004 | MUST | Compute SSPB (Scaled Sum of Prediction Bias, Burt & Disney) for biomass bias characterization. |

### 3.5 Domain Data Classes

| ID | Priority | Requirement |
|----|----------|-------------|
| FR-DATA-001 | MUST | Provide `Tree` dataclass holding DBH, height, species, wood density, and site metadata. |
| FR-DATA-002 | MUST | Provide `Stand` dataclass with per-hectare area expansion and aggregated carbon stock. |
| FR-DATA-003 | MUST | `Tree` and `Stand` consume `ModelEntry` to compute AGB and carbon stock. |
| FR-DATA-004 | SHOULD | Expose wood density defaults and carbon fraction constants in `data/constants.py`. |

### 3.6 I/O Adapters

| ID | Priority | Requirement |
|----|----------|-------------|
| FR-IO-001 | MUST | Provide `read_csv()` to ingest a CSV of tree measurements into a list of `Tree` objects. |
| FR-IO-002 | MUST | Provide `stand_from_csv()` to ingest a CSV into a `Stand`. |
| FR-IO-003 | MUST | Accept pandas `DataFrame` as alternative input to all I/O adapters. |

### 3.7 Yield Table Subsystem

| ID | Priority | Requirement |
|----|----------|-------------|
| FR-YT-001 | MUST | Ingest yield tables from R packages (ForestElementsR — 14 spp; et.nwfva — 5 spp). |
| FR-YT-002 | MUST | Ingest yield tables from Excel files via openpyxl. |
| FR-YT-003 | MUST | Ingest yield tables from PDF sources (FC Bulletin 75, USDA tables) via tabula-py + Java. |
| FR-YT-004 | MUST | Ingest parametric (JSON equation-based) yield tables. |
| FR-YT-005 | MUST | Normalize all ingested tables to the canonical CSV schema (`yield_tables/schema.py`). |
| FR-YT-006 | MUST | Provide offline-first `resolve_yield_table()` matching by species, region, and site index without network access. |
| FR-YT-007 | MUST | Provide `pylometree-ingest` CLI for store management (`--help`, `--list`, `--run <provider>`). |
| FR-YT-008 | SHOULD | Provide species name standardization utilities in `yield_tables/species.py`. |

---

## 4. Acceptance Criteria (High-Level)

| # | Criterion |
|---|-----------|
| AC-1 | All MUST functional requirements have passing pytest tests. |
| AC-2 | `select_model()` returns the equation with lowest AIC across all 12 H-D forms on synthetic data. |
| AC-3 | `registry.query()` returns correct subsets for each filter dimension. |
| AC-4 | `resolve_yield_table()` succeeds without network access given a pre-ingested store. |
| AC-5 | `pylometree-ingest --help` exits with code 0 and lists all available providers. |
| AC-6 | No implicit unit conversion occurs — callers pass cm for DBH and m for height. |

---

## 5. Constraints

### 5.1 Technical Constraints

| Constraint | Detail |
|------------|--------|
| Language | Python 3.12+ only |
| Core deps | numpy ≥1.24, scipy ≥1.10, pandas ≥2.0 — core equations must not require optional extras |
| Distribution | Git-based dependency only; no PyPI wheel (XRFF-131) |
| Variable names | Must follow `allometric` R package convention: `dsob`, `hst`, `vsia`, `agb`, `bgb` |
| Yield-table providers | Runtime deps (R, Java) are user-installed; library never installs them automatically |
| Offline-first | `resolve_yield_table()` must not make network calls |

### 5.2 Academic Constraints

| Constraint | Detail |
|------------|--------|
| Citation integrity | Published models must carry a full bibliographic reference in `ModelEntry.reference` |
| Bias correction | Log-space models must document Sprugel 1983 correction status in model notes |

---

## 6. Assumptions and Dependencies

### 6.1 Assumptions

| # | Assumption |
|---|-----------|
| A-1 | Callers pass DBH in centimeters and height in meters unless a model's docstring states otherwise. |
| A-2 | Field data used for fitting has been cleaned prior to ingestion (no NaN, biologically valid ranges). |
| A-3 | R is on PATH when R-based yield-table providers are invoked. |
| A-4 | Java is available when PDF-based yield-table providers (tabula-py) are invoked. |

### 6.2 Dependencies

| Dependency | Role | When Required |
|------------|------|--------------|
| numpy ≥1.24 | Vectorized math in all model functions | Always |
| scipy ≥1.10 | `curve_fit` in fitting layer | Always |
| pandas ≥2.0 | DataFrame I/O and yield-table normalization | Always |
| scikit-learn ≥1.3 | ML-augmented model selection | Optional `[ml]` |
| statsmodels ≥0.14 | OLS/WLS model evaluation | Optional `[stats]` |
| R + ForestElementsR | Yield-table ingestion — 14 German tree species | Optional (ingestion only) |
| R + et.nwfva | Yield-table ingestion — 5 species | Optional (ingestion only) |
| openpyxl | Excel-based yield-table ingestion | Optional (ingestion only) |
| tabula-py + Java | PDF-based yield-table ingestion | Optional (ingestion only) |

---

## 7. Requirements Traceability

| Requirement ID | Module Path | Test File | Status |
|----------------|-------------|-----------|--------|
| FR-HD-001–005 | `src/pylometree/models/hd.py`, `fitting/nonlinear.py` | `tests/test_hd_models.py`, `tests/test_fitting.py` | Implemented |
| FR-BM-001–006 | `src/pylometree/models/biomass.py`, `models/crown.py` | `tests/test_biomass.py`, `tests/test_crown_models.py` | Implemented |
| FR-BM-005 | `src/pylometree/models/volume.py` | `tests/test_volume_models.py` | Implemented |
| FR-REG-001–006 | `src/pylometree/registry/base.py`, `registry/published.py` | `tests/test_registry.py` | Implemented |
| FR-MET-001–004 | `src/pylometree/metrics/` | `tests/test_metrics.py` | Implemented |
| FR-DATA-001–004 | `src/pylometree/data/tree.py`, `data/stand.py`, `data/constants.py` | `tests/test_data.py` | Implemented |
| FR-IO-001–003 | `src/pylometree/io/` | `tests/test_io.py` | Implemented |
| FR-YT-001–008 | `src/pylometree/yield_tables/` | — | Implemented (yield-table tests pending) |

---

## 8. Glossary

| Term | Definition |
|------|------------|
| dsob | Diameter outside bark at breast height (cm) — allometric R package convention |
| hst | Total stem height (m) — allometric R package convention |
| agb | Above-ground biomass (kg or Mg) |
| bgb | Below-ground biomass (kg or Mg) |
| AIC | Akaike Information Criterion — used for model comparison |
| AICc | AIC with small-sample correction |
| MSA | Mean Squared Accuracy (Burt & Disney 2015) |
| SSPB | Scaled Sum of Prediction Bias (Burt & Disney 2015) |
| ModelEntry | Dataclass bundling a published equation's function, parameters, citation, and metadata |
| ModelRegistry | Searchable in-memory collection of ModelEntry objects |
| YieldProvider | Abstract base class for yield-table data sources (see `yield_tables/providers.py`) |

---

## 9. Appendices

### Appendix A: MoSCoW Prioritization Summary

| Priority | Count |
|----------|-------|
| MUST have | 29 |
| SHOULD have | 5 |
| COULD have | 0 |
| WON'T have (this release) | 0 |

### Appendix B: References

1. ISO/IEC/IEEE 29148:2018 — Systems and software engineering requirements
2. Chave et al. 2014. Global Change Biology 20:3177 — pantropical AGB
3. Jucker et al. 2017. Global Change Biology 23:177 — crown-based AGB
4. Sprugel 1983. Ecology 64:209 — back-transformation bias correction
5. Burt & Disney 2015 — MSA and SSPB metrics
6. allometric R package — variable naming convention (dsob, hst, etc.)

---

## Maintenance

**Last Updated:** 2026-05-11

**Update Triggers:**
- New allometric equation forms added to `src/pylometree/models/`
- New yield-table providers added to `yield_tables/providers.py`
- Registry query interface extended
- Constraint changes (new mandatory dep, Python version floor raised)

**Verification:**
- [ ] All FR-XXX-NNN requirements have MoSCoW priority
- [ ] Traceability table references valid source file paths
- [ ] Glossary covers all domain-specific variable names

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-05-11 | ln-112-project-core-creator | Initial version |
