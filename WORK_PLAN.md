# pylometree — Work Plan

Linear: [XRFF team](https://linear.app/geosense-ufr/team/XRFF/all)

## Issue Sequence

```
XRFF-131  (publish to PyPI — enables proper versioned dep)
    └─► update growpy pyproject.toml to use PyPI dep

Support for XRFF-39 (height gap-fill in digital-twin-db)  ← no code changes here,
                                                              just verify H-D model
                                                              coverage for Ecosense species
```

---

## XRFF-131 — Keep git-based dependency (Medium, assignee: Max)

**Decision**: Skip PyPI publication for now. Keep `growpy/pyproject.toml` using the git-based dependency:

```toml
"pylometree @ git+https://gitlab.uni-freiburg.de/xr-future-forests-lab/pylometree.git",
```

**Rationale**: PyPI adds friction (token management, versioning discipline, release overhead) without immediate benefit. The git-based dep works fine for the current team size and workflow. Revisit PyPI when external users need the package.

**Open questions**:

- When should we reconsider? (external collaborators, public ecosystem, CI/CD simplification)
- What versioning discipline is needed regardless of install method? (semver, changelog)

---

## Support: XRFF-39 (height gap-fill) — no code changes needed

digital-twin-db will call `pylometree` H-D models to predict missing heights. Verify coverage now:

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
