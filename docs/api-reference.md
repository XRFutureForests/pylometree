# API Reference

Public interface of `pylometree`. Private helpers (prefixed with `_`) are not
covered here and are not part of the stable API.

All function signatures use the [allometric R package naming convention](https://allometric.org/):
`dsob` = diameter at breast height outside bark (cm), `hst` = total stem
height (m).

---

## `pylometree.models.hd`

Height–diameter equation forms. Every function has the signature
`fn(dsob, *params) -> height` and is vectorized over NumPy arrays.

| Function | Parameters | Equation |
|---|---|---|
| `chapman_richards(D, a, b, c)` | a, b, c | `a * (1 - exp(-b*D))**c` |
| `exponential_3p(D, a, b, c)` | a, b, c | `a - b*exp(-c*D)` |
| `gompertz(D, a, b, c)` | a, b, c | `a * exp(-exp(b - c*D))` |
| `hyperbolic(D, a, b)` | a, b | `a + b/D` |
| `michaelis_menten(D, a, b)` | a, b | `a*D / (b + D)` |
| `power_law(D, a, b)` | a, b | `a * D**b` |
| `log_linear(D, a, b)` | a, b | `a + b*log(D)` |
| `logistic_3p(D, a, b, c)` | a, b, c | `a / (1 + exp(b - c*D))` |
| `weibull_4p(D, a, b, c, d)` | a, b, c, d | `a*(1 - exp(-b*D**c)) + d` |
| `korf(D, a, b, c)` | a, b, c | `a * exp(-b / D**c)` |
| `von_bertalanffy(D, a, b, c)` | a, b, c | `a * (1 - b*exp(-c*D))**3` |

`HD_MODELS: dict[str, callable]` exposes all forms for iteration.

---

## `pylometree.models.biomass`

| Function | Purpose |
|---|---|
| `power_law_m1(D, a, b)` | AGB = a * D^b |
| `power_law_m2(D, H, a, b, c)` | AGB = a * D^b * H^c |
| `power_law_m3(D, H, rho, a, b, c, d)` | AGB = a * D^b * H^c * rho^d |
| `power_law_m4(DH2rho, a, b)` | AGB = a * (D²Hρ)^b |
| `chave2014(dsob, hst, rho)` | Chave et al. 2014 pantropical AGB (kg) |
| `musa_nsur(D, H)` | Non-Seemingly Unrelated Regression for *Musa balbisiana* |

---

## `pylometree.models.crown`

| Function | Purpose |
|---|---|
| `jucker2017(ca, h, rho)` | Crown area + height → AGB (Jucker 2017) |
| `htoo2025(...)` | Htoo et al. 2025 crown-based AGB |

---

## `pylometree.models.volume`

| Function | Purpose |
|---|---|
| `form_factor(dsob, hst, f)` | `V = f * π/4 * D² * H` |
| `power_law_volume(dsob, hst, a, b, c)` | `V = a * D^b * H^c` |

---

## `pylometree.fitting`

```python
from pylometree.fitting import fit_model, select_model, bootstrap_ci
```

### `fit_model(x, y, *, model_name=None, fn=None, param_names=None, p0=None, bounds=None) -> FitResult`

Fit a nonlinear model via `scipy.optimize.curve_fit`. Either pass `model_name`
(looked up in `HD_MODELS`) or an explicit `fn` with `param_names` and `p0`.

`FitResult` fields:
- `model_name: str`
- `params: dict[str, float]`
- `cov: np.ndarray`
- `r2: float`, `rmse: float`, `aic: float`, `converged: bool`
- `.predict(x) -> np.ndarray`

### `select_model(x, y, catalogue=HD_MODELS) -> (best_name, best_result, all_results)`

Fit every model in `catalogue`, return the one with lowest AICc plus a list of
all `FitResult`s sorted by AICc.

### `bootstrap_ci(x, y, model_name, n_boot=1000, ci=0.95) -> dict`

Non-parametric bootstrap confidence intervals for each parameter.

---

## `pylometree.metrics`

All functions take `(y_true, y_pred)` as NumPy-compatible arrays.

| Function | Returns |
|---|---|
| `r2(y_true, y_pred)` | Coefficient of determination |
| `rmse(y_true, y_pred)` | Root mean squared error |
| `mae(y_true, y_pred)` | Mean absolute error |
| `bias(y_true, y_pred)` | Mean signed error |
| `aic(y_true, y_pred, k)` | Akaike Information Criterion |
| `aicc(y_true, y_pred, k)` | AIC corrected for small samples |
| `msa(y_true, y_pred)` | Median Symmetric Accuracy (%) |
| `sspb(y_true, y_pred)` | Signed Symmetric Percent Bias (%) |
| `model_report(y_true, y_pred, n_params, model_name=None) -> dict` | Bundle of all metrics |

---

## `pylometree.registry`

```python
from pylometree.registry import registry, ModelEntry, ModelRegistry
```

### `ModelEntry`

Metadata container for a published equation.

Required fields: `model_id`, `model_type`, `equation_form`, `response`,
`covariates`, `parameters`, `fn`, `species`, `region`, `reference`, `pub_year`,
`units`.

Methods:
- `.predict(**covariates) -> float | np.ndarray` — call `fn` with bound `parameters`

### `ModelRegistry`

- `register(entry: ModelEntry)` — add an entry
- `get(model_id: str) -> ModelEntry`
- `query(*, model_type=None, species=None, region=None, response=None) -> list[ModelEntry]`
- `summary() -> str` — text summary
- `summary_df() -> pandas.DataFrame` — tabular summary
- `__call__(model_id, **covariates)` — shortcut for `get(id).predict(**cov)`

The global `registry` is populated at import time with entries from
`pylometree.registry.published`.

---

## `pylometree.data`

### `Tree`

```python
Tree(dbh: float, height: float | None = None, wood_density: float | None = None,
     species: str | None = None, **extra)
```

Attributes computed on demand:
- `.basal_area` — m² (from DBH)
- `.agb` — set by `estimate_agb(entry)` (kg)
- `.carbon_stock` — derived from `.agb` via `CARBON_FRACTION` (default 0.47)

### `Stand`

```python
Stand(trees: list[Tree], plot_area: float)  # plot_area in ha
```

Per-hectare aggregates:
- `.basal_area_per_ha` (m²/ha)
- `.agb_mg_ha` (Mg/ha)
- `.carbon_stock_mg_ha` (Mg C/ha)
- `.summary_df()` — pandas DataFrame view

Iterable: `for tree in stand: ...`

---

## `pylometree.io`

```python
from pylometree.io import read_csv  # alias: stand_from_csv
```

### `read_csv(path, *, plot_area, dbh_col, height_col=None, **extra_cols) -> Stand`

Load a plot inventory from CSV. Each row becomes a `Tree`; extra column
mappings are passed through as `Tree(**kwargs)`.

---

## `pylometree.yield_tables`

```python
from pylometree.yield_tables import resolve_yield_table, YieldTableRecord
```

### `resolve_yield_table(*, species_common, species_std, yield_tables_dir, store_dir, preferred_site_index=None, preferred_region=None) -> YieldTableRecord | None`

Offline lookup for the best-matching yield table. Priority:
1. Local CSV in `yield_tables_dir` keyed by standardized species name
2. Ingested store (best match by region, then site index)

### `YieldTableRecord`

- `.ages: np.ndarray` — years
- `.heights: np.ndarray` — meters
- `.dbhs: np.ndarray` — meters
- `.species_latin: str`, `.region: str`, `.site_index: float | None`
- `.source: str`, `.table_id: str`

### CLI — `pylometree-ingest`

Build or refresh a local store from external providers. See
[tutorials/yield-tables.md](tutorials/yield-tables.md) for a worked example.
