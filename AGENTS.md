# pylometree

General-purpose Python toolkit for tree allometry — fitting, evaluating, and looking up allometric equations for H-D relationships, above- and below-ground biomass, crown structure, stem volume, and height-age growth.

<!-- SCOPE: Canonical machine-facing entry point with repo map, critical rules, command overview, and links to detailed documentation ONLY. -->
<!-- DOC_KIND: index -->
<!-- DOC_ROLE: canonical -->
<!-- READ_WHEN: Start here when you need the project map, local rules, or the next canonical document. -->
<!-- SKIP_WHEN: Skip when you already know the exact target document or code area. -->
<!-- PRIMARY_SOURCES: AGENTS.md, docs/README.md -->

## Quick Navigation

| Need | Read |
|------|------|
| Documentation map | [docs/README.md](docs/README.md) |
| Standards | [docs/documentation_standards.md](docs/documentation_standards.md) |
| Principles | [docs/principles.md](docs/principles.md) |
| Architecture | [docs/architecture.md](docs/architecture.md) |
| API reference | [docs/api-reference.md](docs/api-reference.md) |
| GitLab repo | <https://gitlab.uni-freiburg.de/xr-future-forests-lab/pylometree> |

## Agent Entry

- Purpose: Canonical repo map and routing layer for agents.
- Read when: You need the project overview, local rules, or the next canonical doc.
- Skip when: You already know the exact file or document to inspect.
- Canonical: Yes.
- Read next: `docs/README.md`, then the relevant canonical doc for the task.
- Primary sources: `AGENTS.md`, `docs/README.md`.

## Critical Rules

| Category | Rule | When to Apply |
|----------|------|---------------|
| Confirmation | Never commit or push without explicit user confirmation | Always |
| Scope | Modify only what the request requires — no adjacent cleanup | Always |
| Simplicity | Minimum code that solves the problem — no speculative features | Always |
| Pure models | Functions in `src/pylometree/models/` must have no I/O and no side effects | Before adding to models/ |
| Naming | Use allometric R convention: `dsob` (DBH outside bark, cm), `hst` (stem height, m) | All public API |
| Units | Document units in every docstring — no implicit conversion | All model functions |
| Bias correction | Back-transformation bias correction (Sprugel 1983) must be explicit, never silent | Log-space transforms |
| Registry | Strict `model_type` matching — no implicit cross-type lookups | Registry queries |
| Yield tables | Offline-first resolution — no silent remote fallback | yield_tables/ |
| Task tracking | Use Linear MCP for all issue operations — check before creating new issues | Always |
| Language | Keep project code and documentation in English | All written artifacts |

## MCP Tool Preferences

| Need | Preferred flow |
|------|----------------|
| Discover files | `mcp__hex-line__inspect_path` with narrow path |
| Search text | `mcp__hex-line__grep_search` summary mode, narrow before content |
| Read code | `mcp__hex-line__outline` or targeted `mcp__hex-line__read_file` |
| Edit code | `read_file(edit_ready=true)` → `edit_file(base_revision)` → verify |
| Semantic risk | `mcp__hex-graph__index_project` → symbol/architecture analysis |

## Development Commands

| Task | Command |
|------|---------|
| Install (editable + dev) | `pip install -e ".[dev]"` |
| Install with uv | `uv pip install -e ".[dev]"` |
| Run tests | `pytest` |
| Run tests verbose | `pytest -v --tb=short` |
| Yield table CLI | `pylometree-ingest --help` |
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

**Last Updated:** 2026-05-11
