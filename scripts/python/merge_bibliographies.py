#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ROLE: engine-vendored — DO NOT edit here. `scitex-writer update-project`
# overwrites this file on every re-vendor; fix it upstream in the
# scitex-writer package instead (local edits are lost, and update-project
# may set it read-only in the consumer workspace after vendoring).
# Timestamp: "2025-11-09 21:30:00 (ywatanabe)"
# File: ./scripts/python/merge_bibliographies.py
"""
Merge multiple BibTeX files with smart deduplication.

Deduplication strategy:
1. By cite key (a repeated key is what makes bibtex fail -- see below)
2. By DOI (if available)
3. By normalized title + year
4. Merges metadata from duplicates

STUB-VS-REAL PRECEDENCE
-----------------------
scitex-scholar auto-generates STUB entries for citations whose metadata it has
not resolved yet, and writes them to a sidecar (`_stubs_pending_scholar.bib`)
while the real entry may already exist in `bibliography.bib`. The same cite key
then lives in two files, bibtex reports `Repeated entry ... I'm skipping
whatever remains of this entry`, DROPS the reference, and exits non-zero.

So: **a real entry always beats a stub.** When a duplicate pair is one real +
one stub, the REAL entry is the base and the stub may only fill fields the real
entry does not have -- it can never overwrite a real field (the old
"longer value wins" rule would have let the stub's 39-character
`journal = {Pending scitex-scholar metadata lookup}` overwrite a real
`journal = {Nature}`), and its stub STAMPS are never copied onto the real entry
(that would make `check_citations.py` mis-flag a resolved reference as a stub).
Two stubs merge normally and stay stamped, so the citation gate still catches
them. What a stub *is* is defined by scholar's stamps -- imported from
`check_citations.py` so there is ONE definition, not two.
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
# The SSoT for "what is a scholar stub". Do not re-declare these markers here:
# check_citations.py gates the compile on them, and a second copy would drift.
from check_citations import STUB_JOURNAL_MARKERS, STUB_NOTE_MARKERS  # noqa: E402

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


def is_stub(entry: dict) -> bool:
    """True when the entry carries one of scholar's auto-generated stub stamps."""
    note = str(entry.get("note", "")).lower()
    journal = str(entry.get("journal", "")).lower()
    return any(marker in note for marker in STUB_NOTE_MARKERS) or any(
        marker in journal for marker in STUB_JOURNAL_MARKERS
    )


def strip_stub_stamps(entry: dict) -> dict:
    """Drop the fields whose VALUE is a stub stamp (they are placeholders).

    Used when gap-filling a real entry from a stub: the stub may contribute a
    field the real entry lacks, but never its own "this is unresolved" stamps --
    copying those onto a resolved reference would make check_citations.py report
    the real entry as a stub.
    """
    cleaned = {}
    for key, value in entry.items():
        lowered = str(value).lower()
        if key == "note" and any(m in lowered for m in STUB_NOTE_MARKERS):
            continue
        if key == "journal" and any(m in lowered for m in STUB_JOURNAL_MARKERS):
            continue
        cleaned[key] = value
    return cleaned


def merge_entries(existing: dict, duplicate: dict, gap_fill_only: bool = False) -> dict:
    """Merge metadata from duplicate entries, preferring more complete info.

    ``gap_fill_only`` restricts ``duplicate`` to fields ``existing`` does not
    have. It is what makes a real entry immune to a stub's placeholder values:
    without it the "longer value wins" rule below lets a stub's long
    "Pending ..." journal overwrite a real journal name.
    """
    merged = existing.copy()

    # Prefer entries with more fields
    for key, value in duplicate.items():
        if key not in merged or not merged[key]:
            merged[key] = value
        elif gap_fill_only:
            continue
        elif value and len(str(value)) > len(str(merged[key])):
            # Prefer longer/more detailed field
            merged[key] = value

    return merged


def merge_duplicate_pair(existing: dict, duplicate: dict) -> dict:
    """Merge two entries that share an identity, applying real-beats-stub.

    Exactly one stub -> the REAL entry is the base and the stub only gap-fills
    (never overwrites, never donates its stamps). Otherwise (real+real or
    stub+stub) the normal completeness merge applies, so a stub+stub merge stays
    stamped and the citation gate still sees it.
    """
    existing_is_stub = is_stub(existing)
    duplicate_is_stub = is_stub(duplicate)

    if existing_is_stub and not duplicate_is_stub:
        return merge_entries(duplicate, strip_stub_stamps(existing), gap_fill_only=True)
    if duplicate_is_stub and not existing_is_stub:
        return merge_entries(existing, strip_stub_stamps(duplicate), gap_fill_only=True)
    return merge_entries(existing, duplicate)


