#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-12 14:19:14 (ywatanabe)"

r"""
Fast recursive TeX structure compiler.

Replaces \input{} commands with file contents in single pass.
Performance: O(n) instead of O(n²).
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Optional, Set

sys.path.insert(0, str(Path(__file__).parent))
from _build_id import (  # noqa: E402
    generate_build_id,
    inject_build_metadata,
    register_build,
)
from _tex_signature import generate_signature  # noqa: E402


def _is_style_input(input_file: str) -> bool:
    r"""True if an \input target is a preamble style file (latex_styles/)."""
    return "latex_styles" in Path(input_file).parts


def _style_fallback(input_path: Path) -> Optional[Path]:
    r"""Resolve a latex_styles \input against 00_shared/latex_styles by basename.

    Preamble styles are \input via contents/latex_styles/ -- a dev-only,
    UNCOMMITTED symlink to 00_shared/latex_styles that a fresh clone/CI/worktree
    lacks. Resolved from cwd (= project root), like ./-prefixed inputs. Returns
    None if not a style input or the fallback is absent.
    """
    if "latex_styles" in input_path.parts:
        candidate = Path("00_shared") / "latex_styles" / input_path.name
        if candidate.exists():
            return candidate
    return None


def expand_inputs(
    file_path: Path,
    processed: Set[Path] = None,
    depth: int = 0,
    max_depth: int = 10,
    errors: Optional[list] = None,
) -> str:
    r"""
    Recursively expand \input{} commands.

    Args:
        file_path: TeX file to process
        processed: Set of already processed files (prevents infinite loops)
        depth: Current recursion depth
        max_depth: Maximum recursion depth
        errors: Accumulator for FATAL preamble-style misses (fail-loud). The
            top-level caller passes a list and aborts the compile if it is
            non-empty after expansion.

    Returns:
        Expanded content as string
    """
    if processed is None:
        processed = set()
    if errors is None:
        errors = []

    if depth > max_depth:
        return f"% ERROR: Max recursion depth ({max_depth}) exceeded\n"

    if not file_path.exists():
        return f"% SKIPPED: \\input{{{file_path}}} (file not found)\n"

    # Prevent infinite loops
    file_path = file_path.resolve()
    if file_path in processed:
        return f"% SKIPPED: \\input{{{file_path}}} (already processed - circular reference)\n"

    processed.add(file_path)

    # Read file
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return f"% ERROR: Could not read {file_path}: {e}\n"

    # Find all \input{} commands (but not commented lines)
    lines = content.split("\n")
    result_lines = []

    for line in lines:
        # Skip commented lines
        if re.match(r"^\s*%", line):
            result_lines.append(line)
            continue

        # Check for \input{} command
        match = re.search(r"\\input\{([^}]+)\}", line)

        if match:
            input_file = match.group(1)

            # Add .tex if not present
            if not input_file.endswith(".tex"):
                input_file += ".tex"

            input_path = Path(input_file)

            # If relative path starting with ./, resolve from git root (current working directory)
            # Otherwise resolve relative to current file's directory
            if not input_path.is_absolute():
                if input_file.startswith("./"):
                    # Path like ./03_revision/... should be from git root
                    input_path = Path(input_file)
                else:
                    # Path like contents/... is relative to current file
                    input_path = file_path.parent / input_path

            # Fresh-checkout robustness: a latex_styles \input missing in
            # contents/ falls back to 00_shared/latex_styles (uncommitted dev
            # symlink -- see _style_fallback).
            if not input_path.exists():
                fb = _style_fallback(input_path)
                if fb is not None:
                    input_path = fb

            # Add header comment
            result_lines.append("")
            result_lines.append("% " + "=" * 70)
            result_lines.append(f"% File: {input_file}")
            result_lines.append("% " + "=" * 70)

            if input_path.exists():
                expanded = expand_inputs(
                    input_path,
                    processed=processed,
                    depth=depth + 1,
                    max_depth=max_depth,
                    errors=errors,
                )
                result_lines.append(expanded)
            elif _is_style_input(input_file):
                # FAIL LOUD: a missing PREAMBLE STYLE input silently yields a
                # broken PDF (undefined \linenumbers etc.) on exit 0.
                msg = (
                    f"preamble style input not found: \\input{{{input_file}}} "
                    f"(searched contents/ and 00_shared/latex_styles/)"
                )
                errors.append(msg)
                result_lines.append(f"% FATAL: {msg}")
            else:
                result_lines.append(
                    f"% SKIPPED: \\input{{{input_file}}} (file not found)"
                )
            result_lines.append("")

        else:
            # No \input command, keep line as-is
            result_lines.append(line)

    return "\n".join(result_lines)


def compile_tex_structure(
    base_tex: Path,
    output_tex: Path,
    verbose: bool = True,
    dark_mode: bool = False,
    tectonic_mode: bool = False,
) -> bool:
    r"""
    Compile TeX structure by expanding all \input{} commands.

    Args:
        base_tex: Base TeX file with \input commands
        output_tex: Output compiled TeX file
        verbose: Print progress
        dark_mode: Enable dark mode (black background, white text)
        tectonic_mode: Disable incompatible packages for tectonic engine

    Returns:
        True if successful
    """
    if not base_tex.exists():
        print(f"ERROR: Base file not found: {base_tex}")
        return False

    if verbose:
        print(f"Compiling TeX structure: {base_tex}")
        print(f"Output: {output_tex}")
        if dark_mode:
            print("Dark mode: enabled")
        if tectonic_mode:
            print("Tectonic mode: enabled (disabling incompatible packages)")

    # Generate per-compilation build ID (#77)
    build_id = generate_build_id()
    if verbose:
        print(f"Build ID: build:{build_id}")

    # Expand all inputs recursively. A missing PREAMBLE STYLE \input is FATAL
    # (would silently yield a broken PDF); collect any and abort below.
    style_errors: list = []
    expanded_content = expand_inputs(base_tex, errors=style_errors)
    if style_errors:
        print(
            "ERROR: missing preamble style input(s) -- aborting (would produce "
            "a broken PDF on exit 0):",
            file=sys.stderr,
        )
        for e in style_errors:
            print(f"  - {e}", file=sys.stderr)
        print(
            "  Fix: ensure 00_shared/latex_styles/ holds the style files, or "
            "that contents/latex_styles resolves to them.",
            file=sys.stderr,
        )
        return False

    # Inject PDF metadata + \scitexBuildID macro before \begin{document}
    expanded_content = inject_build_metadata(expanded_content, build_id)

    # Prepend signature (now includes Build ID line)
    signature = generate_signature(source_file=base_tex, build_id=build_id)
    expanded_content = signature + expanded_content

    # Check for SciTeX citation
    # Color codes (matching bash scripts)
    GREEN = "\033[0;32m"
    YELLOW = "\033[0;33m"
    NC = "\033[0m"  # No Color

    if (
        r"\cite{watanabe2025scitex" in expanded_content
        or r"\citep{watanabe2025scitex" in expanded_content
        or r"\citet{watanabe2025scitex" in expanded_content
    ):
        print(f"{GREEN}{'=' * 78}{NC}")
        print(f"{GREEN}Thank you for citing SciTeX Writer! 🙏{NC}")
        print("")
        print(f"{GREEN}Your support helps maintain this open-source project.{NC}")
        print(f"{GREEN}Citation found: \\cite{{{{watanabe2025scitex}}}}{NC}")
        print(f"{GREEN}{'=' * 78}{NC}")
        print("")
    else:
        print(f"{YELLOW}{'=' * 78}{NC}")
        print(f"{YELLOW}WARN: SciTeX Writer citation not found!{NC}")
        print("")
        print(f"{YELLOW}Please consider citing SciTeX Writer in your manuscript:{NC}")
        print("  \\cite{watanabe2025scitex}")
        print("")
        print(f"{YELLOW}Add this to your bibliography by including:{NC}")
        print("  00_shared/bib_files/scitex-system.bib")
        print("")
        print(f"{YELLOW}Or merge it with your existing bibliography files.{NC}")
        print(f"{YELLOW}{'=' * 78}{NC}")
        print("")

    # Apply tectonic compatibility if enabled
    if tectonic_mode:
        # Comment out incompatible packages
        expanded_content = re.sub(
            r"(\\usepackage\{[^}]*lineno[^}]*\})",
            r"% \1  % Disabled for tectonic",
            expanded_content,
        )
        expanded_content = re.sub(
            r"(\\usepackage\{[^}]*bashful[^}]*\})",
            r"% \1  % Disabled for tectonic",
            expanded_content,
        )
        # Comment out \linenumbers command
        expanded_content = re.sub(
            r"(^\\linenumbers)",
            r"% \1  % Disabled for tectonic",
            expanded_content,
            flags=re.MULTILINE,
        )

        # Replace \readwordcount{file} with actual file contents
        # Find all \readwordcount commands
        def replace_wordcount(match):
            file_path = match.group(1)
            try:
                # Resolve file path (could be relative or absolute)
                if not file_path.startswith("/"):
                    # Paths starting with ./ are relative to project root, not base_tex
                    if file_path.startswith("./"):
                        # Use current working directory as base (should be project root)
                        full_path = Path(file_path)
                    else:
                        # Relative to base_tex directory
                        full_path = base_tex.parent / file_path
                else:
                    full_path = Path(file_path)

                # Read the count value
                with open(full_path, "r") as f:
                    count_value = f.read().strip()

                # Match the \readwordcount macro's thousands separator (e.g.
                # 1,259) so tectonic mode (which inlines the raw number) renders
                # the same as the latexmk/pdflatex path.
                if count_value.isdigit():
                    count_value = f"{int(count_value):,}"
                return count_value
            except Exception as e:
                # If file can't be read, return a placeholder with debug info
                return f"??({e})"

        expanded_content = re.sub(
            r"\\readwordcount\{([^}]+)\}", replace_wordcount, expanded_content
        )

    # Inject dark mode styling if enabled
    if dark_mode:
        # Read dark_mode.tex content and inline it (avoid \input path issues)
        dark_mode_file = (
            base_tex.parent.parent / "00_shared" / "latex_styles" / "dark_mode.tex"
        )
        if dark_mode_file.exists():
            with open(dark_mode_file, "r", encoding="utf-8") as f:
                dark_mode_content = f.read()
            # Substitute colors from config env vars (DRY with config/*.yaml)
            color_subs = {
                "1E1E1E": os.getenv("SCITEX_WRITER_DARK_BG", "1E1E1E"),
                "D4D4D4": os.getenv("SCITEX_WRITER_DARK_FG", "D4D4D4"),
                "90C695": os.getenv("SCITEX_WRITER_DARK_LINK_INTERNAL", "90C695"),
                "87CEEB": os.getenv("SCITEX_WRITER_DARK_LINK_CITATION", "87CEEB"),
                "DEB887": os.getenv("SCITEX_WRITER_DARK_LINK_URL", "DEB887"),
            }
            for old_hex, new_hex in color_subs.items():
                dark_mode_content = dark_mode_content.replace(old_hex, new_hex)
            dark_mode_injection = (
                "\n% Dark mode styling (inlined at compile time)\n"
                + dark_mode_content
                + "\n"
            )
        else:
            print(f"WARNING: Dark mode file not found: {dark_mode_file}")
            dark_mode_injection = ""

        if dark_mode_injection:
            # Inject dark mode styling before \begin{document}
            # Leave hyperref/link colors untouched (use document defaults)
            expanded_content = expanded_content.replace(
                r"\begin{document}",
                dark_mode_injection + r"\begin{document}",
            )

    # Write output
    try:
        output_tex.parent.mkdir(parents=True, exist_ok=True)
        with open(output_tex, "w", encoding="utf-8") as f:
            f.write(expanded_content)

        if verbose:
            line_count = len(expanded_content.split("\n"))
            print(f"✓ Compiled: {line_count} lines")
            print(f"  Output: {output_tex}")

        # Record the build (#77). doc_type is derived from the
        # SCITEX_WRITER_DOC_TYPE env var that compile.sh sets.
        doc_type = os.getenv("SCITEX_WRITER_DOC_TYPE", "unknown")
        register_build(build_id, doc_type, output_tex)

        return True

    except Exception as e:
        print(f"ERROR: Failed to write output: {e}")
        return False


def _read_config_theme(base_tex: Path) -> str:
    """Read ``theme:`` from config/config_<doctype>.yaml — returns 'light' or 'dark'.

    The project root is the parent of the document dir holding base.tex (e.g.
    ``<root>/01_manuscript/base.tex`` -> ``<root>``), matching how the
    dark_mode.tex path is resolved above.

    Fail loud (SystemExit) on an invalid theme value so a typo cannot silently
    render the wrong theme. A missing file / missing PyYAML / unreadable YAML
    degrade to 'light' (the knob simply has no effect).
    """
    doc_type = os.getenv("SCITEX_WRITER_DOC_TYPE", "manuscript")
    config_path = (
        base_tex.resolve().parent.parent / "config" / f"config_{doc_type}.yaml"
    )
    if not config_path.exists():
        return "light"
    try:
        import yaml
    except ImportError:
        return "light"
    try:
        data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return "light"
    theme = data.get("theme", "light")
    theme = "light" if theme is None else str(theme).strip().lower()
    if theme not in ("light", "dark"):
        print(
            f"ERROR: Invalid theme '{theme}' in {config_path.name} — "
            f"must be 'light' or 'dark'.",
            file=sys.stderr,
        )
        raise SystemExit(2)
    return theme


def _resolve_dark_mode(explicit_flag: bool, base_tex: Path) -> bool:
    """Resolve effective dark mode with precedence.

    ``--dark-mode`` flag > ``SCITEX_WRITER_DARK_MODE`` env > config ``theme:``
    > light. Only a *set* (non-empty) env var short-circuits the config, so
    ``theme: dark`` takes effect when no flag/env is supplied.
    """
    if explicit_flag:
        return True
    env = os.getenv("SCITEX_WRITER_DARK_MODE")
    if env is not None and env.strip() != "":
        return env.strip().lower() == "true"
    return _read_config_theme(base_tex) == "dark"


def main():
    """Command-line interface."""
    import os

    parser = argparse.ArgumentParser(
        description="Compile TeX structure by expanding \\input{} commands"
    )
    parser.add_argument("base_tex", type=Path, help="Base TeX file")
    parser.add_argument("output_tex", type=Path, help="Output compiled TeX file")
    parser.add_argument("-q", "--quiet", action="store_true", help="Quiet mode")
    parser.add_argument(
        "--dark-mode",
        action="store_true",
        help="Enable dark mode (black background, white text)",
    )
    parser.add_argument(
        "--tectonic-mode",
        action="store_true",
        help="Enable tectonic compatibility (disable incompatible packages)",
    )

    args = parser.parse_args()

    # Check environment variables if arguments not provided
    dark_mode = _resolve_dark_mode(args.dark_mode, args.base_tex)
    tectonic_mode = (
        args.tectonic_mode
        or os.getenv("SCITEX_WRITER_ENGINE", "") == "tectonic"
        or os.getenv("SCITEX_WRITER_SELECTED_ENGINE", "") == "tectonic"
    )

    success = compile_tex_structure(
        base_tex=args.base_tex,
        output_tex=args.output_tex,
        verbose=not args.quiet,
        dark_mode=dark_mode,
        tectonic_mode=tectonic_mode,
    )

    exit(0 if success else 1)


if __name__ == "__main__":
    main()

# EOF
