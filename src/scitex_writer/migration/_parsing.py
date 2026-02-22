#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/migration/_parsing.py

"""LaTeX parsing helpers for Overleaf migration."""

import re
from pathlib import Path
from typing import Optional

# Image extensions recognised as figures
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".pdf", ".eps", ".svg", ".tif", ".tiff"}

# Table data extensions
TABLE_EXTS = {".csv", ".tsv"}

# Priority names for detecting the main .tex file
MAIN_TEX_PRIORITY = ["main.tex", "paper.tex", "manuscript.tex", "article.tex"]

# IMRAD section patterns (filename or \section{} heading match)
SECTION_PATTERNS = {
    "abstract": [r"abstract", r"summary"],
    "introduction": [r"intro", r"background"],
    "methods": [r"method", r"material", r"experimental", r"procedure"],
    "results": [r"result", r"finding", r"observation"],
    "discussion": [r"discuss", r"conclu", r"implication"],
}

# Canonical scitex-writer section filenames
IMRAD_SECTIONS = ["abstract", "introduction", "methods", "results", "discussion"]


def read_tex(path: Path) -> str:
    """Read a .tex file with encoding fallback."""
    for enc in ("utf-8", "latin-1"):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    return ""


def detect_main_tex(extracted_dir: Path) -> Optional[Path]:
    """Find the root .tex file containing \\documentclass.

    Strategy:
    1. Scan all .tex files for \\documentclass (not in comments)
    2. If exactly one found, return it
    3. If multiple: prefer main.tex > paper.tex > manuscript.tex > article.tex
    4. If still ambiguous, prefer shallowest directory depth
    """
    candidates = []
    for tex_file in extracted_dir.rglob("*.tex"):
        content = read_tex(tex_file)
        if re.search(r"^[^%]*\\documentclass", content, re.MULTILINE):
            candidates.append(tex_file)

    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]

    for name in MAIN_TEX_PRIORITY:
        matches = [c for c in candidates if c.name == name]
        if matches:
            return matches[0]

    return min(candidates, key=lambda p: len(p.relative_to(extracted_dir).parts))


def parse_inputs(main_tex_path: Path, base_dir: Path, _depth: int = 0) -> list[dict]:
    """Parse \\input{} and \\include{} directives from a .tex file.

    Recursively follows nested \\input up to depth 10.
    """
    if _depth > 10:
        return []

    content = read_tex(main_tex_path)
    results = []
    pattern = re.compile(r"^[^%\n]*\\(input|include)\{([^}]+)\}", re.MULTILINE)

    for match in pattern.finditer(content):
        cmd = match.group(1)
        arg = match.group(2).strip()

        rel_path = Path(arg)
        if not rel_path.suffix:
            rel_path = rel_path.with_suffix(".tex")

        resolved = (main_tex_path.parent / rel_path).resolve()
        if not resolved.exists():
            resolved = (base_dir / rel_path).resolve()

        entry = {
            "command": cmd,
            "arg": arg,
            "resolved_path": resolved,
            "exists": resolved.exists(),
        }
        results.append(entry)

        if resolved.exists() and resolved.suffix == ".tex":
            nested = parse_inputs(resolved, base_dir, _depth + 1)
            results.extend(nested)

    return results


def extract_metadata(content: str) -> dict:
    """Extract \\title{}, \\author{}, keywords from main .tex content."""
    metadata = {"title": None, "authors_block": None, "keywords": None}

    title_match = re.search(r"\\title\{([^}]+)\}", content)
    if title_match:
        metadata["title"] = title_match.group(1).strip()

    author_match = re.search(r"\\author\{([^}]+)\}", content)
    if author_match:
        metadata["authors_block"] = author_match.group(1).strip()

    kw_match = re.search(
        r"\\begin\{keyword[s]?\}(.*?)\\end\{keyword[s]?\}", content, re.DOTALL
    )
    if not kw_match:
        kw_match = re.search(r"\\keywords\{([^}]+)\}", content)
    if kw_match:
        metadata["keywords"] = kw_match.group(1).strip()

    return metadata


def classify_section(tex_path: Path, content: str) -> Optional[str]:
    """Map a .tex file to an IMRAD section name."""
    name = tex_path.stem.lower()

    for section, patterns in SECTION_PATTERNS.items():
        if any(re.search(p, name) for p in patterns):
            return section

    section_cmd = re.search(r"\\section\*?\{([^}]+)\}", content)
    if section_cmd:
        heading = section_cmd.group(1).lower()
        for section, patterns in SECTION_PATTERNS.items():
            if any(re.search(p, heading) for p in patterns):
                return section

    return None


def split_inline_sections(content: str) -> dict[str, str]:
    """Split monolithic main.tex body into IMRAD sections by \\section{} boundaries."""
    pattern = re.compile(r"\\section\*?\{([^}]+)\}")
    matches = list(pattern.finditer(content))

    if not matches:
        return {}

    sections = {}
    for i, match in enumerate(matches):
        heading = match.group(1).strip()
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        section_content = content[start:end].strip()

        heading_lower = heading.lower()
        section_name = None
        for name, pats in SECTION_PATTERNS.items():
            if any(re.search(p, heading_lower) for p in pats):
                section_name = name
                break

        if section_name:
            if section_name in sections:
                sections[section_name] += "\n\n" + section_content
            else:
                sections[section_name] = section_content

    return sections


def find_bib_files(d: Path) -> list[Path]:
    """Find all .bib files."""
    return sorted(d.rglob("*.bib"))


def find_image_files(d: Path) -> list[Path]:
    """Find all image files, excluding compiled-looking PDFs."""
    images = []
    skip_stems = {"main", "output", "manuscript", "paper"}
    for f in d.rglob("*"):
        if f.suffix.lower() in IMAGE_EXTS and f.is_file():
            if f.suffix.lower() == ".pdf" and f.stem in skip_stems:
                continue
            images.append(f)
    return sorted(images)


def find_table_files(d: Path) -> list[Path]:
    """Find CSV and TSV files."""
    return sorted(f for f in d.rglob("*") if f.suffix.lower() in TABLE_EXTS)


def find_style_files(d: Path) -> list[Path]:
    """Find custom .cls, .sty, and .bst files."""
    styles = []
    for ext in ("*.cls", "*.sty", "*.bst"):
        styles.extend(d.rglob(ext))
    return sorted(styles)


def unique_dest(dest: Path) -> Path:
    """Return dest if it doesn't exist; otherwise append _N suffix."""
    if not dest.exists():
        return dest
    stem, suffix = dest.stem, dest.suffix
    n = 1
    while True:
        candidate = dest.parent / f"{stem}_{n}{suffix}"
        if not candidate.exists():
            return candidate
        n += 1


# EOF