def deduplicate_entries(entries: List[dict]) -> tuple[List[dict], dict]:
    """
    Deduplicate BibTeX entries by cite key, DOI, and title.

    Returns:
        (unique_entries, stats)
    """
    unique = []
    id_index = {}  # cite key (entry ID) -> index in unique list
    doi_index = {}  # DOI -> index in unique list
    title_index = {}  # (normalized_title, year) -> index in unique list
    duplicates_found = 0
    duplicates_merged = 0

    for entry in entries:
        doi = get_doi(entry)
        title = entry.get("title", "")
        year = entry.get("year", "")
        title_norm = normalize_title(title)
        cite_key = str(entry.get("ID", "")).strip()

        is_duplicate = False
        merge_with_idx = None

        # Check by cite key (entry ID) FIRST. A repeated cite key is exactly
        # what makes bibtex emit "repeated entry" / "I'm skipping whatever
        # remains of this entry" and drop a whole reference -- so it must never
        # reach the merged output, regardless of DOI/title. Common with
        # auto-generated stub entries duplicated across input .bib files.
        if cite_key and cite_key in id_index:
            is_duplicate = True
            merge_with_idx = id_index[cite_key]
            duplicates_found += 1

        # Check by DOI (most reliable content match)
        elif doi and doi in doi_index:
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
            # Merge metadata with existing entry (real beats stub)
            merge_with = unique[merge_with_idx]
            merged = merge_duplicate_pair(merge_with, entry)

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
            if cite_key:
                id_index[cite_key] = new_idx
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


def input_sort_key(bib_file: Path, output_name: str) -> tuple:
    """Deterministic merge order: output file, then real sources, then stubs.

    Order decides which entry of a duplicate pair is seen FIRST and therefore
    becomes the base. Filesystem glob order is arbitrary, so pin it: the
    author-owned bibliography first, stub sidecars (`_stubs_pending_scholar.bib`)
    last. This is belt-and-braces -- merge_duplicate_pair enforces real-beats-stub
    regardless of order -- but it also makes the OUTPUT byte-stable across runs.
    """
    if bib_file.name == output_name:
        rank = 0
    elif "stub" in bib_file.name.lower():
        rank = 2
    else:
        rank = 1
    return (rank, bib_file.name)


def merge_bibtex_files(
    bib_dir: Path,
    output_file: str = "bibliography.bib",
    verbose: bool = True,
    force: bool = False,
    include_output: bool = False,
) -> bool:
    """
    Merge all .bib files in directory with smart deduplication.

    Args:
        bib_dir: Directory containing .bib files
        output_file: Output filename (saved in bib_dir)
        verbose: Print progress messages
        force: Force merge even if cache is valid
        include_output: Read the output file as an INPUT too, so the merge is
            de-duplicating and additive instead of regenerate-from-scratch.
            The compile path sets this because its output --
            `00_shared/bib_files/bibliography.bib` -- is the consumer-owned file
            the manuscript actually cites (contents/bibliography.bib symlinks to
            it) and is stamped "consumer-owned - safe to edit" in its own header.
            With it OFF, entries that live only in bibliography.bib are silently
            destroyed by a merge with any other .bib, and a duplicate cite key
            INSIDE bibliography.bib is never collapsed at all. Default stays OFF
            so a merge into some other, genuinely derived, output file keeps
            regenerate-from-scratch semantics.

    Returns:
        True if successful
    """
    bib_dir = Path(bib_dir)
    output_file_path = Path(output_file)
    if output_file_path.is_absolute() or str(output_file_path.parent) != ".":
        output_path = output_file_path
    else:
        output_path = bib_dir / output_file
    cache_file = bib_dir / ".bibliography_cache.json"

    # Find all .bib files; the output is an input only when asked (see above).
    bib_files = [
        f for f in bib_dir.glob("*.bib") if include_output or f.name != output_path.name
    ]
    bib_files.sort(key=lambda f: input_sort_key(f, output_path.name))

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
        "output_file": str(output_path),
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
    parser.add_argument(
        "--include-output",
        action="store_true",
        help=(
            "Merge the output file as an input too (de-duplicating + additive, "
            "never destructive). Use when the output is the consumer-owned "
            "bibliography.bib the manuscript cites."
        ),
    )

    args = parser.parse_args()

    success = merge_bibtex_files(
        bib_dir=Path(args.bib_dir),
        output_file=args.output,
        verbose=not args.quiet,
        force=args.force,
        include_output=args.include_output,
    )

    exit(0 if success else 1)


if __name__ == "__main__":
    main()


# EOF
