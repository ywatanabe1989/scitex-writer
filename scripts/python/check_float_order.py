#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: scripts/python/check_float_order.py
# Purpose: Validate and auto-renumber figure/table reference ordering in LaTeX manuscripts
# Usage:
#   python check_float_order.py [project_dir] [--fix] [--doc-type manuscript|supplementary]
#
# Checks that figures and tables are referenced in numerical order in the text.
# With --fix, renumbers files and updates all \ref{} and \label{} to match appearance order.

import argparse
import os
import re
import shutil
import sys
from collections import OrderedDict
from pathlib import Path

# ANSI colors
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
DIM = "\033[0;90m"
BOLD = "\033[1m"
NC = "\033[0m"


def find_references(content_dir, float_type):
    """Find all \\ref{fig:*} or \\ref{tab:*} in text files, in order of appearance.

    Parameters
    ----------
    content_dir : Path
        Directory containing .tex content files.
    float_type : str
        'fig' or 'tab'.

    Returns
    -------
    list of tuple
        (label_key, file, line_number) in order of first appearance.
    """
    # Read order: follow typical IMRAD structure
    section_order = [
        "abstract",
        "introduction",
        "results",
        "methods",
        "star_methods",
        "discussion",
        "additional_info",
        "data_availability",
        "bigger_picture",
        "highlights",
        "graphical_abstract",
    ]

    tex_files = []
    for name in section_order:
        p = content_dir / f"{name}.tex"
        if p.exists():
            tex_files.append(p)

    # Add any remaining .tex files not in the order list
    for p in sorted(content_dir.glob("*.tex")):
        if p not in tex_files:
            tex_files.append(p)

    pattern = re.compile(r"\\ref\{" + float_type + r":([^}]+)\}")
    seen = OrderedDict()
    refs = []

    for tex_file in tex_files:
        text = tex_file.read_text(encoding="utf-8")
        for line_no, line in enumerate(text.splitlines(), 1):
            for m in pattern.finditer(line):
                key = m.group(1)
                if key not in seen:
                    seen[key] = (tex_file.name, line_no)
                    refs.append((key, tex_file.name, line_no))

    return refs


def find_labels(content_dir, float_type):
    """Find all \\label{fig:*} or \\label{tab:*} definitions.

    Searches both caption files in figures/tables subdirs and inline in content .tex files.

    Returns
    -------
    dict
        label_key -> {'file': Path, 'line': int, 'source': 'caption_file'|'inline'}
    """
    labels = {}
    prefix = float_type

    # Search caption files
    if float_type == "fig":
        media_dir = content_dir / "figures" / "caption_and_media"
    else:
        media_dir = content_dir / "tables" / "caption_and_media"

    if media_dir.exists():
        for tex_file in media_dir.glob("[0-9]*.tex"):
            text = tex_file.read_text(encoding="utf-8")
            for line_no, line in enumerate(text.splitlines(), 1):
                m = re.search(r"\\label\{" + prefix + r":([^}]+)\}", line)
                if m:
                    labels[m.group(1)] = {
                        "file": tex_file,
                        "line": line_no,
                        "source": "caption_file",
                    }

    # Search inline in content .tex files
    for tex_file in content_dir.glob("*.tex"):
        text = tex_file.read_text(encoding="utf-8")
        for line_no, line in enumerate(text.splitlines(), 1):
            m = re.search(r"\\label\{" + prefix + r":([^}]+)\}", line)
            if m:
                key = m.group(1)
                if key not in labels:
                    labels[key] = {
                        "file": tex_file,
                        "line": line_no,
                        "source": "inline",
                    }

    return labels


def extract_number_and_name(key):
    """Extract numeric prefix and descriptive name from a key like '04_modules'.

    Returns (4, 'modules') or (None, key) if no numeric prefix.
    """
    m = re.match(r"^(\d+)_(.+)$", key)
    if m:
        return int(m.group(1)), m.group(2)
    m = re.match(r"^(\d+)$", key)
    if m:
        return int(m.group(1)), ""
    return None, key


