#!/usr/bin/env python3
"""Ingest yield tables from external providers into the local store.

Runs each available provider, normalizes output, and writes CSVs to a
store directory.

Usage:
    pylometree-ingest --list-providers
    pylometree-ingest --store-dir ./yield_store
    pylometree-ingest --providers forest_elements et_nwfva
    pylometree-ingest --clean
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional

from pylometree.yield_tables.providers import (
    YieldProvider,
    get_all_providers,
    get_available_providers,
    get_provider_by_name,
)
from pylometree.yield_tables.species import SpeciesMapping, load_species_mapping
from pylometree.yield_tables.store import StoreManifest

logger = logging.getLogger(__name__)


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(
        prog="pylometree-ingest",
        description="Ingest yield tables from external providers into the local store.",
    )
    parser.add_argument(
        "--store-dir",
        type=Path,
        required=False,
        default=Path("yield_store"),
        help="Directory to write store CSVs and manifest. Default: ./yield_store",
    )
    parser.add_argument(
        "--species-csv",
        type=Path,
        required=False,
        default=None,
        help="Custom species mapping CSV. Default: bundled species.csv.",
    )
    parser.add_argument(
        "--list-providers",
        action="store_true",
        help="List all providers and their status, then exit.",
    )
    parser.add_argument(
        "--providers",
        nargs="+",
        help="Run only these providers (by name). Default: all available.",
    )
    parser.add_argument(
        "--config",
        nargs="*",
        metavar="KEY=VALUE",
        help="Provider config overrides (e.g., xlsx_path=/path/to/file.xlsx).",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clear existing store before ingesting.",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose logging.",
    )

    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)-7s %(message)s",
    )

    if args.list_providers:
        _list_providers()
        return

    species_mapping = load_species_mapping(args.species_csv)

    provider_config = {}
    if args.config:
        for item in args.config:
            if "=" in item:
                key, value = item.split("=", 1)
                provider_config[key.strip()] = value.strip()

    providers = _select_providers(args.providers)
    if not providers:
        logger.error("No providers available. Install dependencies or check --list-providers.")
        sys.exit(1)

    store_dir: Path = args.store_dir.resolve()

    if args.clean and store_dir.exists():
        import shutil
        shutil.rmtree(store_dir)
        logger.info("Cleared store: %s", store_dir)

    store_dir.mkdir(parents=True, exist_ok=True)
    manifest = StoreManifest.load(store_dir / "manifest.csv")

    total_tables = 0
    total_errors = 0

    for provider in providers:
        logger.info("")
        logger.info("Running provider: %s", provider.name)
        logger.info("  %s", provider.description)
        count = 0
        errors = 0
        try:
            for record in provider.iter_tables(species_mapping, provider_config):
                issues = record.validate()
                if issues:
                    logger.warning(
                        "  Skipping %s (si=%.0f): %s",
                        record.standardized_name,
                        record.site_index,
                        "; ".join(issues),
                    )
                    errors += 1
                    continue

                filename = record.filename()
                csv_path = store_dir / filename
                record.to_csv(csv_path)
                manifest.add(record, filename)
                count += 1
                logger.debug("  Wrote %s (%d rows)", filename, len(record.ages))
        except Exception as e:
            logger.error("  Provider %s failed: %s", provider.name, e)
            errors += 1

        logger.info("  %s: %d tables ingested, %d errors", provider.name, count, errors)
        total_tables += count
        total_errors += errors

    manifest.save(store_dir / "manifest.csv")

    logger.info("")
    logger.info("Ingestion complete: %d tables in %s", total_tables, store_dir)
    if total_errors:
        logger.warning("  %d errors encountered", total_errors)

    _print_summary(manifest)


def _list_providers() -> None:
    print("Yield table providers:")
    print()
    for p in get_all_providers():
        marker = "[OK]" if p.available() else "[--]"
        print(f"  {marker} {p.name:25s} {p.status_message()}")
        print(f"      {p.description}")
    print()
    available = get_available_providers()
    print(f"  {len(available)} / {len(get_all_providers())} providers available")


def _select_providers(names: Optional[List[str]]) -> List[YieldProvider]:
    if names:
        providers = []
        for name in names:
            p = get_provider_by_name(name)
            if p is None:
                logger.error("Unknown provider: %s", name)
                continue
            if not p.available():
                logger.warning("Provider %s not available: %s", name, p.status_message())
                continue
            providers.append(p)
        return providers
    return get_available_providers()


def _print_summary(manifest: StoreManifest) -> None:
    if not manifest.entries:
        return
    species_set = {e["standardized_name"] for e in manifest.entries}
    sources = {e.get("source", "?") for e in manifest.entries}
    print()
    print(f"  Store contains {len(manifest.entries)} tables for {len(species_set)} species")
    print(f"  Sources: {', '.join(sorted(sources))}")
    print(f"  Species: {', '.join(sorted(species_set))}")


if __name__ == "__main__":
    main()
