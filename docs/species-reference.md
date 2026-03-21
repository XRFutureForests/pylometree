# Species Reference

Comprehensive listing of species for which pylometree provides data (yield tables, site indices, H50 values) and/or allometric equations (biomass, height–diameter, height–age, crown, volume).

---

## Allometric Equations (Registry)

Published equations available via `pylometree.registry`. Predict with `registry.get(model_id).predict(...)` or `registry(model_id, ...)`.

### Biomass (AGB)

| Model ID | Species | Region | Covariates | Equation | Reference |
|---|---|---|---|---|---|
| `chave2014_pantropical` | Pantropical (generic) | pantropical | `dsob`, `hst`, `rho` | AGB = 0.0673·(ρ·D²·H)^0.976 | Chave et al. (2014) GCB |
| `laskar2020_musa_agb` | *Musa balbisiana* | tropical_asia | `dsob`, `hst` | AGB = exp(−4.54 + 0.874·ln(D²H)) × 1.06 | Laskar et al. (2020) |

### Crown → AGB

| Model ID | Species | Region | Covariates | Equation | Reference |
|---|---|---|---|---|---|
| `jucker2017_crown_agb` | Pantropical (generic) | pantropical | `hst`, `crown_area` | AGB = 0.016·H^0.940·CA^0.932 | Jucker et al. (2017) GCB |

### Height–Diameter (H–D)

| Model ID | Species | Region | Covariates | Equation | Reference |
|---|---|---|---|---|---|
| `chapman_richards_generic_hd` | Generic (fit to local data) | any | `dsob` | H = a·(1 − exp(−b·D))^c | Richards (1959); Chapman (1961) |
| `laskar2020_musa_hd_exponential` | *Musa balbisiana* | tropical_asia | `dsob` | H = a − b·exp(−c·D) | Laskar et al. (2020) |

### Height–Age (Growth Curves)

Pretzsch et al. (2025) Chapman-Richards height–age models for temperate European species.  
Equation form: **H = h_max · (1 − exp(−k·t))^c**

| Model ID | Species | h_max (m) | k | c |
|---|---|---|---|---|
| `pretzsch2025_picea_abies_height_age` | *Picea abies* | 48.0 | 0.028 | 1.30 |
| `pretzsch2025_pinus_sylvestris_height_age` | *Pinus sylvestris* | 38.0 | 0.030 | 1.10 |
| `pretzsch2025_fagus_sylvatica_height_age` | *Fagus sylvatica* | 42.0 | 0.024 | 1.20 |
| `pretzsch2025_quercus_petraea_height_age` | *Quercus petraea* | 36.0 | 0.020 | 1.15 |
| `pretzsch2025_quercus_robur_height_age` | *Quercus robur* | 34.0 | 0.019 | 1.10 |

> Reference: Pretzsch H et al. (2025) "Estimating tree age from height using the extended Chapman-Richards function." *Trees*. doi:10.1007/s00468-025-02692-0

---

## Yield Tables by Provider

Yield tables supply age-indexed series of dominant height, mean DBH, and (optionally) standing volume per hectare. Each table has a **site index** (yield class) and a derived **H50** (height at age 50, interpolated via PCHIP).

### Fields per table

| Field | Unit | Description |
|---|---|---|
| `ages` | years | Age series (5- or 10-year intervals) |
| `heights` | m | Dominant / top height |
| `dbhs` | cm | Mean diameter (`dsob` convention) |
| `volumes` | m³/ha | Standing volume (not all providers) |
| `site_index` | — | Yield class / Bonität |
| `h50` | m | Height at reference age 50 (computed) |
| `region` | code | Geographic origin (DE, UK, CA-NS, …) |
| `management` | text | Thinning regime |

### ForestElementsR (DE) — Classical German yield tables

Source: R package `ForestElementsR` (Wiedemann, Assmann, Schober tables).

