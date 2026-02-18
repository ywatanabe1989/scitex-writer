#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/export/_arxiv_cleaner.py

"""LaTeX cleaning and validation for arXiv submission.

Provides utilities for cleaning, validating, and normalizing
LaTeX content to meet arXiv compliance requirements.
"""

import re


class ArxivLatexCleaner:
    """Clean and validate LaTeX content for arXiv compliance."""

    def __init__(self):
        # Packages to remove or replace
        self.problematic_packages = {
            "pstricks": None,  # Not supported on arXiv
            "xy": "xymatrix",  # Replace with xymatrix
            "pdfpages": None,  # Not allowed
            "epstopdf": None,  # Automatic conversion
        }

        # arXiv-approved packages
        self.approved_packages = {
            "amsmath",
            "amsfonts",
            "amssymb",
            "amsthm",
            "graphicx",
            "cite",
            "natbib",
            "biblatex",
            "hyperref",
            "url",
            "geometry",
            "fancyhdr",
            "array",
            "booktabs",
            "longtable",
            "multirow",
            "algorithm",
            "algorithmic",
            "algorithm2e",
            "listings",
            "xcolor",
            "tikz",
            "pgfplots",
            "subcaption",
            "caption",
            "float",
        }

    def clean_latex_for_arxiv(self, latex_content: str) -> str:
        """Clean LaTeX content for arXiv compliance."""
        latex_content = self.remove_problematic_packages(latex_content)
        latex_content = self.fix_common_latex_issues(latex_content)
        latex_content = self.validate_packages(latex_content)
        latex_content = self.clean_formatting(latex_content)
        return latex_content

    def remove_problematic_packages(self, content: str) -> str:
        """Remove or replace packages not supported by arXiv."""
        for problematic, replacement in self.problematic_packages.items():
            pattern = rf"\\usepackage(?:\[[^\]]*\])?\{{{problematic}\}}"
            if replacement:
                repl = f"\\usepackage{{{replacement}}}"
                content = re.sub(pattern, lambda _: repl, content)
            else:
                content = re.sub(
                    pattern, f"% Removed unsupported package: {problematic}", content
                )
        return content

    def fix_common_latex_issues(self, content: str) -> str:
        """Fix common LaTeX issues for arXiv."""
        # Fix figure paths (remove absolute paths)
        content = re.sub(
            r"\\includegraphics\{[^}]*[/\\]([^/\\}]+)\}",
            r"\\includegraphics{\1}",
            content,
        )

        # Ensure UTF-8 encoding
        if (
            "\\usepackage[utf8]{inputenc}" not in content
            and "\\documentclass" in content
        ):
            content = content.replace(
                "\\documentclass", "\\usepackage[utf8]{inputenc}\n\\documentclass"
            )

        # Fix citation commands
        content = re.sub(r"\\cite\s*\{([^}]+)\}", r"\\cite{\1}", content)

        # Remove excessive whitespace
        content = re.sub(r"\n\s*\n\s*\n", "\n\n", content)

        return content

    def validate_packages(self, content: str) -> str:
        """Validate that only approved packages are used."""
        package_pattern = r"\\usepackage(?:\[[^\]]*\])?\{([^}]+)\}"
        packages = re.findall(package_pattern, content)

        warnings = []
        for package in packages:
            if package not in self.approved_packages:
                warnings.append(
                    f"Warning: Package '{package}' may not be supported by arXiv"
                )

        if warnings:
            warning_comment = (
                "% arXiv Package Warnings:\n% " + "\n% ".join(warnings) + "\n\n"
            )
            content = warning_comment + content

        return content

    def clean_formatting(self, content: str) -> str:
        """Clean up LaTeX formatting."""
        content = re.sub(r"\s*\{\s*", "{", content)
        content = re.sub(r"\s*\}\s*", "}", content)
        content = re.sub(r"(?<!\\)\\\\(?!\s*\n)", "\\\\\n", content)
        content = re.sub(r"%\s*$", "%", content, flags=re.MULTILINE)
        return content

    def clean_section_content(self, content: str) -> str:
        """Clean individual section content."""
        content = re.sub(r"^\\section\*?\{[^}]+\}\s*", "", content, flags=re.MULTILINE)
        content = content.strip()
        return content


# EOF
