# Architecture

High-level overview of how `pylometree` is organized and how the pieces fit together.

> **Canonical source moved**: Architecture documentation is now at [docs/project/architecture.md](project/architecture.md). This file is preserved for reference but will not be updated.


## Package layout

```text
pylometree/
├── models/          # Equation implementations (pure functions)
│   ├── hd.py        # Height–diameter forms (12 equations)
│   ├── biomass.py   # AGB equations (power law M1–M4, Chave 2014, Musa NSUR)
│   ├── crown.py     # Crown-area/height → AGB (Jucker, Htoo)
│   └── volume.py    # Stem volume (form factor, power law)
├── fitting/         # Curve fitting and model selection
│   └── nonlinear.py # scipy.optimize.curve_fit wrapper, bootstrap, select_model
├── metrics/         # R², RMSE, MAE, AIC, AICc, MSA, SSPB
├── registry/        # Searchable model registry
│   ├── base.py      # ModelEntry, ModelRegistry classes
│   └── published.py # Pre-loaded published equations
├── data/            # Domain data classes
│   ├── tree.py      # Tree dataclass
│   ├── stand.py     # Stand dataclass (plot-level aggregation)
│   └── constants.py # Wood density defaults, carbon fraction
├── io/              # CSV and DataFrame ingestion
└── yield_tables/    # Multi-source yield table ingestion & resolution
    ├── providers.py # Per-source ingestion logic
    ├── loaders.py   # Normalized CSV reading
    ├── resolver.py  # Runtime best-match lookup
    ├── store.py     # Local store manifest management
    ├── schema.py    # Canonical CSV schema
    ├── species.py   # Species name standardization
    ├── record.py    # YieldTableRecord dataclass
    └── cli.py       # `pylometree-ingest` entry point
```

## Separation of concerns

1. **Equations** (`models/`) — pure math. Each function takes numeric arguments,
   returns a numeric result. No I/O, no state. Vectorized over NumPy arrays.

2. **Fitting** (`fitting/`) — takes observations and a model callable, returns
   a `FitResult` with parameters, covariance, and a `.predict` method. Bootstrap
   CIs and multi-model selection build on this.

3. **Registry** (`registry/`) — metadata store for published equations. Each
   `ModelEntry` bundles a function, its canonical parameter values, reference
   citation, units, species, and region. Queryable by type, species, or region.

4. **Domain objects** (`data/`) — `Tree` and `Stand` hold measurements and
   derived quantities. They consume `ModelEntry` to compute AGB, carbon stock,
   per-hectare aggregates.

5. **I/O** (`io/`) — thin adapters between CSV/DataFrame rows and `Tree`/`Stand`.

6. **Yield tables** (`yield_tables/`) — a self-contained subsystem with its
   own CLI. Ingests from external providers (R packages, Excel files, PDFs,
   JSON parametric models), normalizes to a canonical CSV schema, and resolves
   per-species lookups at runtime without network access.

## Key design decisions

- **Variable naming follows the `allometric` R convention**: `dsob` (DBH
  outside bark, cm), `hst` (stem height, m). This keeps cross-language
  interoperability clean.
- **Strict model type matching** in the registry: `"agb"` does not match
  `"crown_agb"`. Use `registry.query(response="agb")` for looser queries.
- **Back-transformation bias correction** (Sprugel 1983) is applied explicitly
  by models that log-transform internally, not silently.
- **No implicit unit conversion.** Callers pass cm for diameters and m for
  heights unless a model's docstring says otherwise.
- **Yield-table resolution is offline-first.** `resolve_yield_table()` reads
  only pre-ingested local data; no API calls at query time.

## Extension points

- Register a custom equation → `registry.register(ModelEntry(...))`
- Add a yield table provider → subclass `YieldTableProvider` in
  `yield_tables/providers.py`, add to the dispatch in `cli.py`
- Add a new H–D or biomass form → add a function to the relevant module, add
  it to the module's `_MODELS` dict so `select_model` discovers it

## Dependencies

- **Required**: NumPy, SciPy, pandas
- **Optional** (`[ml]`): scikit-learn, CatBoost
- **Yield tables** (per provider): R + ForestElementsR, R + et.nwfva, openpyxl,
  tabula-py + Java (for PDF sources)
- **Dev** (`[dev]`): pytest, pytest-cov
