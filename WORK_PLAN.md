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

## XRFF-131 — Publish pylometree to PyPI (Medium, assignee: Max)

**Context**: `growpy/pyproject.toml` currently uses `pylometree @ git+https://gitlab.uni-freiburg.de/...`. This works but is fragile (requires repo access, no version pinning). PyPI enables `pip install pylometree==0.1.0`.

### Steps

**1. Add `[project.urls]` to `pyproject.toml`**

```toml
[project.urls]
Homepage = "https://gitlab.uni-freiburg.de/xr-future-forests-lab/pylometree"
Repository = "https://gitlab.uni-freiburg.de/xr-future-forests-lab/pylometree"
"Bug Tracker" = "https://gitlab.uni-freiburg.de/xr-future-forests-lab/pylometree/-/issues"
```

**2. Verify `version = "0.1.0"` and all metadata in `pyproject.toml`**

Check: `name`, `description`, `authors`, `license`, `requires-python`, `dependencies`, `classifiers` — all already filled in. Confirm `README.md` renders correctly (it's the PyPI description).

**3. Install build tools**

```bash
pip install build twine
```

**4. Build**

```bash
cd /d/Git/pylometree
python -m build
# Creates dist/pylometree-0.1.0.tar.gz and dist/pylometree-0.1.0-py3-none-any.whl
```

**5. Check with twine**

```bash
twine check dist/*
```

Fix any warnings before upload.

**6. Upload to PyPI**

```bash
twine upload dist/*
# Prompts for PyPI username + API token
# Get token at: https://pypi.org/manage/account/token/
```

**7. Verify install**

```bash
pip install pylometree==0.1.0
python -c "import pylometree; print(pylometree.__version__)"
```

**8. Update growpy dependency**

In `growpy/pyproject.toml`, replace:
```toml
"pylometree @ git+https://gitlab.uni-freiburg.de/xr-future-forests-lab/pylometree.git",
```
with:
```toml
"pylometree>=0.1.0",
```

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
