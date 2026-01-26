#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-27
# File: src/scitex_writer/bib.py

"""Bibliography management functions.

Usage::

    import scitex_writer as sw

    # List bib files
    result = sw.bib.list_files("./my-paper")

    # List entries
    result = sw.bib.list_entries("./my-paper")

    # Add an entry
    sw.bib.add("./my-paper", "@article{Smith2024, ...}")

    # Merge all bib files
    sw.bib.merge("./my-paper")
"""

import re as _re
from typing import Optional as _Optional

from ._mcp.utils import resolve_project_path as _resolve_project_path


def list_files(project_dir: str) -> dict:
    """List all bibliography files in the project.

    Args:
        project_dir: Path to scitex-writer project.

    Returns:
        Dict with bibfiles list and count.
    """
    try:
        project_path = _resolve_project_path(project_dir)
        bib_dir = project_path / "00_shared" / "bib_files"

        if not bib_dir.exists():
            return {"success": True, "bibfiles": [], "count": 0}

        bibfiles = []
        for bib_file in sorted(bib_dir.glob("*.bib")):
            content = bib_file.read_text(encoding="utf-8")
            entry_count = content.count("@")
            bibfiles.append(
                {
                    "name": bib_file.name,
                    "path": str(bib_file),
                    "entry_count": entry_count,
                    "is_merged": bib_file.name == "bibliography.bib",
                }
            )

        return {"success": True, "bibfiles": bibfiles, "count": len(bibfiles)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_entries(project_dir: str, bibfile: _Optional[str] = None) -> dict:
    """List all BibTeX entries in the project or specific file.

    Args:
        project_dir: Path to scitex-writer project.
        bibfile: Specific bib file name (optional).

    Returns:
        Dict with entries list and count.
    """
    try:
        project_path = _resolve_project_path(project_dir)
        bib_dir = project_path / "00_shared" / "bib_files"

        if not bib_dir.exists():
            return {"success": True, "entries": [], "count": 0}

        entries = []
        files_to_scan = [bib_dir / bibfile] if bibfile else list(bib_dir.glob("*.bib"))

        for bib_file in files_to_scan:
            if not bib_file.exists():
                continue
            content = bib_file.read_text(encoding="utf-8")
            pattern = r"@(\w+)\{([^,\s]+)"
            for match in _re.finditer(pattern, content):
                entry_type, citation_key = match.groups()
                entries.append(
                    {
                        "citation_key": citation_key,
                        "entry_type": entry_type,
                        "bibfile": bib_file.name,
                    }
                )

        return {"success": True, "entries": entries, "count": len(entries)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get(project_dir: str, citation_key: str) -> dict:
    """Get a specific BibTeX entry by citation key.

    Args:
        project_dir: Path to scitex-writer project.
        citation_key: The citation key to find.

    Returns:
        Dict with entry content and bibfile path.
    """
    try:
        project_path = _resolve_project_path(project_dir)
        bib_dir = project_path / "00_shared" / "bib_files"

        if not bib_dir.exists():
            return {"success": False, "error": "No bib_files directory found"}

        for bib_file in bib_dir.glob("*.bib"):
            content = bib_file.read_text(encoding="utf-8")
            pattern = rf"(@\w+\{{{citation_key}\s*,.*?(?=\n@|\Z))"
            match = _re.search(pattern, content, _re.DOTALL)
            if match:
                return {
                    "success": True,
                    "citation_key": citation_key,
                    "bibfile": str(bib_file),
                    "entry": match.group(1).strip(),
                }

        return {"success": False, "error": f"Citation key not found: {citation_key}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def add(
    project_dir: str,
    bibtex_entry: str,
    bibfile: str = "custom.bib",
    deduplicate: bool = True,
) -> dict:
    """Add a BibTeX entry to a bibliography file.

    Args:
        project_dir: Path to scitex-writer project.
        bibtex_entry: The BibTeX entry to add.
        bibfile: Target bib file name (default: custom.bib).
        deduplicate: Check for existing entry with same key.

    Returns:
        Dict with bibfile path and citation_key.
    """
    try:
        project_path = _resolve_project_path(project_dir)
        bib_dir = project_path / "00_shared" / "bib_files"
        bib_dir.mkdir(parents=True, exist_ok=True)

        key_match = _re.search(r"@\w+\{([^,\s]+)", bibtex_entry)
        if not key_match:
            return {"success": False, "error": "Could not parse citation key"}
        citation_key = key_match.group(1)

        if deduplicate:
            existing = get(project_dir, citation_key)
            if existing.get("success"):
                return {
                    "success": False,
                    "error": f"Duplicate citation key: {citation_key}",
                    "existing_file": existing.get("bibfile"),
                }

        bib_path = bib_dir / bibfile
        if bib_path.exists():
            current_content = bib_path.read_text(encoding="utf-8")
            if not current_content.endswith("\n"):
                current_content += "\n"
            new_content = current_content + "\n" + bibtex_entry.strip() + "\n"
        else:
            new_content = bibtex_entry.strip() + "\n"

        bib_path.write_text(new_content, encoding="utf-8")

        return {
            "success": True,
            "bibfile": str(bib_path),
            "citation_key": citation_key,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def remove(project_dir: str, citation_key: str) -> dict:
    """Remove a BibTeX entry by citation key.

    Args:
        project_dir: Path to scitex-writer project.
        citation_key: The citation key to remove.

    Returns:
        Dict with removed_from path.
    """
    try:
        project_path = _resolve_project_path(project_dir)
        bib_dir = project_path / "00_shared" / "bib_files"

        if not bib_dir.exists():
            return {"success": False, "error": "No bib_files directory found"}

        for bib_file in bib_dir.glob("*.bib"):
            content = bib_file.read_text(encoding="utf-8")
            pattern = rf"@\w+\{{{citation_key}\s*,.*?(?=\n@|\Z)"
            match = _re.search(pattern, content, _re.DOTALL)
            if match:
                new_content = content[: match.start()] + content[match.end() :]
                new_content = _re.sub(r"\n{3,}", "\n\n", new_content).strip() + "\n"
                bib_file.write_text(new_content, encoding="utf-8")
                return {
                    "success": True,
                    "citation_key": citation_key,
                    "removed_from": str(bib_file),
                }

        return {"success": False, "error": f"Citation key not found: {citation_key}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def merge(
    project_dir: str,
    output_file: str = "bibliography.bib",
    deduplicate: bool = True,
) -> dict:
    """Merge all .bib files into one, with optional deduplication.

    Args:
        project_dir: Path to scitex-writer project.
        output_file: Output filename (default: bibliography.bib).
        deduplicate: Skip duplicate citation keys.

    Returns:
        Dict with entry_count and duplicates_skipped.
    """
    try:
        project_path = _resolve_project_path(project_dir)
        bib_dir = project_path / "00_shared" / "bib_files"

        if not bib_dir.exists():
            return {"success": False, "error": "No bib_files directory found"}

        output_path = bib_dir / output_file
        seen_keys = set()
        merged_entries = []
        duplicates = []

        for bib_file in sorted(bib_dir.glob("*.bib")):
            if bib_file.name == output_file:
                continue

            content = bib_file.read_text(encoding="utf-8")
            entries = _re.findall(r"(@\w+\{[^@]*)", content, _re.DOTALL)

            for entry in entries:
                entry = entry.strip()
                if not entry:
                    continue

                key_match = _re.search(r"@\w+\{([^,\s]+)", entry)
                if not key_match:
                    continue

                citation_key = key_match.group(1)

                if deduplicate and citation_key in seen_keys:
                    duplicates.append({"key": citation_key, "file": bib_file.name})
                    continue

                seen_keys.add(citation_key)
                merged_entries.append(entry)

        output_content = "\n\n".join(merged_entries) + "\n"
        output_path.write_text(output_content, encoding="utf-8")

        return {
            "success": True,
            "output_file": str(output_path),
            "entry_count": len(merged_entries),
            "duplicates_skipped": len(duplicates),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


__all__ = ["list_files", "list_entries", "get", "add", "remove", "merge"]

# EOF
