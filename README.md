# pylometree

A general-purpose Python toolkit for tree allometry — fitting, evaluating, and looking up allometric equations for height–diameter relationships, above- and below-ground biomass, crown structure, stem volume, and height–age growth.

---

## Features

| Module | Capability |
|---|---|
| `pylometree.models.hd` | 12 H–D equation forms (Chapman-Richards, Gompertz, Weibull, …) |
| `pylometree.models.biomass` | Power-law M1–M4, Chave 2014 pantropical, Musa NSUR |
| `pylometree.models.crown` | Crown-area/height → AGB (Jucker 2017, Htoo 2025) |
| `pylometree.models.volume` | Form-factor and power-law stem volume |
| `pylometree.fitting` | `scipy` curve-fit wrapper, bootstrap CIs, AIC-based model selection |
| `pylometree.metrics` | R², RMSE, MAE, bias, AIC, AICc, **MSA**, **SSPB** |
| `pylometree.registry` | Searchable model registry pre-loaded with published equations |
| `pylometree.data` | `Tree` and `Stand` dataclasses with plot-level aggregation |
| `pylometree.io` | Load trees from CSV or pandas DataFrame |
| `pylometree.yield_tables` | Multi-source yield table ingestion, store management, and resolution |

---

## Installation

```bash
# Basic install (NumPy, SciPy, pandas)
pip install pylometree

# With optional ML support (scikit-learn, CatBoost)
pip install "pylometree[ml]"

# Development (adds pytest, pytest-cov)
pip install "pylometree[dev]"
```

From source:

```bash
git clone https://gitlab.uni-freiburg.de/xr-future-forests-lab/pylometree
pip install -e ".[dev]"
```

Requires **Python ≥ 3.12**.

---

## Quick Start

### 1. Fit a height–diameter model

```python
import numpy as np
from pylometree.fitting import fit_model, select_model
from pylometree.models.hd import HD_MODELS

# Example field data (DBH in cm, height in m)
dbh    = np.array([5, 8, 12, 18, 24, 30, 38, 45])
height = np.array([6, 9, 13, 17, 21, 24, 27, 29])

# Fit a single model (convenience form – looks up HD_MODELS automatically)
result = fit_model(dbh, height, model_name="chapman_richards")
print(result)
# FitResult('chapman_richards', R²=0.998, converged=True)

# Predict with the fitted model
h_pred = result.predict(np.array([10, 20, 30]))

# Or pass an explicit function and parameters
from pylometree.models.hd import power_law
result2 = fit_model(
    fn=power_law, x=dbh, y=height,
    param_names=["a", "b"], p0=[1.0, 0.5],
)

# Select the best model from all 12 forms
best_name, best_result, all_results = select_model(dbh, height)
# Or with an explicit catalogue:
best_name, best_result, all_results = select_model(HD_MODELS, x=dbh, y=height)
```

### 2. Estimate biomass

```python
from pylometree.models.biomass import chave2014

# Chave et al. 2014 pantropical equation
agb_kg = chave2014(dsob=25.0, hst=22.0, rho=0.60)
print(f"AGB = {agb_kg:.1f} kg")
# AGB = 462.3 kg
```

### 3. Use the Tree dataclass

```python
from pylometree.data import Tree, Stand
from pylometree.registry import registry

tree = Tree(dbh=25.0, height=22.0, wood_density=0.60, species="Tectona grandis")

# Estimate AGB using a published model
chave = registry.get("chave2014_pantropical")
tree.estimate_agb(chave)
print(f"AGB  = {tree.agb:.1f} kg")
print(f"C    = {tree.carbon_stock:.1f} kg C")

# Build a stand and compute per-hectare stocks
trees = [Tree(dbh=d, height=h, wood_density=0.65)
         for d, h in zip([15, 20, 25, 18, 22], [12, 17, 20, 14, 18])]
stand = Stand(trees=trees, plot_area=0.1)

# Apply biomass model to every tree in the stand
for t in stand:
    t.estimate_agb(chave)

print(f"AGB  = {stand.agb_mg_ha:.2f} Mg/ha")
print(f"Carbon = {stand.carbon_stock_mg_ha:.2f} Mg C/ha")
print(stand.summary_df())
```

### 4. Query published equations

