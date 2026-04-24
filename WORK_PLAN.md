# pylometree — Work Plan

Linear: [XRFF team](https://linear.app/geosense-ufr/team/XRFF/all)

# pylometree — Work Plan

Linear: [XRFF team](https://linear.app/geosense-ufr/team/XRFF/all)

**Last updated:** 2026-04-23

---

## Status

🟢 **XRFF-131 complete.** Decision: skip PyPI, keep git-based dependency.

---

## Completed

| Issue | Status | Notes |
|---|---|---|
| [XRFF-131](https://linear.app/geosense-ufr/issue/XRFF-131) Publish pylometree to PyPI | ✅ DONE | Decision: skip PyPI, keep git dep in growpy/pyproject.toml |

### Decision rationale

PyPI adds friction (token management, versioning discipline, release overhead) without immediate benefit. Git-based dep works fine for current team size/workflow. Revisit when external users need the package.

---

## Support: XRFF-39 (height gap-fill) — no code changes needed

digital-twin-db will call `pylometree` H-D models to predict missing heights. Verify coverage:

```python
from pylometree.yield_tables import get_yield_table
from pylometree.models.hd import fit_hd_model

# Ecosense dominant species — all must resolve without error
for species in ["European Beech", "Norway Spruce", "Scots Pine", "European Oak", "Silver Fir"]:
    yt = get_yield_table(species)
    model = fit_hd_model(yt)
    print(f"{species}: H(30cm DBH) = {model.predict(30):.1f} m")
```

If any species raises `ValueError` or returns unreasonable values (< 5 m or > 40 m for mature trees), add or fix the yield table entry before XRFF-39 runs.

---

## See Also

- `src/pylometree/models/hd.py` — H-D model implementations
- `src/pylometree/yield_tables/` — yield table loading and provider logic
- [XRFF-131](https://linear.app/geosense-ufr/issue/XRFF-131) — PyPI publication
- [XRFF-39](https://linear.app/geosense-ufr/issue/XRFF-39) — height gap-fill (digital-twin-db)
