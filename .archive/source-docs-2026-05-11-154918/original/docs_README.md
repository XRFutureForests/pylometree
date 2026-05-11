# pylometree — Documentation

Developer-oriented reference for [pylometree](../README.md), a Python toolkit for tree allometry.

## Contents

- [architecture.md](architecture.md) — package layout and module responsibilities
- [api-reference.md](api-reference.md) — public API by subpackage
- [tutorials/hd-fitting.md](tutorials/hd-fitting.md) — fit and select height–diameter models
- [tutorials/biomass.md](tutorials/biomass.md) — estimate AGB with the registry
- [tutorials/yield-tables.md](tutorials/yield-tables.md) — ingest and resolve yield tables
- [species-reference.md](species-reference.md) — standardized species names and codes
- [research/](research/) — methodological notes and bibliography
- [internal-phases-roadmap.md](internal-phases-roadmap.md) — internal development roadmap (phases 3–7)

## Quick links

- Top-level [README.md](../README.md) — install, quick start, model catalogue
- [species-reference.md](species-reference.md) — name normalization conventions
- Issue tracker: [GitLab Issues](https://gitlab.uni-freiburg.de/xr-future-forests-lab/pylometree/-/issues)

## Scope

`pylometree` is a general-purpose library. It does not depend on any specific
inventory format, database, or rendering pipeline. Within the XR Future Forests
Lab it is used by [growpy](https://gitlab.uni-freiburg.de/xr-future-forests-lab/growpy)
for yield-table-driven growth calibration and by
[digital-twin-db](https://gitlab.uni-freiburg.de/xr-future-forests-lab/digital-twin-db)
consumers that compute derived attributes (biomass, predicted height) from
stored measurements.
