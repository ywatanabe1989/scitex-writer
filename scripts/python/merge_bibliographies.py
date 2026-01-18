#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-09 21:30:00 (ywatanabe)"
# File: ./scripts/python/merge_bibliographies.py
"""
Merge multiple BibTeX files with smart deduplication.

Deduplication strategy:
1. By DOI (if available)
2. By normalized title + year
3. Merges metadata from duplicates
"""

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import List, Optional

try:
    import bibtexparser
    from bibtexparser.bibdatabase import BibDatabase
    from bibtexparser.bwriter import BibTexWriter
except ImportError:
    print("ERROR: bibtexparser not installed")
    print("Install with: pip install bibtexparser")
    exit(1)


def normalize_title(title: str) -> str:
    """Normalize title for comparison (lowercase, no punctuation)."""
    if not title:
        return ""
    # Remove LaTeX commands
    title = re.sub(r"\\[a-zA-Z]+\{([^}]*)\}", r"\1", title)
    # Remove special characters and extra whitespace
    title = re.sub(r"[^\w\s]", "", title.lower())
    title = re.sub(r"\s+", " ", title).strip()
    return title


def get_doi(entry: dict) -> str:
    """Extract DOI from entry."""
    doi = entry.get("doi", "").strip()
    if doi:
        # Normalize DOI (remove URL prefix if present)
        doi = re.sub(r"https?://doi.org/", "", doi, flags=re.IGNORECASE)
        doi = re.sub(r"https?://dx.doi.org/", "", doi, flags=re.IGNORECASE)
    return doi


def merge_entries(existing: dict, duplicate: dict) -> dict:
    """Merge metadata from duplicate entries, preferring more complete info."""
    merged = existing.copy()

    # Prefer entries with more fields
    for key, value in duplicate.items():
        if key not in merged or not merged[key]:
            merged[key] = value
        elif value and len(str(value)) > len(str(merged[key])):
            # Prefer longer/more detailed field
            merged[key] = value

    return merged


def deduplicate_entries(entries: List[dict]) -> tuple[List[dict], dict]:
    """
    Deduplicate BibTeX entries by DOI and title.

    Returns:
        (unique_entries, stats)
    """
    unique = []
    doi_index = {}  # DOI -> index in unique list
    title_index = {}  # (normalized_title, year) -> index in unique list
    duplicates_found = 0
    duplicates_merged = 0

    for entry in entries:
        doi = get_doi(entry)
        title = entry.get("title", "")
        year = entry.get("year", "")
        title_norm = normalize_title(title)

        is_duplicate = False
        merge_with_idx = None

        # Check by DOI first (most reliable)
        if doi and doi in doi_index:
            is_duplicate = True
            merge_with_idx = doi_index[doi]
            duplicates_found += 1

        # Check by title + year
        elif title_norm and year:
            key = (title_norm, year)
            if key in title_index:
                is_duplicate = True
                merge_with_idx = title_index[key]
                duplicates_found += 1

        if is_duplicate and merge_with_idx is not None:
            # Merge metadata with existing entry
            merge_with = unique[merge_with_idx]
            merged = merge_entries(merge_with, entry)

            # Update in unique list
            unique[merge_with_idx] = merged

            # Indices remain the same (still pointing to same position)
            # No need to update doi_index or title_index

            duplicates_merged += 1
        else:
            # New unique entry
            new_idx = len(unique)
            unique.append(entry)

            # Index it by position
            if doi:
                doi_index[doi] = new_idx
            if title_norm and year:
                title_index[(title_norm, year)] = new_idx

    stats = {
        "total_input": len(entries),
        "unique_output": len(unique),
        "duplicates_found": duplicates_found,
        "duplicates_merged": duplicates_merged,
    }

    return unique, stats


def calculate_files_hash(bib_files: List[Path]) -> str:
    """
    Calculate MD5 hash of all input .bib files.

    Args:
        bib_files: List of .bib file paths

    Returns:
        Hex digest of combined file hashes
    """
    hasher = hashlib.md5()

    # Sort files for consistent hashing
    for bib_file in sorted(bib_files, key=lambda x: x.name):
        # Include filename in hash
        hasher.update(bib_file.name.encode("utf-8"))

        # Include file content hash
        with open(bib_file, "rb") as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
            hasher.update(file_hash.encode("utf-8"))

    return hasher.hexdigest()


