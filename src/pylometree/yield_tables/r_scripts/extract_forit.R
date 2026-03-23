#!/usr/bin/env Rscript
# Extract volume and phytomass equations from the ForIT R package (Italian NFI).
#
# Usage: Rscript extract_forit.R <output_csv>
#
# ForIT implements the INFC-2005 double-entry volume and phytomass equations
# for Italian forest tree species (Tabacchi et al. 2011).  We evaluate each
# species on a synthetic grid of DBH x height combinations to produce yield-
# table-like records that pylometree can ingest.
#
# Output CSV columns:
#   species_latin, age, height, dbh, volume, region, management, site_index, table_id

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 1) {
  stop("Usage: Rscript extract_forit.R <output_csv>")
}
output_csv <- args[1]

if (!requireNamespace("ForIT", quietly = TRUE)) {
  stop("ForIT package not installed. Install with:\n  install.packages('ForIT', repos='https://cloud.r-project.org')")
}

library(ForIT)

# ForIT species lookup table -- maps EPPO codes to Latin names.
# We read the built-in Coefficienti table to discover all available species.
data("Coefficienti", package = "ForIT", envir = environment())

# Get unique species codes from the coefficients table
species_codes <- unique(Coefficienti$EPPOcode)

cat(sprintf("Found %d species codes in ForIT\n", length(species_codes)))

# Map EPPO codes to Latin names (ForIT uses EPPO codes internally)
# The Coefficienti table has specie_lat column with Latin names
eppo_to_latin <- setNames(
  as.character(Coefficienti$specie_lat),
  as.character(Coefficienti$EPPOcode)
)
# Deduplicate
eppo_to_latin <- eppo_to_latin[!duplicated(names(eppo_to_latin))]

# Generate a synthetic grid: DBH 5-80 cm, height 5-40 m
# We use age=0 as a placeholder since ForIT provides volume not age-based tables
dbh_grid <- seq(5, 80, by = 5)
height_grid <- seq(5, 40, by = 5)

results <- data.frame(
  species_latin = character(),
  age = numeric(),
  height = numeric(),
  dbh = numeric(),
  volume = numeric(),
  region = character(),
  management = character(),
  site_index = numeric(),
  table_id = character(),
  stringsAsFactors = FALSE
)

cat("Processing ForIT species...\n")

for (eppo in names(eppo_to_latin)) {
  latin <- eppo_to_latin[[eppo]]
  cat(sprintf("  %s (%s): ", latin, eppo))

  row_count <- 0

  for (h in height_grid) {
    rows_for_h <- list()

    for (d in dbh_grid) {
      tryCatch({
        # INFCvpe returns volume and phytomass estimates
        est <- INFCvpe(eppo, d, h)

        if (is.null(est) || nrow(est) < 1) next

        # Extract stem volume (m3) -- INFCvpe returns dm3, convert to m3
        vol_dm3 <- est$Stima[est$Grandezza == "vol_ha"]
        if (length(vol_dm3) == 0) {
          # Try total volume
          vol_dm3 <- est$Stima[est$Grandezza == "vol"]
        }
        if (length(vol_dm3) == 0) next

        vol_m3 <- vol_dm3[1] / 1000.0  # dm3 -> m3

        if (is.na(vol_m3) || vol_m3 <= 0) next

        rows_for_h[[length(rows_for_h) + 1]] <- data.frame(
          species_latin = latin,
          age = 0,
          height = h,
          dbh = d,
          volume = vol_m3,
          region = "IT",
          management = "inventory",
          site_index = 0,
          table_id = paste0("forit_", eppo, "_h", h),
          stringsAsFactors = FALSE
        )
        row_count <- row_count + 1
      }, error = function(e) {
        # DBH/height combination out of range for this species - skip
      })
    }

    if (length(rows_for_h) > 0) {
      results <- rbind(results, do.call(rbind, rows_for_h))
    }
  }

  cat(sprintf("%d records\n", row_count))
}

cat(sprintf("\nExtracted %d rows for %d species\n",
            nrow(results),
            length(unique(results$species_latin))))

write.csv(results, output_csv, row.names = FALSE)
cat(sprintf("Wrote %s\n", output_csv))
