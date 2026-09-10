# Runbook — pylometree

Install it, fit an equation, use a published one, ingest yield tables, and read the result
correctly. For what the library is and the design behind it, see [README.md](README.md).

---

## 1. Install

```bash
pip install pylometree                 # NumPy, SciPy, pandas
pip install "pylometree[ml]"           # + scikit-learn, CatBoost
pip install "pylometree[dev]"          # + pytest, pytest-cov
```

From source:

```bash
git clone https://github.com/XRFutureForests/pylometree
cd pylometree
pip install -e ".[dev]"
pytest
```

Python ≥ 3.12. Conda environments only in this workspace — never create a `.venv`.

---

## 2. Fit an equation

```python
from pylometree.fitting import fit_model, select_model
from pylometree.models.hd import HD_MODELS, power_law
```

| Call | Use when |
|------|----------|
| `fit_model(x, y, model_name="chapman_richards")` | You know which form you want; it is looked up in `HD_MODELS` |
| `fit_model(fn=power_law, x=…, y=…, param_names=["a","b"], p0=[1.0, 0.5])` | You are fitting a function that is not in the catalogue |
| `select_model(x, y)` | Let AIC choose among all 12 forms |
| `select_model(HD_MODELS, x=…, y=…)` | Same, against an explicit catalogue |

`fit_model` returns a `FitResult` — inspect `.converged` before trusting `.predict()`.

```python
result = fit_model(dbh, height, model_name="chapman_richards")
if result.converged:
    h = result.predict(new_dbh)
```

### Judging the fit

```python
from pylometree.metrics import model_report
model_report(y_obs, y_pred, n_params=3, model_name="Chapman-Richards")
# {'r2': 0.997, 'rmse': 0.42, 'mae': 0.31, 'bias': -0.02,
#  'aic': -18.7, 'aicc': -15.2, 'msa': 2.1, 'sspb': -0.4}
```

| Metric | Function | Read it as |
|--------|----------|-----------|
| R² | `r2` | Variance explained |
| RMSE / MAE | `rmse` / `mae` | Error in the response's own units |
| Bias | `bias` | Mean signed error — systematic over/under-prediction |
| AIC / AICc | `aic` / `aicc` | Model comparison; AICc for small samples |
| **MSA** | `msa` | Median Symmetric Accuracy (%) — the one to quote for biomass |
| **SSPB** | `sspb` | Signed Symmetric Percent Bias (%) — direction of that error |

For biomass, prefer MSA/SSPB over R²: errors there are multiplicative and asymmetric, and R²
flatters a model that is badly wrong on large trees.

---

## 3. Use a published equation

```python
from pylometree.registry import registry

print(registry.summary())                                   # all built-in models
registry.summary_df()[["model_id", "model_type", "species", "pub_year"]]

agb_models = registry.query(model_type="agb", region="pantropical")

chave = registry.get("chave2014_pantropical")
agb   = chave.predict(dsob=30.0, hst=25.0, rho=0.55)        # kg
agb   = registry("chave2014_pantropical", dsob=30.0, hst=25.0, rho=0.55)   # shortcut
```

**Units are yours to get right.** `dsob` is cm, `hst` is m, `rho` is g/cm³, `agb` comes back
in kg. Nothing is converted for you.

`model_type` matches exactly — `"agb"` will not return `"crown_agb"` entries. Search by
response instead:

```python
registry.query(response="agb")
```

### Register your own

```python
from pylometree.registry import registry, ModelEntry

def my_agb(dsob, hst, a, b, **_):
    return a * (dsob**2 * hst) ** b

registry.register(ModelEntry(
    model_id="smith2024_teak_agb",
    model_type="agb",
    equation_form="AGB = a*(D²H)^b",
    response="agb",
    covariates=["dsob", "hst"],
    parameters={"a": 0.052, "b": 0.91},
    fn=my_agb,
    species=["Tectona grandis"],
    region=["tropical_asia"],
    reference="Smith et al. (2024) Forest Ecology and Management.",
    pub_year=2024,
    units={"agb": "kg", "dsob": "cm", "hst": "m"},
))
```

Keep the parameter names convention-compliant (`dsob` / `hst` / `rho`) and always fill
`units` — an entry without them cannot be used safely by anyone else.

---

## 4. Load a plot

```python
from pylometree.io import read_csv          # stand_from_csv is an alias

stand = read_csv(
    "survey_plot.csv",
    plot_area=0.25,
    dbh_col="DBH_cm",
    height_col="H_m",
    wood_density="rho",       # extra Tree attributes via **kwargs
    species_col="species",
)
print(f"n = {len(stand)}, BA = {stand.basal_area_per_ha:.1f} m²/ha")
```