| Species | Latin Name | Site indices | Management |
|---|---|---|---|
| Norway spruce | *Picea abies* | Multiple yield classes | normal / moderate thinning |
| European beech | *Fagus sylvatica* | Multiple yield classes | normal / moderate thinning |
| Scots pine | *Pinus sylvestris* | Multiple yield classes | normal / moderate thinning |
| European oak | *Quercus robur* | Multiple yield classes | normal / moderate thinning |
| Douglas fir | *Pseudotsuga menziesii* | Multiple yield classes | normal / moderate thinning |
| Silver fir | *Abies alba* | Multiple yield classes | normal |
| European larch | *Larix decidua* | Multiple yield classes | normal |
| Japanese larch | *Larix kaempferi* | Multiple yield classes | normal |
| Silver birch | *Betula pendula* | Multiple yield classes | normal |
| Black alder | *Alnus glutinosa* | Multiple yield classes | normal |
| Common ash | *Fraxinus excelsior* | Multiple yield classes | normal |
| Grey poplar | *Populus × canescens* | Multiple yield classes | normal |
| Red oak | *Quercus rubra* | Multiple yield classes | normal |

### et.nwfva (DE-NW) — Modern NW-FVA tables

Source: R package `et.nwfva` (2021). Ages 20–160 yr, 5-year intervals. Site index (Bonität) −2 to +4.

| Species | Latin Name | Site indices | Fields |
|---|---|---|---|
| European oak | *Quercus robur* | −2 … +4 | H100, Dg, volume |
| European beech | *Fagus sylvatica* | −2 … +4 | H100, Dg, volume |
| Norway spruce | *Picea abies* | −2 … +4 | H100, Dg, volume |
| Douglas fir | *Pseudotsuga menziesii* | −2 … +4 | H100, Dg, volume |
| Scots pine | *Pinus sylvestris* | −2 … +4 | H100, Dg, volume |

### CarbonEtXlsx (DE) — Schober-based carbon tables

Source: C_ET_pub.xlsx (OpenAgrar). Derived from classical Schober yield tables with carbon extensions.

| Species | Latin Name |
|---|---|
| Norway spruce | *Picea abies* |
| Scots pine | *Pinus sylvestris* |
| European beech | *Fagus sylvatica* |
| European oak | *Quercus robur* |
| Douglas fir | *Pseudotsuga menziesii* |

### ForestYieldPdf (UK) — Forestry Commission Booklet 48

Source: Edwards & Christie (1981) yield tables, PDF extraction.

| Species | Latin Name |
|---|---|
| Sitka spruce | *Picea sitchensis* |
| Norway spruce | *Picea abies* |
| Scots pine | *Pinus sylvestris* |
| Corsican pine | *Pinus nigra* subsp. *laricio* |
| Lodgepole pine | *Pinus contorta* |
| Douglas fir | *Pseudotsuga menziesii* |
| Japanese larch | *Larix kaempferi* |
| European larch | *Larix decidua* |
| Western hemlock | *Tsuga heterophylla* |
| Western redcedar | *Thuja plicata* |
| European oak | *Quercus robur* |
| European beech | *Fagus sylvatica* |
| Sycamore maple | *Acer pseudoplatanus* |
| Common ash | *Fraxinus excelsior* |
| Silver birch | *Betula pendula* |
| Poplar | *Populus* spp. |

### PryorPdf (UK) — FC Bulletin 75

Source: Pryor (1988) wild cherry yield tables.

| Species | Latin Name |
|---|---|
| Wild cherry | *Prunus avium* |

### NovaScotiaPdf (CA-NS) — Nova Scotia softwood tables

Source: Nova Scotia Department of Natural Resources.

| Species | Latin Name |
|---|---|
| Balsam fir | *Abies balsamea* |
| Red spruce | *Picea rubens* |
| Black spruce | *Picea mariana* |
| White spruce | *Picea glauca* |
| Eastern hemlock | *Tsuga canadensis* |
| Jack pine | *Pinus banksiana* |
| Red pine | *Pinus resinosa* |
| White pine | *Pinus strobus* |

---

## Cross-Reference: Species × Data Source

Species with coverage from **multiple** data sources. "Eq." = allometric equation in registry, "YT" = yield table.

