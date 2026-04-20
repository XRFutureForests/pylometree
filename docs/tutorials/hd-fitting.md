# Tutorial — Fitting Height–Diameter Models

Fit and compare multiple H–D forms on inventory data, pick the best by AICc,
and report its predictions with uncertainty.

## Setup

```python
import numpy as np
import pandas as pd
from pylometree.fitting import fit_model, select_model, bootstrap_ci
from pylometree.metrics import model_report
```

Load a plot: any CSV with DBH (cm) and height (m) columns works. Here we use a
synthetic example:

```python
rng = np.random.default_rng(42)
dsob = np.array([5, 8, 12, 18, 24, 30, 38, 45, 52, 60], dtype=float)
hst  = 35 * (1 - np.exp(-0.04 * dsob))**1.2 + rng.normal(0, 0.8, dsob.size)
```

## Fit a single model

```python
result = fit_model(dsob, hst, model_name="chapman_richards")
print(result)
# FitResult('chapman_richards', R²=0.997, converged=True)
print(result.params)
# {'a': 34.9, 'b': 0.041, 'c': 1.18}
```

`result.predict(x)` returns heights for any DBH array.

## Compare all H–D forms

```python
best_name, best_result, all_results = select_model(dsob, hst)
print(f"Best model: {best_name} (AICc = {best_result.aicc:.2f})")

for r in all_results[:5]:
    print(f"  {r.model_name:<20} AICc={r.aicc:6.2f} R²={r.r2:.3f}")
```

`select_model` fits every entry in `HD_MODELS` and returns them sorted by AICc
(lower is better, and more informative than plain AIC for small samples).

## Bootstrap parameter CIs

```python
ci = bootstrap_ci(dsob, hst, model_name="chapman_richards", n_boot=2000, ci=0.95)
for name, (lo, hi) in ci.items():
    print(f"  {name}: [{lo:.3f}, {hi:.3f}]")
```

## Full report

```python
y_pred = best_result.predict(dsob)
report = model_report(hst, y_pred, n_params=len(best_result.params),
                      model_name=best_name)
print(report)
# {'r2': 0.997, 'rmse': 0.78, 'mae': 0.63, 'bias': -0.04,
#  'aic': -2.3, 'aicc': 0.7, 'msa': 3.4, 'sspb': -0.6}
```

MSA (Median Symmetric Accuracy) and SSPB (Signed Symmetric Percent Bias) are
robust under the asymmetric multiplicative errors typical of allometric data —
prefer them over RMSE/bias for cross-species or cross-size comparisons.

## Pitfalls

- **Starting values matter.** If a non-linear fit does not converge, pass
  `p0=[...]` explicitly. For `chapman_richards`, reasonable starts are
  `a≈max(y)`, `b≈0.03`, `c≈1.0`.
- **Do not pool species without testing.** A single H–D form rarely fits well
  across species. Fit per species, or include species as a random effect
  outside this library (e.g. via `statsmodels` MixedLM on log-transformed y).
- **Prefer AICc over AIC** whenever n/k < 40.
