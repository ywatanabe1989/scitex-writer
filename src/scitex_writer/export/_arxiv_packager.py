#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/export/_arxiv_packager.py

"""File packaging for arXiv submission.

Pure functions to package manuscript files into arXiv-compatible
zip archives with validation.  No Django or ORM dependencies.
"""

import zipfile
from pathlib import Path
from typing import List, Tuple

# arXiv limits and allowed file types
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
ALLOWED_EXTENSIONS = {
    ".tex",
    ".bib",
    ".bbl",
    ".cls",
    ".sty",
    ".eps",
    ".ps",
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
}


def package_submission(
    work_dir: Path,
    submission_id: str = "submission",
) -> Path:
    """Package all files for arXiv submission.

    Args:
        work_dir: Working directory containing manuscript files.
        submission_id: Identifier for the output zip filename.

    Returns:
        Path to the created zip archive.

    Raises:
        ValueError: If the package exceeds the arXiv size limit.
    """
    work_dir = Path(work_dir)
    package_path = work_dir / f"arxiv_submission_{submission_id}.zip"

    with zipfile.ZipFile(package_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        # Add main LaTeX file
        if (work_dir / "main.tex").exists():
            zipf.write(work_dir / "main.tex", "main.tex")

        # Add bibliography
        if (work_dir / "references.bib").exists():
            zipf.write(work_dir / "references.bib", "references.bib")

        # Add figures
        figures_dir = work_dir / "figures"
        if figures_dir.exists():
            for figure_file in figures_dir.iterdir():
                if (
                    figure_file.is_file()
                    and figure_file.suffix.lower() in ALLOWED_EXTENSIONS
                ):
                    zipf.write(figure_file, f"figures/{figure_file.name}")

        # Add any additional allowed files
        for file_path in work_dir.iterdir():
            if (
                file_path.is_file()
                and file_path.suffix.lower() in ALLOWED_EXTENSIONS
                and file_path.name not in ["main.tex", "references.bib"]
            ):
                zipf.write(file_path, file_path.name)

    if package_path.stat().st_size > MAX_FILE_SIZE:
        raise ValueError(
            f"Submission package exceeds {MAX_FILE_SIZE / (1024 * 1024):.1f}MB limit"
        )

    return package_path


def validate_file_types(work_dir: Path) -> Tuple[List[str], List[str]]:
    """Validate file types in a directory against arXiv allowed types.

    Args:
        work_dir: Directory to validate.

    Returns:
        Tuple of (valid_files, invalid_files) as relative path strings.
    """
    work_dir = Path(work_dir)
    valid_files = []
    invalid_files = []

    for file_path in work_dir.rglob("*"):
        if file_path.is_file():
            if file_path.suffix.lower() in ALLOWED_EXTENSIONS:
                valid_files.append(str(file_path.relative_to(work_dir)))
            else:
                invalid_files.append(str(file_path.relative_to(work_dir)))

    return valid_files, invalid_files


# EOF
