# Patterns Catalog — pylometree

Architectural patterns with 4-score evaluation.

> **SCOPE:** Pattern inventory with scores, ADR/Guide links. Updated by ln-640 Pattern Evolution Auditor.
> **Last Audit:** 2026-05-11 (initial detection, not yet scored)

<!-- SCOPE: Pattern inventory with scores, ADR/Guide links. Updated by ln-640 Pattern Evolution Auditor. -->
<!-- DOC_KIND: reference -->
<!-- DOC_ROLE: canonical -->
<!-- READ_WHEN: Read when you need the current inventory of architectural patterns and their audit status. -->
<!-- SKIP_WHEN: Skip when you only need one specific design decision or source file. -->
<!-- PRIMARY_SOURCES: docs/project/architecture.md, src/pylometree/registry/base.py, src/pylometree/yield_tables/providers.py -->

## Quick Navigation

- [Architecture](../project/architecture.md)
- [Requirements](../project/requirements.md)
- [API Reference](../api-reference.md)

## Agent Entry

| Signal | Value |
|--------|-------|
| Purpose | Tracks active architectural patterns, links to supporting docs, and records audit posture for pylometree. |
| Read When | You need pattern inventory, trend, or audit status. |
| Skip When | You already know the exact source file or design decision to inspect. |
| Canonical | Yes |
| Next Docs | [Architecture](../project/architecture.md) |
| Primary Sources | `src/pylometree/registry/base.py`, `src/pylometree/yield_tables/providers.py`, `docs/project/architecture.md` |

---

## Score Legend

| Score | Measures | Threshold |
|-------|----------|-----------|
| **Compliance** | Industry standards, naming, tech stack conventions, layer boundaries | 70% |
| **Completeness** | All components, error handling, observability, tests | 70% |
| **Quality** | Readability, maintainability, SOLID, no smells, no duplication | 70% |
| **Implementation** | Code exists, production use, monitored | 70% |

---

## Pattern Inventory

Patterns confirmed as deliberately implemented (baseline).

| # | Pattern | ADR | Guide | Compl | Complt | Qual | Impl | Avg | Notes | Story |
|---|---------|-----|-------|-------|--------|------|------|-----|-------|-------|
| 1 | Registry / Service Locator | — | — | —% | —% | —% | —% | **—%** | `registry/base.py` ModelRegistry; strict type matching; singleton via `published.py` | — |
| 2 | Template Method / Strategy (equation dispatch) | — | — | —% | —% | —% | —% | **—%** | `models/` `_MODELS` dict + `select_model`; callers pass callable; AIC selects strategy | — |
| 3 | Provider / Plugin (yield tables) | — | — | —% | —% | —% | —% | **—%** | `YieldProvider` ABC in `providers.py`; 8 concrete providers; CLI dispatch | — |
| 4 | Value Object / Dataclass | — | — | —% | —% | —% | —% | **—%** | `ModelEntry`, `Tree`, `Stand`, `YieldTableRecord` — immutable-by-convention domain objects | — |

*Scores pending ln-640 audit.*

<!-- Auto-detected by ln-112, audit with ln-640 -->

---

## Discovered Patterns (Adaptive)

Patterns found via heuristic discovery, not in baseline library.

| # | Pattern | Confidence | Evidence | Compl | Complt | Qual | Impl | Avg | Story |
|---|---------|------------|----------|-------|--------|------|------|-----|-------|
| 1 | Singleton (global registry) | HIGH | `registry/published.py` populates module-level `registry` instance on import; `__init__.py` re-exports it | —% | —% | —% | —% | **—%** | — |
| 2 | Factory (ModelEntry construction) | MEDIUM | `registry/published.py:166` — factory function to avoid closure-capture issues in loop | —% | —% | —% | —% | **—%** | — |
| 3 | Layered Architecture | HIGH | 7 independent layers: `models → fitting → metrics → registry → data → io → yield_tables`; directional dependency enforced by convention | —% | —% | —% | —% | **—%** | — |

**Confidence levels:**
- `HIGH` — Naming + structural indicators match
- `MEDIUM` — Naming convention only
- `LOW` — Structural heuristic only

---

## Layer Boundary Status

Audit results from ln-642-layer-ownership-boundary-auditor.

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Layer Violations | — | 0 | Not yet audited |
| Circular imports | — | 0 | Not yet audited |
| yield_tables isolation | — | Full | Not yet audited |

### Active Layer Violations

<!-- Populated by ln-642 -->

| # | File | Line | Violation | Allowed In | Story |
|---|------|------|-----------|------------|-------|
| — | — | — | None detected yet | — | — |

---

## API Contract Status

Audit results from ln-643-api-contract-auditor.

| Check | Status | Details |
|-------|--------|---------|
| ModelEntry public API | Not audited | — |
| FitResult contract | Not audited | — |
| YieldProvider ABC | Not audited | — |
| Error format consistency | Not audited | — |

---

## Pattern Recommendations

Suggested patterns based on project analysis (NOT scored, advisory only).

| Condition Found | Recommended Pattern | Rationale |
|-----------------|---------------------|-----------|
| Yield-table ingestion has no retry logic | Resilience / Retry decorator | Provider subprocess calls can fail transiently (R not on PATH, Java unavailable) |
| No formal ADR directory | Decision Record (ADR) | Current design rationale is scattered in code comments; formalize in `docs/reference/adrs/` |

---

## Excluded Patterns

Patterns detected by keyword but excluded after applicability verification.

| # | Pattern | Keywords Found | Exclusion Reason |
|---|---------|---------------|-----------------|
| 1 | Job Queue / Bull | "Worker" in docstring only | No actual job queue infra; provider runs are synchronous subprocess calls |
| 2 | Event-Driven / Pub-Sub | "publish" in `registry/published.py` docstring | "published" refers to academic publication, not event publishing |

**Exclusion reasons:**
- **Language idiom:** Standard language construct or terminology — not an architectural pattern
- **Structural:** Fewer than 2 required structural components detected

---

## Quick Wins (< 4h effort)

| Pattern | Issue | Recommendation | Effort | Impact |
|---------|-------|----------------|--------|--------|
| Provider / Plugin | No availability check logged at startup | Add `logging.info` in CLI for each unavailable provider | 1h | +observability |
| Registry | No `list()` method to enumerate all registered models | Add `ModelRegistry.list()` returning all entries | 1-2h | +discoverability |

---

## Summary

**Architecture Health Score:** — (Not yet audited)

| Status | Count | Patterns |
|--------|-------|----------|
| Healthy (90%+) | — | — |
| Warning (70-89%) | — | — |
| Critical (<70%) | — | — |
| Detected, not scored | 7 | Registry, Strategy/dispatch, Provider/Plugin, Value Object, Singleton, Factory, Layered Architecture |

---

## Maintenance

**Updated by:** ln-640-pattern-evolution-auditor
**Layer audit by:** ln-642-layer-ownership-boundary-auditor
**API contract audit by:** ln-643-api-contract-auditor
**Last Updated:** 2026-05-11

**Update Triggers:**
- New architectural pattern introduced
- Pattern refactored (run ln-640 audit)
- Layer violation introduced or fixed
- ADR created for a pattern decision

**Verification:**
- [ ] Pattern rows match current `src/pylometree/` structure
- [ ] Excluded patterns list kept accurate after refactoring
- [ ] Quick Wins acted on or promoted to Stories

**Next Audit:** 2026-06-10 (30 days)
