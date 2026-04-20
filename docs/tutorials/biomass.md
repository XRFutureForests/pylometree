# Tutorial — Estimating Biomass

Compute aboveground biomass (AGB) and carbon stock for a plot using a
registered published equation.

## Setup

```python
from pylometree.data import Tree, Stand
from pylometree.registry import registry
```

## Single tree, single equation

```python
chave = registry.get("chave2014_pantropical")

tree = Tree(dbh=25.0, height=22.0, wood_density=0.60, species="Tectona grandis")
tree.estimate_agb(chave)

print(f"AGB   = {tree.agb:.1f} kg")
print(f"C     = {tree.carbon_stock:.1f} kg C")
```

`estimate_agb(entry)` calls `entry.predict(**covariates)` with the tree's
attributes. A tree missing a required covariate (e.g. `rho` for Chave 2014)
raises a clear error.

## Plot-level aggregation

```python
trees = [
    Tree(dbh=d, height=h, wood_density=0.65)
    for d, h in zip([15, 20, 25, 18, 22, 30, 12], [12, 17, 20, 14, 18, 23, 10])
]
stand = Stand(trees=trees, plot_area=0.1)  # ha

for t in stand:
    t.estimate_agb(chave)

print(f"Basal area = {stand.basal_area_per_ha:.1f} m²/ha")
print(f"AGB        = {stand.agb_mg_ha:.2f} Mg/ha")
print(f"Carbon     = {stand.carbon_stock_mg_ha:.2f} Mg C/ha")
print(stand.summary_df())
```

## Choosing an equation

`registry.query(...)` filters by metadata:

```python
# All AGB models
agb_models = registry.query(model_type="agb")

# Pantropical only
pan = registry.query(model_type="agb", region="pantropical")

# Models that use DBH and height as covariates
dh = [m for m in registry.query(model_type="agb")
      if set(m.covariates) >= {"dsob", "hst"}]
```

**Rule of thumb**: prefer a species- or region-specific equation when one
exists and the plot falls inside its calibration range. Fall back to
pantropical (Chave 2014) for tropical broadleaves outside calibrated regions.

## Registering your own equation

```python
from pylometree.registry import ModelEntry

def teak_agb(dsob, hst, a, b, **_):
    return a * (dsob**2 * hst) ** b

registry.register(ModelEntry(
    model_id="smith2024_teak_agb",
    model_type="agb",
    equation_form="AGB = a*(D²H)^b",
    response="agb",
    covariates=["dsob", "hst"],
    parameters={"a": 0.052, "b": 0.91},
    fn=teak_agb,
    species=["Tectona grandis"],
    region=["tropical_asia"],
    reference="Smith et al. (2024) FEM.",
    pub_year=2024,
    units={"agb": "kg", "dsob": "cm", "hst": "m"},
))

# Now usable like any built-in
tree.estimate_agb(registry.get("smith2024_teak_agb"))
```

## Back-transformation bias

Many biomass equations are fitted on log(AGB) and incur bias when
back-transformed. `pylometree` applies the Sprugel (1983) correction
`CF = exp(MSE/2)` automatically for models whose `ModelEntry` declares it;
no action needed from the caller.

## Validating on your data

Compute plot-level error on held-out inventory measurements:

```python
from pylometree.metrics import model_report

y_true = np.array([obs_agb_kg_per_tree])  # your destructively sampled AGB
y_pred = np.array([tree.agb for tree in stand])

print(model_report(y_true, y_pred, n_params=3, model_name="chave2014"))
```

Prefer MSA/SSPB over RMSE for cross-size comparison of biomass estimates.
