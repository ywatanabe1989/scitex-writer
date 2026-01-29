#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-27
# File: src/scitex_writer/_mcp/tools/bib.py

"""Bibliography MCP tools."""

from __future__ import annotations

import re
from typing import Optional

from fastmcp import FastMCP

from ..utils import resolve_project_path


def register_tools(mcp: FastMCP) -> None:
    """Register bibliography tools."""

    @mcp.tool()
    def writer_list_bibfiles(project_dir: str) -> dict:
        """[writer] List all bibliography files in the project."""
        try:
            project_path = resolve_project_path(project_dir)
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

    @mcp.tool()
    def writer_list_bibentries(project_dir: str, bibfile: Optional[str] = None) -> dict:
        """[writer] List all BibTeX entries in the project or specific file."""
        try:
            project_path = resolve_project_path(project_dir)
            bib_dir = project_path / "00_shared" / "bib_files"

            if not bib_dir.exists():
                return {"success": True, "entries": [], "count": 0}

            entries = []
            files_to_scan = (
                [bib_dir / bibfile] if bibfile else list(bib_dir.glob("*.bib"))
            )

            for bib_file in files_to_scan:
                if not bib_file.exists():
                    continue
                content = bib_file.read_text(encoding="utf-8")
                # Extract citation keys and types
                pattern = r"@(\w+)\{([^,\s]+)"
                for match in re.finditer(pattern, content):
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

    @mcp.tool()
    def writer_get_bibentry(project_dir: str, citation_key: str) -> dict:
        """[writer] Get a specific BibTeX entry by citation key."""
        try:
            project_path = resolve_project_path(project_dir)
            bib_dir = project_path / "00_shared" / "bib_files"

            if not bib_dir.exists():
                return {"success": False, "error": "No bib_files directory found"}

            for bib_file in bib_dir.glob("*.bib"):
                content = bib_file.read_text(encoding="utf-8")
                # Match @type{citation_key, ... }
                pattern = rf"(@\w+\{{{citation_key}\s*,.*?(?=\n@|\Z))"
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    return {
                        "success": True,
                        "citation_key": citation_key,
                        "bibfile": str(bib_file),
                        "entry": match.group(1).strip(),
                    }

            return {
                "success": False,
                "error": f"Citation key not found: {citation_key}",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @mcp.tool()
    def writer_add_bibentry(
        project_dir: str,
        bibtex_entry: str,
        bibfile: str = "custom.bib",
        deduplicate: bool = True,
    ) -> dict:
        """[writer] Add a BibTeX entry to a bibliography file.

        Args:
            project_dir: Path to project
            bibtex_entry: The BibTeX entry to add
            bibfile: Target bib file name (default: custom.bib)
            deduplicate: Check for existing entry with same key (default: True)
        """
        try:
            project_path = resolve_project_path(project_dir)
            bib_dir = project_path / "00_shared" / "bib_files"
            bib_dir.mkdir(parents=True, exist_ok=True)

            # Extract citation key from entry
            key_match = re.search(r"@\w+\{([^,\s]+)", bibtex_entry)
            if not key_match:
                return {"success": False, "error": "Could not parse citation key"}
            citation_key = key_match.group(1)

            # Check for duplicates if requested
            if deduplicate:
                existing = writer_get_bibentry.__wrapped__(project_dir, citation_key)
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
                "message": f"Entry '{citation_key}' added to {bibfile}",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @mcp.tool()
    def writer_remove_bibentry(
        project_dir: str,
        citation_key: str,
    ) -> dict:
        """[writer] Remove a BibTeX entry by citation key."""
        try:
            project_path = resolve_project_path(project_dir)
            bib_dir = project_path / "00_shared" / "bib_files"

            if not bib_dir.exists():
                return {"success": False, "error": "No bib_files directory found"}

            for bib_file in bib_dir.glob("*.bib"):
                content = bib_file.read_text(encoding="utf-8")
                # Match the full entry
                pattern = rf"@\w+\{{{citation_key}\s*,.*?(?=\n@|\Z)"
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    new_content = content[: match.start()] + content[match.end() :]
                    # Clean up extra newlines
                    new_content = re.sub(r"\n{3,}", "\n\n", new_content).strip() + "\n"
                    bib_file.write_text(new_content, encoding="utf-8")
                    return {
                        "success": True,
                        "citation_key": citation_key,
                        "removed_from": str(bib_file),
                    }

            return {
                "success": False,
                "error": f"Citation key not found: {citation_key}",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @mcp.tool()
    def writer_merge_bibfiles(
        project_dir: str,
        output_file: str = "bibliography.bib",
        deduplicate: bool = True,
    ) -> dict:
        """[writer] Merge all .bib files into one, with optional deduplication.

        Deduplication is done by citation key (first occurrence wins).
        """
        try:
            project_path = resolve_project_path(project_dir)
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
                # Split into entries
                entries = re.findall(r"(@\w+\{[^@]*)", content, re.DOTALL)

                for entry in entries:
                    entry = entry.strip()
                    if not entry:
                        continue

                    # Extract citation key
                    key_match = re.search(r"@\w+\{([^,\s]+)", entry)
                    if not key_match:
                        continue

                    citation_key = key_match.group(1)

                    if deduplicate and citation_key in seen_keys:
                        duplicates.append({"key": citation_key, "file": bib_file.name})
                        continue

                    seen_keys.add(citation_key)
                    merged_entries.append(entry)

            # Write merged file
            output_content = "\n\n".join(merged_entries) + "\n"
            output_path.write_text(output_content, encoding="utf-8")

            return {
                "success": True,
                "output_file": str(output_path),
                "entry_count": len(merged_entries),
                "duplicates_skipped": len(duplicates),
                "duplicates": duplicates[:10] if duplicates else [],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


# EOF
