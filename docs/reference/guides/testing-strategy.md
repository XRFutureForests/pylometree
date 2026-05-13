# Testing Strategy

Universal testing philosophy and strategy for modern software projects: principles, organization, and best practices.

<!-- SCOPE: Testing philosophy, risk-based strategy, test organization, isolation patterns, what to test ONLY. -->
<!-- DOC_KIND: how-to -->
<!-- DOC_ROLE: canonical -->
<!-- READ_WHEN: Read when you need testing philosophy, prioritization rules, or isolation guidance. -->
<!-- SKIP_WHEN: Skip when you only need current test inventory or project-specific execution commands. -->
<!-- PRIMARY_SOURCES: tests/README.md, docs/tasks/README.md, docs/project/architecture.md -->
<!-- DO NOT add here: project structure, framework-specific patterns, CI/CD configuration, test tooling setup -->

## Quick Navigation

- **Tests Organization:** [tests/README.md](../../../tests/README.md) - Directory structure, Story-Level Pattern, running tests
- **Task Rules:** [docs/tasks/README.md](../../tasks/README.md) - Workflow rules for Story-Level test tasks

## Agent Entry

| Signal | Value |
|--------|-------|
| Purpose | Defines the testing philosophy, prioritization thresholds, and isolation expectations. |
| Read When | You need risk-based testing rules or guidance on what to automate. |
| Skip When | You only need the current project's test commands or directory map. |
| Canonical | Yes |
| Next Docs | [tests/README.md](../../../tests/README.md), [docs/tasks/README.md](../../tasks/README.md) |
| Primary Sources | `tests/README.md`, `docs/tasks/README.md`, `docs/project/architecture.md` |

---

## Testing Philosophy

### Test Your Code, Not Frameworks

Focus testing effort on your business logic and integration usage. Do not retest numpy/scipy internals, pandas DataFrame mechanics, or third-party allometry library behavior.

**Rule of thumb:** If deleting your code would not fail the test, you are testing someone else's code.

### Risk-Based Testing

Automate only high-value scenarios using **Business Impact (1-5) x Probability (1-5)**.

| Priority Score | Action | Example Scenarios |
|----------------|--------|-------------------|
| **>=15** | Must test | Allometry equation correctness, biomass calculation accuracy, H-D curve fitting |
| **10-14** | Consider testing | Species-specific model edge cases, unit conversion correctness |
| **<10** | Usually skip automation | numpy/scipy internals, pandas I/O mechanics |

### Test Usefulness Criteria

Before keeping a test, validate:

| Check | Question |
|-------|----------|
| Risk Priority | Does it cover a >=15 scenario or a justified exception? |
| Confidence ROI | Will failure teach us something important? |
| Behavioral Value | Does it validate project behavior, not library behavior? |
| Predictive Value | Would failure warn us about a real regression? |
| Specificity | If it fails, is the cause obvious enough to fix quickly? |

---

## Test Levels

### End-to-End

Use for full allometry pipelines — field measurements through final biomass/carbon output — where the full chain of transformations matters most.

### Integration

Use for cross-module interaction when E2E would be too slow or too broad. Examples: H-D model fitting combined with volume calculations, registry loading combined with species dispatch.

### Unit

Use for dense business logic and branch-heavy code that cannot be covered efficiently at higher levels. Examples: individual allometric equation implementations, edge cases in biomass coefficient lookups, boundary conditions in H-D curve parameterization.

### Recommended Balance

- Prefer fewer, higher-value tests over many shallow tests.
- Keep E2E focused on critical allometry pipelines.
- Use integration tests to cover module seams (fitting + prediction + output).
- Use unit tests for complex formulas and species-specific model accuracy validation.

---

## Test Organization

- `tests/automated/e2e/` for critical end-to-end allometry pipelines
- `tests/automated/integration/` for cross-module behavior
- `tests/automated/unit/` for complex business logic and equation implementations
- `tests/manual/` for manual scripts and supporting fixtures

Use `test_*.py` naming convention (pytest default, already in use across this project).

---

## Isolation Patterns

- Each test creates its own data or fixture setup.
- Tests clean up after themselves or use pytest fixtures with appropriate scope.
- No hidden dependency on execution order.
- No real external calls unless the test is explicitly designed for them.

---

## What to Test vs Skip

| Test This | Usually Skip This |
|-----------|-------------------|
| Allometric equation implementations | numpy/scipy internal math |
| H-D curve fitting logic you wrote | pandas DataFrame indexing mechanics |
| Biomass calculation formulas | statsmodels fitting internals |
| Species registry dispatch | scikit-learn model internals |
| Carbon conversion accuracy | Third-party library serialization |

---

## Maintenance

**Update Triggers:**
- New testing patterns discovered
- Framework version changes affecting tests
- Significant changes to test architecture
- New isolation issues identified

**Verification:**
- [ ] Philosophy still matches risk-based testing guidance
- [ ] Thresholds and examples still reflect current project standards
- [ ] Linked docs resolve

**Last Updated:** 2026-05-12
