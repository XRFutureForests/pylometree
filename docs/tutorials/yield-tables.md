# Tutorial — Yield Tables

Ingest growth and yield tables from multiple external sources into a local
store, then resolve per-species lookups offline at runtime.

## Why a local store?

Yield tables live in many incompatible formats: R packages (ForestElementsR,
et.nwfva), Excel files (Kohlenstoff-Ertragstafeln), PDF booklets (UK Forest
Yield, Nova Scotia Report 22), JSON parametric models. `pylometree` normalizes
all of them into a single CSV schema so downstream code has one shape to
handle.

The store is **offline-first**. After ingestion, `resolve_yield_table` does
no network or subprocess calls — it reads CSVs from disk.

## Ingestion

List what is available in your environment:

```bash
pylometree-ingest --list-providers
```

Providers appear as enabled / disabled depending on whether their dependencies
(R, Java for PDF parsing, openpyxl, etc.) are installed.

Run ingestion:

```bash
pylometree-ingest --store-dir ./yield_store
```

Or pick specific providers:

```bash
pylometree-ingest \
  --providers forest_elements et_nwfva carbon_et_xlsx \
  --config xlsx_path=/data/C_ET_pub.xlsx \
  --store-dir ./yield_store
```

Clean and re-ingest:

```bash
pylometree-ingest --clean --store-dir ./yield_store
```

## Store layout

```text
yield_store/
├── manifest.csv               # Index: table_id, species_latin, region, site_index, source, path
├── forest_elements_picea_abies_32.csv
├── et_nwfva_fagus_sylvatica_28.csv
├── carbon_et_picea_abies_34.csv
└── parametric_acer_campestre.csv
```

Each table CSV has columns:
`age, height, dbh, species_latin, region, management, site_index, source,
table_id`, optionally `volume`.

## Runtime resolution

```python
from pathlib import Path
from pylometree.yield_tables import resolve_yield_table

result = resolve_yield_table(
    species_common="Norway spruce",
    species_std="norway_spruce",
    yield_tables_dir=Path("data/input/yield_tables"),
    store_dir=Path("data/input/yield_tables/store"),
    preferred_site_index=32.0,
    preferred_region="DE",
)

if result is None:
    raise RuntimeError("No yield table available for Norway spruce")

print(result.ages)     # [20, 25, 30, ...]
print(result.heights)  # [7.1, 9.2, 11.5, ...] (m)
print(result.dbhs)     # [0.075, 0.095, 0.115, ...] (m)
```

Resolution priority:

1. Local hand-curated CSV in `yield_tables_dir` (highest — user override)
2. Ingested store (best match by region, then site index)

## Parametric fallback

For species without a published yield table, provide a JSON parametric model:

```json
{
    "species_latin": "Acer campestre",
    "height_model": {"type": "chapman_richards",
                     "A": 20.0, "k": 0.025, "p": 1.2, "y0": 0.5},
    "dbh_model":    {"type": "chapman_richards",
                     "A": 40.0, "k": 0.020, "p": 1.1, "y0": 0.0},
    "age_range": [10, 150],
    "age_step": 5,
    "site_index": 1.0
}
```

Run ingestion with the `parametric_models` provider pointing at the directory
containing these JSON files. The provider evaluates each model on the age
grid and writes a standard yield-table CSV into the store.

## Adding a provider

Providers subclass `YieldTableProvider` in
[`pylometree/yield_tables/providers.py`](../../src/pylometree/yield_tables/providers.py).
Minimum contract:

```python
class MyProvider(YieldTableProvider):
    name = "my_provider"

    def available(self) -> bool:
        """Return True if dependencies are importable."""
        ...

    def ingest(self, store: Store, **config) -> list[YieldTableRecord]:
        """Write normalized CSVs into `store`, return records produced."""
        ...
```

Then wire it into `cli.py`'s provider dispatch.

## Troubleshooting

- **`tabula-py` errors** — install Java (OpenJDK 11+) and ensure `java` is on
  PATH. tabula-py calls a JAR bundled with the package.
- **R-based providers fail to import** — run the provider's install command
  from inside your R environment: for ForestElementsR see
  [https://gitlab.com/forestelementsr/forestelementsr](https://gitlab.com/forestelementsr/forestelementsr),
  for et.nwfva see [https://github.com/fvafrCU/et.nwfva](https://github.com/fvafrCU/et.nwfva).
- **Store lookup returns None** — check `manifest.csv` to confirm the species
  name match. `species_std` in `resolve_yield_table` must match the manifest's
  standardized form (see [species-reference.md](../species-reference.md)).