| Species | Latin Name | Eq. (AGB) | Eq. (H–D) | Eq. (H–Age) | YT: DE (FE) | YT: DE (NW-FVA) | YT: DE (C_ET) | YT: UK | YT: CA |
|---|---|---|---|---|---|---|---|---|---|
| Norway spruce | *Picea abies* | — | — | Pretzsch | ✓ | ✓ | ✓ | ✓ | — |
| Scots pine | *Pinus sylvestris* | — | — | Pretzsch | ✓ | ✓ | ✓ | ✓ | — |
| European beech | *Fagus sylvatica* | — | — | Pretzsch | ✓ | ✓ | ✓ | ✓ | — |
| European oak | *Quercus robur* | — | — | Pretzsch | ✓ | ✓ | ✓ | ✓ | — |
| Sessile oak | *Quercus petraea* | — | — | Pretzsch | — | — | — | — | — |
| Douglas fir | *Pseudotsuga menziesii* | — | — | — | ✓ | ✓ | ✓ | ✓ | — |
| Silver fir | *Abies alba* | — | — | — | ✓ | — | — | — | — |
| European larch | *Larix decidua* | — | — | — | ✓ | — | — | ✓ | — |
| Japanese larch | *Larix kaempferi* | — | — | — | ✓ | — | — | ✓ | — |
| Silver birch | *Betula pendula* | — | — | — | ✓ | — | — | ✓ | — |
| Black alder | *Alnus glutinosa* | — | — | — | ✓ | — | — | — | — |
| Common ash | *Fraxinus excelsior* | — | — | — | ✓ | — | — | ✓ | — |
| Grey poplar | *Populus × canescens* | — | — | — | ✓ | — | — | — | — |
| Red oak | *Quercus rubra* | — | — | — | ✓ | — | — | — | — |
| Sitka spruce | *Picea sitchensis* | — | — | — | — | — | — | ✓ | — |
| Corsican pine | *Pinus nigra* | — | — | — | — | — | — | ✓ | — |
| Lodgepole pine | *Pinus contorta* | — | — | — | — | — | — | ✓ | — |
| Western hemlock | *Tsuga heterophylla* | — | — | — | — | — | — | ✓ | — |
| Western redcedar | *Thuja plicata* | — | — | — | — | — | — | ✓ | — |
| Sycamore maple | *Acer pseudoplatanus* | — | — | — | — | — | — | ✓ | — |
| Poplar | *Populus* spp. | — | — | — | — | — | — | ✓ | — |
| Wild cherry | *Prunus avium* | — | — | — | — | — | — | ✓ | — |
| Balsam fir | *Abies balsamea* | — | — | — | — | — | — | — | ✓ |
| Red spruce | *Picea rubens* | — | — | — | — | — | — | — | ✓ |
| Black spruce | *Picea mariana* | — | — | — | — | — | — | — | ✓ |
| White spruce | *Picea glauca* | — | — | — | — | — | — | — | ✓ |
| Eastern hemlock | *Tsuga canadensis* | — | — | — | — | — | — | — | ✓ |
| Jack pine | *Pinus banksiana* | — | — | — | — | — | — | — | ✓ |
| Red pine | *Pinus resinosa* | — | — | — | — | — | — | — | ✓ |
| White pine | *Pinus strobus* | — | — | — | — | — | — | — | ✓ |
| *Musa balbisiana* | *Musa balbisiana* | Laskar | Laskar | — | — | — | — | — | — |

> **Pantropical equations** (Chave 2014 AGB, Jucker 2017 crown→AGB) apply to all tropical species given `dsob`, `hst`, `rho` (or `crown_area`). They are not species-specific and are omitted from per-species rows.

---

## Species Mapping

The bundled species lookup at `pylometree/yield_tables/data/species.csv` maps 60 species between common name, standardized slug, Latin name, and German yield-table search key.

