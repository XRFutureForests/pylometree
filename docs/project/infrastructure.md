# Infrastructure: pylometree

<!-- SCOPE: Development environment requirements, optional provider dependencies, local data paths, artifact distribution, and CI/CD status ONLY. -->
<!-- DO NOT add here: Operational procedures → runbook.md, Architecture patterns → architecture.md, Tech stack versions → tech_stack.md, API contracts → api-reference.md -->
<!-- DOC_KIND: explanation -->
<!-- DOC_ROLE: canonical -->
<!-- READ_WHEN: Read when you need host requirements, optional dependency constraints, data file locations, or distribution/install facts. -->
<!-- SKIP_WHEN: Skip when you only need feature-level architecture or public API contracts. -->
<!-- PRIMARY_SOURCES: pyproject.toml, src/pylometree/yield_tables/, data/ -->

> **Status:** Active — library in Alpha (v0.1.0)
> **Last Updated:** 2026-05-11

## Quick Navigation

- [Docs Hub](../README.md)
- [Architecture](../architecture.md)
- [API Reference](../api-reference.md)
- [Contributing](../../CONTRIBUTING.md)

## Agent Entry

| Signal | Value |
|--------|-------|
| Purpose | Describes host requirements, optional dependencies, data paths, and distribution model for pylometree. |
| Read When | You need install constraints, optional provider requirements, data directory layout, or CI/CD facts. |
| Skip When | You only need API signatures, model equations, or architecture design rationale. |
| Canonical | Yes |
| Next Docs | [Architecture](../architecture.md), [API Reference](../api-reference.md) |
| Primary Sources | `pyproject.toml`, `src/pylometree/yield_tables/`, `data/` |

## 1. Deployment Model

pylometree is a **pure Python library** — there are no servers, containers, or running services. It is installed as a local Git dependency and runs entirely in-process within the consuming application or interactive session.

| Property | Value |
|----------|-------|
| **Distribution** | Git dependency (no PyPI release) — decision tracked in Linear XRFF team |
| **Install target** | Developer workstation / CI runner |
| **Deployment scale** | Single (library, not a service) |
| **Entry points** | `pylometree-ingest` CLI (yield table ingestion only) |

## 2. Host Requirements

| Requirement | Minimum | Notes |
|-------------|---------|-------|
| **Python** | 3.12 | 3.13 also tested; see `pyproject.toml` classifiers |
| **RAM** | ~256 MB | Pandas DataFrames for large yield tables may require more |
| **Disk** | ~50 MB | Includes `data/` yield tables and source tree |
| **R** | 4.0+ | Optional — required only for NWFVA, forest_elements, and FORIT yield table providers |
| **Java** | Any recent JRE | Optional — required only for `tabula-py` PDF yield table parsing |

No GPU is required or used.

## 3. Local Data Paths

| Path | Contents | Required |
|------|----------|----------|
| `data/all_species.csv` | Master species list (all supported species codes) | Yes |
| `src/pylometree/yield_tables/data/species.csv` | Species metadata used by yield table resolvers | Yes |
| `src/pylometree/yield_tables/r_scripts/` | R extraction scripts for yield table providers | Only with R providers |
| `./yield_store/` (runtime) | Local yield table store created by `pylometree-ingest` | Created on first ingest |

The `yield_store` path is configurable via the `--store-dir` flag of `pylometree-ingest`.

## 4. Optional Dependencies

All optional extras are declared in `pyproject.toml` under `[project.optional-dependencies]`.

| Extra | Packages | Use Case |
|-------|----------|----------|
| `ml` | scikit-learn ≥ 1.3 | Machine-learning–based allometric fits |
| `stats` | statsmodels ≥ 0.14 | Statistical model diagnostics and summaries |
| `dev` | pytest ≥ 7.4, pytest-cov ≥ 4.1 | Test suite execution |
| `all` | All of the above | Full development environment |

Install the full development environment with:
```shell
pip install -e ".[all]"
```

## 5. Artifact Distribution

No artifact repository or package registry is configured. pylometree is consumed directly from Git:

```shell
pip install git+https://github.com/XRFutureForests/pylometree.git
```

Publishing to PyPI is not planned for the current Alpha phase. Distribution approach is tracked in the [Linear XRFF backlog](https://linear.app/geosense-ufr/team/XRFF).

## 6. CI/CD Pipeline

No automated CI/CD pipeline is currently configured. Tests are run locally by contributors.

| Property | Value |
|----------|-------|
| **Platform** | None configured |
| **Test runner** | `pytest` (local, `testpaths = ["tests"]`) |
| **Issue tracker** | [GitHub Issues](https://github.com/XRFutureForests/pylometree/issues) |
| **Task tracker** | [Linear — XRFF team](https://linear.app/geosense-ufr/team/XRFF) |

## 7. Contacts

| Role | Contact |
|------|---------|
| Maintainer | maximilian.sperlich@gmail.com |
| Organisation | XR Future Forests Lab, University of Freiburg (funded by Eva Mayr-Stihl Stiftung) |

## Maintenance

**Update Triggers:**
- Python version support changes (update Host Requirements table)
- New optional dependency extras added to `pyproject.toml`
- Yield table provider added that requires a new external runtime (R, Java)
- Distribution model changes (e.g. PyPI release)
- CI/CD pipeline added or changed

**Verification:**
- Confirm `pyproject.toml` `requires-python` matches the Python row in Host Requirements
- Confirm `[project.optional-dependencies]` extras match the Optional Dependencies table
- Confirm data file paths exist under `data/` and `src/pylometree/yield_tables/data/`

---
