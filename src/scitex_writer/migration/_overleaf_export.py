#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/migration/_overleaf_export.py

"""Export logic: scitex-writer project -> Overleaf-compatible ZIP."""

import zipfile
from pathlib import Path
from typing import Optional

from ._parsing import IMAGE_EXTS, IMRAD_SECTIONS, read_tex


def _resolve_project_path(project_dir: str) -> Path:
    """Resolve project directory to absolute path."""
    project_path = Path(project_dir)
    if not project_path.is_absolute():
        project_path = Path.cwd() / project_path
    return project_path.resolve()


def to_overleaf(
    project_dir: str = ".",
    output_path: Optional[str] = None,
    dry_run: bool = False,
) -> dict:
    """Export a scitex-writer project as an Overleaf-compatible ZIP.

    Parameters
    ----------
    project_dir : str
        Path to the scitex-writer project.
    output_path : str, optional
        Path for the output .zip. Defaults to {project_dir}/overleaf_export.zip.
    dry_run : bool
        If True, report what would be included without creating the ZIP.
    """
    try:
        project_path = _resolve_project_path(project_dir)
        if not project_path.exists():
            return {"success": False, "error": f"Project not found: {project_path}"}
        if not (project_path / "00_shared").exists():
            return {
                "success": False,
                "error": f"{project_path} does not look like a scitex-writer project.",
            }

        warnings = []
        files: list[tuple[Path, str]] = []
        contents = project_path / "01_manuscript" / "contents"

        main_tex = _build_main_tex(project_path, contents, files)
        merged_bib = _collect_bib(project_path)
        _collect_figures(contents, files)
        _collect_styles(project_path, files)

        archive_names = ["main.tex"]
        if merged_bib:
            archive_names.append("references.bib")
        archive_names.extend(name for _, name in files)

        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "zip_path": output_path or str(project_path / "overleaf_export.zip"),
                "file_count": len(archive_names),
                "files_included": archive_names,
                "warnings": warnings,
                "message": f"Dry run: would create ZIP with {len(archive_names)} files.",
            }

        zip_dest = (
            Path(output_path).resolve()
            if output_path
            else project_path / "overleaf_export.zip"
        )
        zip_dest.parent.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_dest, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("main.tex", main_tex)
            if merged_bib:
                zf.writestr("references.bib", "\n\n".join(merged_bib))
            for source, archive_name in files:
                zf.write(source, archive_name)

        return {
            "success": True,
            "dry_run": False,
            "zip_path": str(zip_dest),
            "file_count": len(archive_names),
            "files_included": archive_names,
            "warnings": warnings,
            "message": f"Exported {len(archive_names)} files to {zip_dest}.",
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


def _build_main_tex(project_path, contents, files):
    """Build main.tex suitable for Overleaf from project structure."""
    lines = []

    base_tex = project_path / "01_manuscript" / "base.tex"
    if base_tex.exists():
        base_content = read_tex(base_tex)
        doc_start = base_content.find(r"\begin{document}")
        if doc_start >= 0:
            lines.append(base_content[:doc_start].strip())
        else:
            lines.append(r"\documentclass[a4paper,12pt]{article}")
    else:
        lines.append(r"\documentclass[a4paper,12pt]{article}")

    title_file = project_path / "00_shared" / "title.tex"
    authors_file = project_path / "00_shared" / "authors.tex"
    title = read_tex(title_file).strip() if title_file.exists() else ""
    authors = read_tex(authors_file).strip() if authors_file.exists() else ""

    lines.append("")
    if title:
        lines.append(f"\\title{{{title}}}")
    if authors:
        lines.append(f"\\author{{{authors}}}")
    lines.extend(["", r"\begin{document}", r"\maketitle", ""])

    for section in IMRAD_SECTIONS:
        f = contents / f"{section}.tex"
        if f.exists() and read_tex(f).strip():
            lines.append(f"\\input{{sections/{section}}}")
            files.append((f, f"sections/{section}.tex"))

    lines.extend(
        [
            "",
            r"\bibliographystyle{plain}",
            r"\bibliography{references}",
            "",
            r"\end{document}",
        ]
    )
    return "\n".join(lines) + "\n"


def _collect_bib(project_path):
    """Merge all .bib files."""
    bib_dir = project_path / "00_shared" / "bib_files"
    merged = []
    if bib_dir.exists():
        for f in sorted(bib_dir.glob("*.bib")):
            merged.append(read_tex(f))
    return merged


def _collect_figures(contents, files):
    """Collect figure files from project."""
    for fig_dir in [
        contents / "figures" / "caption_and_media",
        contents / "figures" / "compiled",
    ]:
        if not fig_dir.exists():
            continue
        for img in sorted(fig_dir.iterdir()):
            if img.suffix.lower() in IMAGE_EXTS and img.is_file():
                files.append((img, f"images/{img.name}"))


def _collect_styles(project_path, files):
    """Collect custom style files."""
    styles_dir = project_path / "00_shared" / "latex_styles"
    if not styles_dir.exists():
        return
    for sty in sorted(styles_dir.iterdir()):
        if sty.suffix.lower() in (".sty", ".cls", ".bst") and sty.is_file():
            files.append((sty, sty.name))


# EOF
