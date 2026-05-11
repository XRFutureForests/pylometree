# RSH-001: Allometric Variable Naming Convention

<!-- SCOPE: Research note on allometric variable naming — dsob/hst/rho origins and rationale -->
<!-- DOC_KIND: explanation -->
<!-- DOC_ROLE: reference -->
<!-- READ_WHEN: Read when adding new model functions or integrating with external allometric tools. -->
<!-- SKIP_WHEN: Skip if variable names dsob, hst, rho are already familiar from the allometric R package. -->
<!-- PRIMARY_SOURCES: src/pylometree/models/, src/pylometree/registry/published.py -->

## Quick Navigation

- [Reference Hub](../README.md)
- [Architecture](../../project/architecture.md)
- [Tech Stack](../../project/tech_stack.md)

## Agent Entry

| Signal | Value |
|--------|-------|
| Purpose | Documents why pylometree uses allometric R package variable naming (dsob, hst, rho) rather than informal names. |
| Read When | Adding model functions, integrating third-party equations, or cross-referencing R allometry literature. |
| Skip When | Variable naming is already understood from existing code or allometric R docs. |
| Canonical | Yes — this is the single rationale source for naming convention |

---

## Question

Why does pylometree use `dsob`, `hst`, `rho` instead of common names like `dbh`, `height`, `density`?

## Background

Forest allometry literature uses inconsistent variable names across papers and tools. Informal names like `dbh`, `h`, `height`, `density` clash between languages and measurement conventions (inside/outside bark, total/merchantable height).

## Finding

The [allometric R package](https://allometric.org/) standardized naming for tree measurements following ISO/FAO conventions. pylometree adopts this standard for cross-language interoperability.

## Variable Reference

| Variable | Meaning | Unit | Notes |
|----------|---------|------|-------|
| `dsob` | Diameter of stem, outside bark | cm | FAO/allometric convention |
| `hst` | Height of stem, total | m | Total stem height |
| `rho` | Wood density | g/cm³ | Oven-dry density |
| `agb` | Above-ground biomass | kg | Response variable for biomass models |
| `vol` | Stem volume | m³ | Response variable for volume models |

## Rationale

| Reason | Detail |
|--------|--------|
| Cross-language | Equations from R allometric package map 1:1 without renaming |
| Precision | `dsob` distinguishes outside-bark from inside-bark (`dsib`) diameter |
| Literature alignment | Chave 2014, Jucker 2017, and Pretzsch 2025 use these conventions |
| Registry clarity | `model_type` + variable names uniquely identify equation contracts |

## Decision

**Adopt allometric R package naming throughout pylometree.** All model functions, docstrings, and registry entries use this convention. Callers must pass values in stated units — no implicit conversion.

## Implications

- Model docstrings must specify units and variable names explicitly
- `dsob` always means diameter outside bark in cm; pass `dsib` only to functions that explicitly accept it
- Unit conversion is caller responsibility (pylometree does not normalize units)

## References

- [allometric R package](https://allometric.org/) — canonical variable naming source
- [FAO Forest Resources Assessment](https://www.fao.org/forest-resources-assessment/) — measurement conventions
- Chave J et al. (2014) GCB 20:3177 — uses `D` for `dsob`, `H` for `hst`, `ρ` for `rho`

## Maintenance

**Last Updated:** 2026-05-11

**Update Triggers:**
- New variable types added to model signatures
- New cross-language integration targets (e.g., Julia, Python wrappers for R packages)

**Verification:**
- [ ] All model functions in `src/pylometree/models/` use convention-compliant parameter names
- [ ] Registry entries use `dsob`/`hst`/`rho` in `covariates` and `units` fields

