# pylometree — Documentation Hub

<!-- SCOPE: Root documentation hub for pylometree — navigation to all project docs -->
<!-- DOC_KIND: index -->
<!-- DOC_ROLE: navigation -->
<!-- READ_WHEN: Read when orienting to the documentation structure or finding the right doc. -->
<!-- SKIP_WHEN: Skip when you already know the exact document to open. -->
<!-- PRIMARY_SOURCES: AGENTS.md, docs/project/, docs/reference/, docs/tasks/ -->

## Quick Navigation

- [AGENTS.md](../AGENTS.md) — canonical project entry point
- [Project Docs](project/) — requirements, architecture, tech stack, infrastructure
- [Reference](reference/README.md) — ADRs, guides, manuals, research
- [Tasks](tasks/README.md) — task workflow and kanban board
- [Tutorials](tutorials/) — usage tutorials (H-D fitting, biomass, yield tables)
- [API Reference](api-reference.md) — public API by subpackage
- [Species Reference](species-reference.md) — standardized species names

## Agent Entry

| Signal | Value |
|--------|-------|
| Purpose | Navigation hub for all pylometree documentation. Routes to canonical project docs, reference artifacts, and task management. |
| Read When | You need to find the right documentation file or understand the doc structure. |
| Skip When | You already know the exact file you need. |
| Canonical | Navigation only — see AGENTS.md for the canonical project map. |
| Next Docs | [AGENTS.md](../AGENTS.md), [project/architecture.md](project/architecture.md), [project/requirements.md](project/requirements.md) |

---

## Project Documentation

| Document | Purpose |
|----------|--------|
| [requirements.md](project/requirements.md) | Functional requirements (FR-XXX-NNN, MoSCoW) |
| [architecture.md](project/architecture.md) | Package architecture, C4 model, design decisions |
| [tech_stack.md](project/tech_stack.md) | Technology versions, dependency rationale |
| [infrastructure.md](project/infrastructure.md) | Dev environment, optional providers, data paths |

## Reference

| Document | Purpose |
|----------|--------|
| [reference/README.md](reference/README.md) | ADRs, guides, manuals, research hub |
| [reference/research/rsh-001-allometric-naming.md](reference/research/rsh-001-allometric-naming.md) | Variable naming convention (dsob, hst, rho) |

## Tasks

| Document | Purpose |
|----------|--------|
| [tasks/README.md](tasks/README.md) | Task workflow, Linear integration rules |
| [tasks/kanban_board.md](tasks/kanban_board.md) | Live board navigation (Linear XRFF team) |

## Tutorials and API Reference

| Document | Purpose |
|----------|--------|
| [tutorials/hd-fitting.md](tutorials/hd-fitting.md) | Fit and select H-D models |
| [tutorials/biomass.md](tutorials/biomass.md) | Estimate AGB with the registry |
| [tutorials/yield-tables.md](tutorials/yield-tables.md) | Ingest and resolve yield tables |
| [api-reference.md](api-reference.md) | Public API by subpackage |
| [species-reference.md](species-reference.md) | Standardized species names and codes |

## Scope Note

`pylometree` is a general-purpose library with no dependency on any specific inventory format, database, or rendering pipeline. Within XR Future Forests Lab it is used by [growpy](https://gitlab.uni-freiburg.de/xr-future-forests-lab/growpy) for yield-table-driven growth calibration and by [digital-twin-db](https://gitlab.uni-freiburg.de/xr-future-forests-lab/digital-twin-db) consumers that compute derived attributes.

---

## Maintenance

**Last Updated:** 2026-05-11

**Update Triggers:**
- New documents added to docs/project/, docs/reference/, docs/tasks/
- Tutorials or API reference updated
- Project scope changes

**Verification:**
- [ ] All links in navigation tables resolve
- [ ] AGENTS.md link points to correct root file
- [ ] Tutorials directory links are valid