| Common Name | Standardized Name | Latin Name | Yield Search Key |
|---|---|---|---|
| European beech | `european_beech` | *Fagus sylvatica* | Buche |
| Norway spruce | `norway_spruce` | *Picea abies* | Fichte |
| Scots pine | `scots_pine` | *Pinus sylvestris* | Kiefer |
| Silver fir | `silver_fir` | *Abies alba* | Tanne |
| Grand fir | `grand_fir` | *Abies grandis* | |
| European oak | `european_oak` | *Quercus robur* | Eiche |
| Red oak | `red_oak` | *Quercus rubra* | Roteiche |
| White oak | `white_oak` | *Quercus alba* | |
| Sweet chestnut | `sweet_chestnut` | *Castanea sativa* | Edelkastanie |
| Common ash | `common_ash` | *Fraxinus excelsior* | Esche |
| Narrow-leaved ash | `narrow_leaved_ash` | *Fraxinus angustifolia* | |
| One-leaved ash | `one_leaved_ash` | *Fraxinus excelsior* 'Diversifolia' | |
| Downy birch | `downy_birch` | *Betula pubescens* | Birke |
| Silver birch | `silver_birch` | *Betula pendula* | Birke |
| Paper birch | `paper_birch` | *Betula papyrifera* | |
| Black alder | `black_alder` | *Alnus glutinosa* | Erle |
| Hornbeam | `hornbeam` | *Carpinus betulus* | Hainbuche |
| Hazel | `hazel` | *Corylus avellana* | |
| Field maple | `field_maple` | *Acer campestre* | |
| Sycamore maple | `sycamore_maple` | *Acer pseudoplatanus* | |
| Japanese maple | `japanese_maple` | *Acer palmatum* | |
| Horse chestnut | `horse_chestnut` | *Aesculus hippocastanum* | |
| Small-leaved linden | `small_leaved_linden` | *Tilia cordata* | Winterlinde |
| Wild cherry | `wild_cherry` | *Prunus avium* | |
| Japanese cherry | `japanese_cherry` | *Prunus serrulata* | |
| Rowan / Mountain ash | `rowan_mountain_ash` | *Sorbus aucuparia* | |
| Wild apple | `wild_apple` | *Malus sylvestris* | |
| Willow | `willow` | *Salix alba* | Weide |
| Weeping willow | `weeping_willow` | *Salix babylonica* | |
| Grey poplar | `grey_poplar` | *Populus × canescens* | Pappel |
| Italian poplar | `italian_poplar` | *Populus × canadensis* | Pappel |
| Aspen | `aspen` | *Populus tremula* | |
| Elm | `elm` | *Ulmus minor* | |
| Yew | `yew` | *Taxus baccata* | |
| Austrian pine | `austrian_pine` | *Pinus nigra* | Schwarzkiefer |
| Lodgepole pine | `lodgepole_pine` | *Pinus contorta* | |
| Longleaf pine | `longleaf_pine` | *Pinus palustris* | |
| Monterey pine | `monterey_pine` | *Pinus radiata* | |
| Ponderosa pine | `ponderosa_pine` | *Pinus ponderosa* | |
| Stone pine | `stone_pine` | *Pinus pinea* | |
| Western hemlock | `western_hemlock` | *Tsuga heterophylla* | |
| Western redcedar | `western_redcedar` | *Thuja plicata* | |
| Swamp cypress | `swamp_cypress` | *Taxodium distichum* | |
| Hackberry | `hackberry` | *Celtis occidentalis* | |
| Honey locust | `honey_locust` | *Gleditsia triacanthos* | |
| Robinia | `robinia` | *Robinia pseudoacacia* | Robinie |
| Umbrella acacia | `umbrella_acacia` | *Robinia umbraculifera* | |
| Ginkgo biloba | `ginkgo_biloba` | *Ginkgo biloba* | |
| Walnut | `walnut` | *Juglans regia* | |
| Wingnut | `wingnut` | *Pterocarya fraxinifolia* | |
| Avocado | `avocado` | *Persea americana* | |
| Magnolia | `magnolia` | *Magnolia × soulangeana* | |
| Blue gum | `blue_gum` | *Eucalyptus globulus* | |
| Manna gum | `manna_gum` | *Eucalyptus viminalis* | |
| Black tupelo | `black_tupelo` | *Nyssa sylvatica* | |
| London plane tree | `london_plane_tree` | *Platanus × acerifolia* | |
| Douglas fir | `douglas_fir` | *Pseudotsuga menziesii* | Douglasie |
| European larch | `european_larch` | *Larix decidua* | Laerche |
| Japanese larch | `japanese_larch` | *Larix kaempferi* | |
| Sitka spruce | `sitka_spruce` | *Picea sitchensis* | |
