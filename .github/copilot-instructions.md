# Project Guidelines — pylometree

General-purpose Python toolkit for tree allometry (height–diameter, biomass, crown, volume, growth models).

## Build and Test

```bash
pip install -e ".[dev]"       # editable install with pytest
pytest                        # runs tests/ with -v (see pyproject.toml)
pytest tests/test_hd_models.py -k "TestMonotonicity"  # targeted run
```

Requires **Python ≥ 3.10**. Core deps: NumPy, SciPy, pandas.

## Architecture

```
src/pylometree/
  models/        # Pure functions: hd, biomass, crown, volume
  fitting/       # scipy curve_fit wrapper, bootstrap CI, model selection
  metrics/       # R², RMSE, MAE, bias, AIC/AICc/BIC, MSA, SSPB
  registry/      # Global ModelRegistry + published equations
  data/          # Tree / Stand dataclasses, constants
  io/            # CSV / DataFrame loaders
  yield_tables/  # Provider-based ingestion, store, CLI, species mapping
```

**Two-tier model storage:**
- **Catalogues** (`HD_MODELS`, `BIOMASS_MODELS`, …) in `models/*.py` — dict of model forms used by `fit_model()` / `select_model()`.
- **Registry** (`registry/base.py`) — global singleton of published equations with fixed parameters. Auto-populated on import via `registry/published.py`.

## Code Style

- **`from __future__ import annotations`** at the top of every module.
- **Type hints** on all public functions. Use `ArrayLike` from `numpy.typing` for array inputs, `np.ndarray` for returns.
- **NumPy-style docstrings** with `Parameters`, `Returns`, `References` sections.
- **Allometric variable names** from forestry convention: `dsob` (diameter outside bark, cm), `hst` (total height, m), `rho` (wood density, g/cm³), `agb`/`bgb` (biomass, kg), `d2h` (DBH²×H composite).
- Helper `_arr(x) = np.asarray(x, dtype=float)` at module top for input normalization — use it in every model function.

## Conventions

### Adding a model function

1. Define a pure function in the appropriate `models/*.py` module accepting `ArrayLike` args → `np.ndarray`.
2. Start with `_arr()` conversion for each input.
3. Add it to the module's catalogue dict with `fn`, `params`, `p0` (initial guesses), `bounds`, and `notes`.
4. If it's a published equation, also register a `ModelEntry` in `registry/published.py` with a lambda wrapper that accepts `**_`.

### Adding a published equation to the registry

```python
ModelEntry(
    model_id="author_year_descriptor",
    model_type="agb",             # agb | bgb | hd | crown_agb | volume | height_age
    equation_form="M = a·(ρD²H)^b",
    response="agb",
    covariates=["dsob", "hst", "rho"],
    parameters={"a": 0.0673, "b": 0.976},
    fn=lambda dsob, hst, rho, **_: my_func(dsob, hst, rho),
    species=["Pantropical"],
    region=["pantropical"],
    reference="Author et al. (Year) Journal. DOI:...",
    pub_year=2024,
    units={"agb": "kg", "dsob": "cm", "hst": "m"},
)
```

### Dataclass rules

- `Tree` attributes are `Optional[float]` with `None` defaults. Derived properties (`basal_area`, `d2h`) return `None` when inputs are missing.
- `Stand` requires `plot_area_ha` for per-hectare methods — these raise `ValueError` if it's `None`.

### Testing patterns

- Group tests by concern: `TestMonotonicity`, `TestOutputShape`, `TestSpecific`.
- **Parametrize** over catalogue dicts: `@pytest.mark.parametrize("name,entry", HD_MODELS.items())`.
- Use `np.testing.assert_allclose()` for numerical comparisons.
- For parameter recovery tests, generate synthetic data from known params + noise.

### Units

Units are stored in `ModelEntry.units` but **not enforced at runtime**. Document expected units in docstrings.