def load_cache(cache_file: Path) -> Optional[dict]:
    """Load cache from file."""
    if not cache_file.exists():
        return None

    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def save_cache(cache_file: Path, data: dict) -> None:
    """Save cache to file."""
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        print(f"WARNING: Could not save cache: {e}")


def is_cache_valid(cache_file: Path, bib_files: List[Path], output_file: Path) -> bool:
    """
    Check if cached merge is still valid.

    Args:
        cache_file: Path to cache file
        bib_files: List of input .bib files
        output_file: Path to output file

    Returns:
        True if cache is valid and merge can be skipped
    """
    # No cache file
    if not cache_file.exists():
        return False

    # No output file
    if not output_file.exists():
        return False

    # Load cache
    cache = load_cache(cache_file)
    if not cache:
        return False

    # Calculate current hash
    current_hash = calculate_files_hash(bib_files)

    # Compare with cached hash
    return cache.get("input_hash") == current_hash


def merge_bibtex_files(
    bib_dir: Path,
    output_file: str = "bibliography.bib",
    verbose: bool = True,
    force: bool = False,
) -> bool:
    """
    Merge all .bib files in directory with smart deduplication.

    Args:
        bib_dir: Directory containing .bib files
        output_file: Output filename (saved in bib_dir)
        verbose: Print progress messages
        force: Force merge even if cache is valid

    Returns:
        True if successful
    """
    bib_dir = Path(bib_dir)
    output_path = bib_dir / output_file
    cache_file = bib_dir / ".bibliography_cache.json"

    # Find all .bib files except the output file
    bib_files = [f for f in bib_dir.glob("*.bib") if f.name != output_file]

    if not bib_files:
        if verbose:
            print(f"No .bib files found in {bib_dir}")
        return False

    # Check cache (skip if force=True)
    if not force and is_cache_valid(cache_file, bib_files, output_path):
        if verbose:
            print("✓ Bibliography cache valid (no changes detected)")
            print("  Use --force to rebuild")
        return True

    if verbose:
        print(f"Merging {len(bib_files)} bibliography files...")
        for f in sorted(bib_files):
            print(f"  - {f.name}")

    # Load and parse all files
    all_entries = []
    for bib_file in bib_files:
        try:
            with open(bib_file, "r", encoding="utf-8") as f:
                parser = bibtexparser.bparser.BibTexParser(
                    common_strings=True, ignore_nonstandard_types=False
                )
                bib_db = bibtexparser.load(f, parser=parser)
                all_entries.extend(bib_db.entries)
                if verbose:
                    print(
                        f"  Loaded: {len(bib_db.entries)} entries from {bib_file.name}"
                    )
        except Exception as e:
            print(f"ERROR: Failed to parse {bib_file}: {e}")
            continue

    # Deduplicate
    unique_entries, stats = deduplicate_entries(all_entries)

    # Create output database
    output_db = BibDatabase()
    output_db.entries = unique_entries

    # Write output
    writer = BibTexWriter()
    writer.indent = "  "  # 2-space indentation
    writer.order_entries_by = "ID"  # Sort by citation key

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(writer.write(output_db))

    # Save cache
    input_hash = calculate_files_hash(bib_files)
    cache_data = {
        "input_hash": input_hash,
        "input_files": [f.name for f in sorted(bib_files, key=lambda x: x.name)],
        "output_file": output_file,
        "stats": stats,
    }
    save_cache(cache_file, cache_data)

    if verbose:
        print(f"\n✓ Merged bibliography saved: {output_path}")
        print(f"  Input entries: {stats['total_input']}")
        print(f"  Unique entries: {stats['unique_output']}")
        print(f"  Duplicates removed: {stats['duplicates_merged']}")

    return True


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Merge BibTeX files with smart deduplication"
    )
    parser.add_argument(
        "bib_dir",
        nargs="?",
        default="00_shared/bib_files",
        help="Directory containing .bib files (default: 00_shared/bib_files)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="bibliography.bib",
        help="Output filename (default: bibliography.bib)",
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Quiet mode (no output)"
    )
    parser.add_argument(
        "-f", "--force", action="store_true", help="Force merge (ignore cache)"
    )

    args = parser.parse_args()

    success = merge_bibtex_files(
        bib_dir=Path(args.bib_dir),
        output_file=args.output,
        verbose=not args.quiet,
        force=args.force,
    )

    exit(0 if success else 1)


if __name__ == "__main__":
    main()


# EOF