def check_order(content_dir, float_type, label):
    """Check if references appear in numerical order.

    Returns
    -------
    tuple
        (is_ok, refs, desired_mapping)
        refs: list of (key, file, line)
        desired_mapping: dict of old_key -> new_key if reordering needed
    """
    refs = find_references(content_dir, float_type)
    labels = find_labels(content_dir, float_type)

    if not refs:
        print(f"  {GREEN}[PASS]{NC} {label} references - none found")
        return True, refs, {}

    # Check if numbered keys appear in order
    numbered_refs = []
    for key, fname, line in refs:
        num, name = extract_number_and_name(key)
        if num is not None:
            numbered_refs.append((num, name, key, fname, line))

    if not numbered_refs:
        print(f"  {GREEN}[PASS]{NC} {label} references - no numbered references")
        return True, refs, {}

    # Check sequential ordering
    numbers = [n for n, _, _, _, _ in numbered_refs]
    is_sequential = all(numbers[i] < numbers[i + 1] for i in range(len(numbers) - 1))

    if is_sequential:
        # Check if numbering starts at 01 and is contiguous
        expected = list(range(1, len(numbered_refs) + 1))
        actual = numbers
        if actual == expected:
            print(
                f"  {GREEN}[PASS]{NC} {label} reference order (1..{len(numbered_refs)})"
            )
        else:
            print(
                f"  {YELLOW}[WARN]{NC} {label} references sequential but not contiguous: {numbers}"
            )
        return True, refs, {}

    # Out of order - build mapping
    print(f"  {RED}[FAIL]{NC} {label} reference order")
    desired_mapping = {}
    for new_num_0, (old_num, name, old_key, fname, line) in enumerate(numbered_refs):
        new_num = new_num_0 + 1
        new_key = f"{new_num:02d}_{name}" if name else f"{new_num:02d}"
        if old_key != new_key:
            desired_mapping[old_key] = new_key
        print(
            f"    {DIM}{fname}:{line}: "
            f"\\ref{{{float_type}:{old_key}}} -> should be {new_num:02d}{NC}"
        )

    # Report orphaned labels (defined but never referenced)
    ref_keys = {key for key, _, _ in refs}
    for label_key, info in labels.items():
        if label_key not in ref_keys:
            print(
                f"    {YELLOW}[WARN]{NC} \\label{{{float_type}:{label_key}}} "
                f"defined in {info['file'].name}:{info['line']} but never referenced"
            )

    return False, refs, desired_mapping


def apply_fix(content_dir, float_type, mapping, dry_run=False):
    """Rename files and update all \\ref{} and \\label{} in place.

    Parameters
    ----------
    content_dir : Path
    float_type : str
        'fig' or 'tab'
    mapping : dict
        old_key -> new_key
    dry_run : bool
        If True, only print what would be done.
    """
    if not mapping:
        return

    prefix = float_type

    # 1. Collect all .tex files that may contain references
    all_tex_files = list(content_dir.glob("*.tex"))
    if float_type == "fig":
        media_dir = content_dir / "figures" / "caption_and_media"
    else:
        media_dir = content_dir / "tables" / "caption_and_media"

    if media_dir.exists():
        all_tex_files.extend(media_dir.glob("*.tex"))

    # Also check the parent manuscript .tex files
    doc_dir = content_dir.parent
    for tex in doc_dir.glob("*.tex"):
        all_tex_files.append(tex)

    all_tex_files = list(set(all_tex_files))

    # 2. Text replacements in all .tex files
    # Use intermediate keys to avoid collision (old_key -> __TEMP_N__ -> new_key)
    temp_keys = {old: f"__REORDER_TEMP_{i}__" for i, old in enumerate(mapping)}

    for tex_file in all_tex_files:
        text = tex_file.read_text(encoding="utf-8")
        original = text

        # Pass 1: old -> temp
        for old_key, temp_key in temp_keys.items():
            text = text.replace(f"{prefix}:{old_key}", f"{prefix}:{temp_key}")

        # Pass 2: temp -> new
        for old_key, new_key in mapping.items():
            temp_key = temp_keys[old_key]
            text = text.replace(f"{prefix}:{temp_key}", f"{prefix}:{new_key}")

        if text != original:
            action = "Would update" if dry_run else "Updated"
            print(f"    {action} references in {tex_file.name}")
            if not dry_run:
                tex_file.write_text(text, encoding="utf-8")

    # 3. Rename media files (caption .tex, images, CSV, etc.)
    if not media_dir or not media_dir.exists():
        return

    # Build file rename map using temp names to avoid collision
    renames = []  # (old_path, temp_path, new_path)

    for old_key, new_key in mapping.items():
        old_prefix_str = old_key  # e.g., "04_modules"
        new_prefix_str = new_key  # e.g., "01_modules"

        for f in media_dir.iterdir():
            if f.is_dir():
                continue
            fname = f.name
            stem = f.stem

            if stem == old_prefix_str or fname.startswith(old_prefix_str + "."):
                new_name = fname.replace(old_prefix_str, new_prefix_str, 1)
                temp_name = fname.replace(old_prefix_str, f"__TEMP_{old_key}__", 1)
                renames.append((f, media_dir / temp_name, media_dir / new_name))

        # Also check symlinks in jpg_for_compilation
        jpg_dir = media_dir / "jpg_for_compilation"
        if jpg_dir.exists():
            for f in jpg_dir.iterdir():
                fname = f.name
                if fname.startswith(old_prefix_str + ".") or f.stem == old_prefix_str:
                    new_name = fname.replace(old_prefix_str, new_prefix_str, 1)
                    temp_name = fname.replace(old_prefix_str, f"__TEMP_{old_key}__", 1)
                    renames.append((f, jpg_dir / temp_name, jpg_dir / new_name))

    if renames:
        # Pass 1: old -> temp
        for old_path, temp_path, _ in renames:
            if old_path.exists():
                action = "Would rename" if dry_run else "Renamed"
                if not dry_run:
                    old_path.rename(temp_path)

        # Pass 2: temp -> new
        for _, temp_path, new_path in renames:
            if temp_path.exists():
                action = "Would rename" if dry_run else "Renamed"
                print(f"    {action} {temp_path.parent.name}/{new_path.name}")
                if not dry_run:
                    temp_path.rename(new_path)


