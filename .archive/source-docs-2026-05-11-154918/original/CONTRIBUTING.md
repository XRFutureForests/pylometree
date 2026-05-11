# Contributing

Thanks for your interest in contributing. This project is developed by the
XR Future Forests Lab at the University of Freiburg.

## Ways to contribute

- **Report bugs** via the [GitLab issue tracker](https://gitlab.uni-freiburg.de/xr-future-forests-lab/pylometree/-/issues).
- **Add a published equation** — register it in
  `src/pylometree/registry/published.py` with full citation metadata.
- **Add a yield-table provider** — subclass `YieldTableProvider` in
  `src/pylometree/yield_tables/providers.py`. See
  [docs/tutorials/yield-tables.md](docs/tutorials/yield-tables.md).
- **Improve test coverage** — current gaps: crown models, volume models, I/O
  layer, registry queries.
- **Improve documentation** — tutorials, species reference notes, methodology.

## Development workflow

1. Editable install with dev extras: `pip install -e ".[dev]"`.
2. Run tests: `pytest`.
3. Make focused changes — one logical change per merge request.
4. Update `CHANGELOG.md` under `[Unreleased]` for user-visible changes.
5. Open a merge request with a clear description.

## Repository structure

- `src/pylometree/models/` — equation implementations (pure functions)
- `src/pylometree/fitting/` — nonlinear fitting & model selection
- `src/pylometree/metrics/` — R², AIC, MSA, SSPB, etc.
- `src/pylometree/registry/` — published-equation registry
- `src/pylometree/data/` — Tree and Stand dataclasses
- `src/pylometree/io/` — CSV/DataFrame adapters
- `src/pylometree/yield_tables/` — multi-source yield-table ingestion
- `tests/` — test suite
- `docs/` — architecture, API reference, tutorials, species reference

## Code style

- **Python**: Black (88 char line length), snake_case, type hints on public
  functions.
- **Naming convention**: follows the [allometric R package](https://allometric.org/):
  `dsob` (DBH outside bark, cm), `hst` (stem height, m).
- **No implicit unit conversion** in equations — document expected units in
  every function docstring.
- `.editorconfig` enforces whitespace conventions.

## Adding a published equation

```python
from pylometree.registry import registry, ModelEntry

def my_equation(dsob, hst, a, b, **_):
    return a * (dsob**2 * hst) ** b

registry.register(ModelEntry(
    model_id="author_year_species_agb",
    model_type="agb",
    equation_form="AGB = a*(D²H)^b",
    response="agb",
    covariates=["dsob", "hst"],
    parameters={"a": ..., "b": ...},
    fn=my_equation,
    species=["..."],
    region=["..."],
    reference="Author et al. (YEAR) Journal Vol:pp.",
    pub_year=YEAR,
    units={"agb": "kg", "dsob": "cm", "hst": "m"},
))
```

Add the call to `src/pylometree/registry/published.py` and a corresponding
test in `tests/test_published_registry.py`.

## Questions

Open an issue or contact the maintainer.
