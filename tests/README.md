# Tests — pylometree

**Last Updated:** 2026-09-15

pytest suite, discovered via `pyproject.toml` (`testpaths = ["tests"]`). No CI (all
pipelines are off workspace-wide since 2026-09-01) and no pre-commit hook — run it yourself
before committing.

```
tests/
|-- test_biomass.py          # AGB equations, bias correction
|-- test_crown_models.py     # crown → AGB
|-- test_data.py             # Tree / Stand dataclasses, per-hectare aggregation
|-- test_fitting.py          # curve_fit wrapper, bootstrap CIs, AIC selection
|-- test_hd_models.py        # the 12 height–diameter forms
|-- test_io.py               # CSV / DataFrame adapters
|-- test_metrics.py          # R², RMSE, MAE, bias, AIC, AICc, MSA, SSPB
|-- test_mixed_effects.py    # mixed-effects fitting
|-- test_registry.py         # ModelRegistry queries, strict model_type matching
|-- test_taxonomy.py         # Taxon resolution
|-- test_units.py            # pint-based unit conversion
|-- test_volume_models.py    # stem volume
`-- manual/                  # scratch for manual runs (gitignored results)
```

## Running

```shell
pip install -e ".[dev]"
pytest                       # everything
pytest tests/test_hd_models.py -v
pytest -k "forrester or zianis" -v
pytest --cov=src --cov-report=term-missing
```

## What to test

Business logic — equation forms, back-transformation bias correction, registry matching,
unit handling — not numpy, scipy or pandas internals. A new published equation gets a test
in `test_registry.py` that checks one known value against the source paper.