def main():
    parser = argparse.ArgumentParser(
        description="Check and fix figure/table reference ordering in LaTeX manuscripts"
    )
    parser.add_argument(
        "project_dir",
        nargs="?",
        default=".",
        help="Project root directory (default: current directory)",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-renumber files and update references to match appearance order",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what --fix would do without making changes",
    )
    parser.add_argument(
        "--doc-type",
        choices=["manuscript", "supplementary", "all"],
        default="all",
        help="Which document type to check (default: all)",
    )
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()

    doc_types = []
    if args.doc_type in ("manuscript", "all"):
        d = project_dir / "01_manuscript" / "contents"
        if d.exists():
            doc_types.append(("manuscript", d))
    if args.doc_type in ("supplementary", "all"):
        d = project_dir / "02_supplementary" / "contents"
        if d.exists():
            doc_types.append(("supplementary", d))

    if not doc_types:
        print(f"{RED}No content directories found in {project_dir}{NC}")
        sys.exit(1)

    print(f"\n{BOLD}=== Float Reference Order Check ==={NC}\n")

    has_issues = False
    all_mappings = []

    for doc_label, content_dir in doc_types:
        for float_type, float_label in [("fig", "Figure"), ("tab", "Table")]:
            label = f"{float_label} ({doc_label})"
            ok, refs, mapping = check_order(content_dir, float_type, label)
            if not ok:
                has_issues = True
                if mapping:
                    all_mappings.append((content_dir, float_type, mapping, label))

    print()

    if not has_issues:
        print(f"{GREEN}All float references are in order.{NC}")
        return 0

    if args.fix or args.dry_run:
        mode = "DRY RUN" if args.dry_run else "FIXING"
        print(f"{BOLD}--- {mode} ---{NC}\n")
        for content_dir, float_type, mapping, label in all_mappings:
            print(f"  {label}: renumbering {len(mapping)} items")
            for old, new in mapping.items():
                print(f"    {old} -> {new}")
            apply_fix(content_dir, float_type, mapping, dry_run=args.dry_run)
            print()

        if not args.dry_run:
            print(f"{GREEN}Renumbering complete. Re-run to verify.{NC}")
        return 0
    else:
        print(f"{YELLOW}Run with --fix to auto-renumber, or --dry-run to preview.{NC}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
