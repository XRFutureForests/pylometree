# Development Principles

<!-- SCOPE: pylometree development principles and tradeoffs ONLY. Contains governing principles, decision order, anti-patterns, and verification guidance. -->
<!-- DOC_KIND: explanation -->
<!-- DOC_ROLE: canonical -->
<!-- READ_WHEN: Read when making implementation or documentation decisions and you need the governing principles. -->
<!-- SKIP_WHEN: Skip when you only need routing or an exact factual lookup. -->
<!-- PRIMARY_SOURCES: docs/principles.md, docs/documentation_standards.md -->

## Quick Navigation

| Need | Read |
|------|------|
| Documentation rules | [documentation_standards.md](documentation_standards.md) |
| Documentation map | [README.md](README.md) |
| Architecture decisions | [architecture.md](architecture.md) |

## Agent Entry

- Purpose: Explain pylometree's governing principles and decision hierarchy.
- Read when: You need to choose between alternatives or justify a tradeoff.
- Skip when: You only need a direct factual lookup.
- Canonical: Yes.
- Read next: The relevant project or reference doc for the concrete domain.
- Primary sources: `docs/principles.md`, `docs/documentation_standards.md`.

## Core Principles

| # | Principle | Application |
|---|-----------|-------------|
| 1 | Pure functions in models/ | `src/pylometree/models/` functions have no I/O, no state, no side effects |
| 2 | Strict type matching | No implicit cross-type model queries in the registry |
| 3 | Explicit bias correction | Sprugel 1983 back-transformation applied explicitly; never silently absorbed |
| 4 | No implicit unit conversion | Document units in every docstring; callers own conversion |
| 5 | Offline-first | Yield-table resolution never silently falls back to remote sources |
| 6 | Src layout | `src/pylometree/` keeps the package separate from tests and tooling |
| 7 | Allometric R naming | Public API uses `dsob`/`hst` per the allometric R convention |
| 8 | KISS / YAGNI | Build only what is needed now; prefer the simplest correct solution |

## Decision Framework

When choosing between alternatives, apply criteria in this order:

| Priority | Criterion |
|----------|-----------|
| 1 | Numerical correctness (equations match published sources) |
| 2 | Explicit over implicit (units, corrections, type matching) |
| 3 | Simplicity — fewest moving parts that solve the problem |
| 4 | Standards compliance (Python, forestry convention) |
| 5 | Maintainability |
| 6 | Performance |

## Anti-Patterns

| Anti-pattern | Why It Is Wrong |
|--------------|-----------------|
| Silent unit normalization inside a model function | Hides caller assumptions; causes hard-to-trace errors in pipelines |
| Implicit bias correction | Correction is a scientific decision; hiding it produces unreproducible results |
| Cross-type registry lookup fallback | Masks model mismatches; produces silently wrong estimates |
| I/O or logging inside `models/` | Breaks composability and testability of pure equation functions |
| Remote yield-table fetch without explicit opt-in | Breaks offline workflows and reproducibility |
| Speculative features / over-engineering | Contradicts YAGNI; adds maintenance debt with no current payoff |
| Magic constants scattered in source | Undermines traceability to published allometric coefficients |

## Naming Reference

| Symbol | Meaning | Unit |
|--------|---------|------|
| `dsob` | Diameter at breast height, outside bark | cm |
| `hst` | Stem height (total tree height) | m |
| `agb` | Above-ground biomass | kg or Mg |
| `bgb` | Below-ground biomass | kg or Mg |

## Verification Checklist

- [ ] Model functions in `models/` are pure (no I/O, no global state)
- [ ] Units documented in each affected docstring
- [ ] Bias correction applied explicitly and documented when log-space transform is used
- [ ] Registry query uses strict `model_type` matching
- [ ] Yield-table path uses offline-first resolution
- [ ] New public names follow `dsob`/`hst` allometric R convention
- [ ] No speculative code added beyond the stated requirement

## Maintenance

**Update Triggers:**
- When a new principle is adopted or an existing one changes
- When a recurring anti-pattern is identified in code review
- When the allometric naming convention is extended

**Verification:**
- [ ] Principles still reflect the current codebase
- [ ] Decision order matches team expectations
- [ ] Anti-pattern list covers currently observed violations

**Last Updated:** 2026-05-11