`plot_area` is in hectares and is what every per-hectare aggregate depends on. Get it wrong
and every `*_mg_ha` figure is wrong by the same factor.

---

## 5. Yield tables

Ingestion is a **separate, one-off step**. At runtime nothing goes to the network.

### Ingest

```bash
# what is available on this machine
python -m pylometree.yield_tables.cli --list-providers

# ingest everything available
python -m pylometree.yield_tables.cli --store-dir ./yield_store

# ingest specific providers with config
python -m pylometree.yield_tables.cli \
  --providers forest_elements et_nwfva carbon_et_xlsx \
  --config xlsx_path=/data/C_ET_pub.xlsx \
  --store-dir ./yield_store

# start clean
python -m pylometree.yield_tables.cli --clean --store-dir ./yield_store
```

| Provider | Source | Species | Needs |
|---|---|---|---|
| `forest_elements` | ForestElementsR (classical German tables) | 14 | R + ForestElementsR |
| `et_nwfva` | NW-FVA 2021 (Northwest Germany) | 5 | R + et.nwfva |
| `carbon_et_xlsx` | Kohlenstoff-Ertragstafeln (Schober) | 5 | openpyxl |
| `forest_yield_uk` | UK Forest Yield (FC Booklet 48) | 16 | tabula-py + Java |
| `pryor_cherry` | Wild cherry (FC Bulletin 75) | 1 | tabula-py + Java |
| `nova_scotia` | Nova Scotia Report 22 | 8 | tabula-py + Java |
| `usda_stocking` | USDA stocking/yield tables | varies | tabula-py + Java |
| `parametric_models` | JSON growth model files | any | none |

A provider whose dependency is missing is **silently disabled**, not an error — so always
check `--list-providers` before concluding a species is uncovered.

### Resolve at runtime

```python
from pylometree.yield_tables import resolve_yield_table

result = resolve_yield_table(
    species_common="Norway spruce",
    species_std="norway_spruce",
    yield_tables_dir=Path("data/input/yield_tables"),
    store_dir=Path("data/input/yield_tables/store"),
    preferred_site_index=32.0,
    preferred_region="DE",
)
if result:
    result.ages, result.heights, result.dbhs      # dbhs in metres, heights in metres
```

Resolution order: a **local CSV** in `yield_tables_dir` matched by standardised species name,
then the **ingested store**, best match by region and site index.

### Store format

One CSV per table with `age`, `height`, `dbh`, `species_latin`, `region`, `management`,
`site_index`, `source`, `table_id`, optionally `volume`; a `manifest.csv` indexes them for
per-species lookup.

### Covering a species with no published table

The `parametric_models` provider evaluates a JSON growth model on an age grid and emits a
standard yield-table CSV:

```json
{
    "species_latin": "Acer campestre",
    "height_model": {"type": "chapman_richards", "A": 20.0, "k": 0.025, "p": 1.2, "y0": 0.5},
    "dbh_model":    {"type": "chapman_richards", "A": 40.0, "k": 0.020, "p": 1.1, "y0": 0.0},
    "age_range": [10, 150],
    "age_step": 5,
    "site_index": 1.0
}
```

Chapman-Richards, Korf and Lundqvist forms are supported.

---

## 6. Troubleshooting

**`fit_model` returns `converged=False`**
Give it a starting point: `p0=[...]`. Non-linear forms (Weibull, Korf, von Bertalanffy) are
sensitive to initial values, and a bad `p0` fails silently into a flat fit.

**A registry query returns nothing**
`model_type` matches exactly. `"agb"` does not match `"crown_agb"` — use
`registry.query(response="agb")`.

**Biomass looks systematically low**
Log-transformed equations need the Sprugel (1983) back-transformation correction. Check
whether the equation you are calling applies it, and read SSPB rather than R².

**Per-hectare figures are off by a round factor**
`plot_area` is hectares, not m².

**A yield-table provider silently produced nothing**
Its dependency is missing — R + ForestElementsR, Java for the `tabula-py` providers, openpyxl
for the XLSX one. `--list-providers` shows availability.

**`resolve_yield_table` returns `None`**
Nothing matched that species name. Check the standardised name against the manifest, and
confirm ingestion actually ran for a provider that covers it.

**A species has no published equation at all**
Report it rather than substituting a related species — that is the project rule for age and
biomass fills, and the reason coverage is stated per species in
[docs/species-reference.md](docs/species-reference.md).