```python
from pylometree.registry import registry

# Summary of all built-in models
print(registry.summary())
# DataFrame summary (requires pandas)
print(registry.summary_df()[["model_id", "model_type", "species", "pub_year"]])

# Query by type and region
agb_models = registry.query(model_type="agb", region="pantropical")

# Predict with a published model
chave = registry.get("chave2014_pantropical")
agb   = chave.predict(dsob=30.0, hst=25.0, rho=0.55)
print(f"AGB = {agb:.1f} kg")

# Or use callable shortcut on the registry
agb = registry("chave2014_pantropical", dsob=30.0, hst=25.0, rho=0.55)
```

### 5. Register your own equation

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

### 6. Load data from CSV

```python
from pylometree.io import read_csv  # or stand_from_csv (alias)

stand = read_csv(
    "survey_plot.csv",
    plot_area=0.25,
    dbh_col="DBH_cm",
    height_col="H_m",
    wood_density="rho",       # extra Tree attrs via **kwargs
    species_col="species",
)
print(f"n = {len(stand)}, BA = {stand.basal_area_per_ha:.1f} m²/ha")
```

---

## Included Models

### H–D relationship forms (`pylometree.models.hd`)

| Name | Equation |
|---|---|
| `chapman_richards` | $H = a(1-e^{-bD})^c$ |
| `exponential_3p` | $H = a - be^{-cD}$ |
| `gompertz` | $H = a\cdot e^{-e^{b-cD}}$ |
| `hyperbolic` | $H = a + b/D$ |
| `michaelis_menten` | $H = aD/(b+D)$ |
| `power_law` | $H = aD^b$ |
| `log_linear` | $H = e^{a+b\ln D}$ |
| `logistic_3p` | $H = a/(1+e^{b-cD})$ |
| `weibull_4p` | $H = a(1-e^{-bD^c})+d$ |
| `korf` | $H = a\cdot e^{-b/D^c}$ |
| `von_bertalanffy` | $H = a(1-be^{-cD})^3$ |

### Published registry entries

| Model ID | Type | Source |
|---|---|---|
| `chave2014_pantropical` | `agb` | Chave et al. (2014) GCB |
| `jucker2017_crown_agb` | `crown_agb` | Jucker et al. (2017) GCB |
| `laskar2020_musa_agb` | `agb` | Laskar et al. (2020) JEM |
| `laskar2020_musa_hd_exponential` | `hd` | Laskar et al. (2020) |
| `chapman_richards_generic_hd` | `hd` | Richards (1959) |
| `pretzsch2025_*_height_age` | `height_age` | Pretzsch et al. (2025) Trees |

---

## Metrics

| Metric | Function | Notes |
|---|---|---|
| R² | `r2(y_true, y_pred)` | Coefficient of determination |
| RMSE | `rmse(y_true, y_pred)` | Root mean squared error |
| MAE | `mae(y_true, y_pred)` | Mean absolute error |
| Bias | `bias(y_true, y_pred)` | Mean signed error |
| AIC | `aic(y_true, y_pred, k)` | Akaike Information Criterion |
| AICc | `aicc(y_true, y_pred, k)` | AIC corrected for small samples |
| **MSA** | `msa(y_true, y_pred)` | Median Symmetric Accuracy (%) — Burt & Disney |
| **SSPB** | `sspb(y_true, y_pred)` | Signed Symmetric Percent Bias (%) — Burt & Disney |

```python
from pylometree.metrics import model_report
report = model_report(y_obs, y_pred, n_params=3, model_name="Chapman-Richards")
# {'r2': 0.997, 'rmse': 0.42, 'mae': 0.31, 'bias': -0.02,
#  'aic': -18.7, 'aicc': -15.2, 'msa': 2.1, 'sspb': -0.4}
```

---

## Yield Tables

The `pylometree.yield_tables` module ingests, normalizes, and resolves forestry yield tables from multiple sources into a single standardized CSV format.

### Ingestion

Run `python -m pylometree.yield_tables.cli` to extract yield tables from external sources into a local store:

```bash
# List available providers and their status
python -m pylometree.yield_tables.cli --list-providers

# Ingest all available providers into a store directory
python -m pylometree.yield_tables.cli --store-dir ./yield_store

# Ingest specific providers with config
python -m pylometree.yield_tables.cli \
  --providers forest_elements et_nwfva carbon_et_xlsx \
  --config xlsx_path=/data/C_ET_pub.xlsx \
  --store-dir ./yield_store

# Clean store before re-ingesting
python -m pylometree.yield_tables.cli --clean --store-dir ./yield_store
```

### Providers

| Provider | Source | Species | Dependencies |
| --- | --- | --- | --- |
| `forest_elements` | ForestElementsR (classical German tables) | 14 species | R + ForestElementsR |
| `et_nwfva` | NW-FVA 2021 (Northwest Germany) | 5 species | R + et.nwfva |
| `carbon_et_xlsx` | Kohlenstoff-Ertragstafeln (Schober) | 5 species | openpyxl |
| `forest_yield_uk` | UK Forest Yield (FC Booklet 48) | 16 species | tabula-py + Java |
| `pryor_cherry` | Wild cherry (FC Bulletin 75) | 1 species | tabula-py + Java |
| `nova_scotia` | Nova Scotia Report 22 | 8 species | tabula-py + Java |
| `usda_stocking` | USDA stocking/yield tables | varies | tabula-py + Java |
| `parametric_models` | JSON growth model files | any | none |

Providers are gracefully disabled when dependencies are missing. Use `--list-providers` to check availability.

### Resolution

At runtime, `resolve_yield_table()` looks up the best available table for a species using only pre-ingested local data (no API calls):

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
    print(result.ages)     # [20, 25, 30, ...]
    print(result.heights)  # [7.1, 9.2, 11.5, ...] (meters)
    print(result.dbhs)     # [0.075, 0.095, 0.115, ...] (meters)
```

Resolution priority:

1. **Local CSV** in `yield_tables_dir` (by standardized species name)
2. **Ingested store** (best match by region and site index)

### Store format

Each ingested table is a CSV with columns: `age`, `height`, `dbh`, `species_latin`, `region`, `management`, `site_index`, `source`, `table_id`, and optionally `volume`. A `manifest.csv` index enables per-species lookup and multi-criteria selection.

### Parametric models

The `parametric_models` provider evaluates JSON growth model files (Chapman-Richards, Korf, Lundqvist) on an age grid and outputs standard yield table CSVs. This allows species without published yield tables to be covered via fitted parametric equations:

```json
{
    "species_latin": "Acer campestre",
    "height_model": {"type": "chapman_richards", "A": 20.0, "k": 0.025, "p": 1.2, "y0": 0.5},
    "dbh_model": {"type": "chapman_richards", "A": 40.0, "k": 0.020, "p": 1.1, "y0": 0.0},
    "age_range": [10, 150],
    "age_step": 5,
    "site_index": 1.0
}
```

---

## Design Notes

- **Variable naming** follows the [allometric R package](https://allometric.org/) convention: `dsob` (DBH outside bark, cm), `hst` (total stem height, m).
- **AGB back-transformation bias** is corrected using Sprugel (1983): $CF = e^{MSE/2}$.
- **MSA and SSPB** are forestry-specific accuracy metrics from Burt & Disney (*treeallom*) that are robust to asymmetric multiplicative errors typical in biomass data.
- The registry uses **exact `model_type` matching** (`"agb"` will not match `"crown_agb"`); use `registry.query(response="agb")` to search by response variable instead.

---

## References

- Chave J et al. (2014) Improved allometric models to estimate the aboveground biomass of tropical trees. *Global Change Biology* 20:3177–3190.
- Jucker T et al. (2017) Allometric equations for integrating remote sensing imagery into forest monitoring programmes. *Global Change Biology* 23:177–190.
- Pretzsch H et al. (2025) Estimating tree age from height using the extended Chapman-Richards function. *Trees*. doi:10.1007/s00468-025-02692-0
- Laskar S Y et al. (2020) Allometric models for estimating biomass of wild *Musa balbisiana*. *Journal of Environmental Management*.
- Burt A & Disney M — [treeallom R package](https://github.com/apburt/treeallom) (MSA, SSPB definitions).
- Sprugel D G (1983) Correcting for bias in log-transformed allometric equations. *Ecology* 64:209–210.

---

## License

MIT © pylometree contributors
