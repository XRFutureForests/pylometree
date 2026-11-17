# pylometree

General-purpose Python toolkit for tree allometry — fitting, evaluating, and looking up allometric equations for H-D relationships, above- and below-ground biomass, crown structure, stem volume, and height-age growth.

## Documentation Map

| Need | Read |
|------|------|
| What the library is, features, design notes | [README.md](README.md) |
| Install, fitting, registry, yield tables, troubleshooting | [RUNBOOK.md](RUNBOOK.md) |
| API surface, species coverage, tutorials | [docs/](docs/README.md) |
| Why these metrics, equation-choice rationale, place in the twin | XR Future Forests Lab knowledge hub (`04-LOGIC-TIER/pylometree`) — **not** in this repo |
| GitHub repo | <https://github.com/XRFutureForests/pylometree> |

Deep-dive documentation is deliberately not duplicated here. If you need to explain *why* an
approach was chosen, write it in the knowledge hub and link to it.

## Critical Rules

Workspace rules (decision rights, commits, Linear, tool preferences) are in the workspace `AGENTS.md` one level above the repos and apply here too. The basics: change only what the task needs, verify each step, commit your own work with an explicit pathspec, never commit secrets.

| Category | Rule | When to Apply |
|----------|------|---------------|
| Pure models | Functions in `src/pylometree/models/` must have no I/O and no side effects | Before adding to models/ |
| Naming | Use allometric R convention: `dsob` (DBH outside bark, cm), `hst` (stem height, m) | All public API |
| Units | Document units in every docstring — no implicit conversion | All model functions |
| Bias correction | Back-transformation bias correction (Sprugel 1983) must be explicit, never silent | Log-space transforms |
| Registry | Strict `model_type` matching — no implicit cross-type lookups | Registry queries |
| Yield tables | Offline-first resolution — no silent remote fallback | yield_tables/ |
| Language | Keep project code and documentation in English | All written artifacts |
| Release docs | `CHANGELOG.md` and `CONTRIBUTING.md` stay: public PyPI-style package released to Zenodo from `main` (workspace decision 2026-09-15 — only growpy, pylometree, digital-twin-db and dtm-to-unreal carry them); `dev` is the working branch | Always |
| Tutorials | `docs/tutorials/` stays in the repo: they are package how-tos for external users, not project explanations | docs/ changes |

## Development Commands

| Task | Command |
|------|---------|
| Install (editable + dev) | `pip install -e ".[dev]"` |
| Install with uv | `uv pip install -e ".[dev]"` |
| Run tests | `pytest` |
| Run tests verbose | `pytest -v --tb=short` |
| Yield table CLI | `pylometree-ingest --help` (console script restored 2026-09-15, XRFF-353 — re-install editable) |
| Format | `ruff format .` |
| Lint | `ruff check .` |

## Source Layout

| Path | Purpose |
|------|---------|
| `src/pylometree/models/` | Pure equation functions: hd (12 forms), biomass, crown, volume |
| `src/pylometree/fitting/` | scipy curve_fit wrapper, bootstrap CIs, AIC-based model selection |
| `src/pylometree/metrics/` | R², RMSE, MAE, bias, AIC, AICc, MSA, SSPB |
| `src/pylometree/registry/` | ModelEntry + ModelRegistry, pre-loaded published equations |
| `src/pylometree/data/` | Tree and Stand dataclasses, carbon stock, per-hectare aggregation |
| `src/pylometree/io/` | CSV/DataFrame adapters to Tree/Stand |
| `src/pylometree/yield_tables/` | Multi-source ingestion, offline-first resolution, pylometree-ingest CLI |
| `tests/` | pytest suite mirroring src layout |

## Maintenance

**Update Triggers:**
- When root navigation or canonical document links change
- When core commands change
- When critical project rules change

**Verification:**
- [ ] Links resolve
- [ ] Commands match current `pyproject.toml`
- [ ] Canonical docs listed here still exist

**Last Updated:** 2026-11-17
