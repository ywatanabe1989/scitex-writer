#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-09 21:35:00 (ywatanabe)"
# File: ./scripts/python/compile_tex_structure.py
"""
Fast recursive TeX structure compiler.

Replaces \input{} commands with file contents in single pass.
Performance: O(n) instead of O(n²).
"""

import argparse
import re
from pathlib import Path
from typing import Set


def expand_inputs(
    file_path: Path,
    processed: Set[Path] = None,
    depth: int = 0,
    max_depth: int = 10
) -> str:
    """
    Recursively expand \input{} commands.

    Args:
        file_path: TeX file to process
        processed: Set of already processed files (prevents infinite loops)
        depth: Current recursion depth
        max_depth: Maximum recursion depth

    Returns:
        Expanded content as string
    """
    if processed is None:
        processed = set()

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
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return f"% ERROR: Could not read {file_path}: {e}\n"

    # Find all \input{} commands (but not commented lines)
    lines = content.split('\n')
    result_lines = []

    for line in lines:
        # Skip commented lines
        if re.match(r'^\s*%', line):
            result_lines.append(line)
            continue

        # Check for \input{} command
        match = re.search(r'\\input\{([^}]+)\}', line)

        if match:
            input_file = match.group(1)

            # Add .tex if not present
            if not input_file.endswith('.tex'):
                input_file += '.tex'

            input_path = Path(input_file)

            # If relative path, resolve relative to current file's directory
            if not input_path.is_absolute():
                input_path = file_path.parent / input_path

            # Add header comment
            result_lines.append('')
            result_lines.append('% ' + '=' * 70)
            result_lines.append(f'% File: {input_file}')
            result_lines.append('% ' + '=' * 70)

            # Recursively expand
            expanded = expand_inputs(
                input_path,
                processed=processed,
                depth=depth + 1,
                max_depth=max_depth
            )

            result_lines.append(expanded)
            result_lines.append('')

        else:
            # No \input command, keep line as-is
            result_lines.append(line)

    return '\n'.join(result_lines)


def compile_tex_structure(
    base_tex: Path,
    output_tex: Path,
    verbose: bool = True
) -> bool:
    """
    Compile TeX structure by expanding all \input{} commands.

    Args:
        base_tex: Base TeX file with \input commands
        output_tex: Output compiled TeX file
        verbose: Print progress

    Returns:
        True if successful
    """
    if not base_tex.exists():
        print(f"ERROR: Base file not found: {base_tex}")
        return False

    if verbose:
        print(f"Compiling TeX structure: {base_tex}")
        print(f"Output: {output_tex}")

    # Expand all inputs recursively
    expanded_content = expand_inputs(base_tex)

    # Write output
    try:
        output_tex.parent.mkdir(parents=True, exist_ok=True)
        with open(output_tex, 'w', encoding='utf-8') as f:
            f.write(expanded_content)

        if verbose:
            line_count = len(expanded_content.split('\n'))
            print(f"✓ Compiled: {line_count} lines")
            print(f"  Output: {output_tex}")

        return True

    except Exception as e:
        print(f"ERROR: Failed to write output: {e}")
        return False


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Compile TeX structure by expanding \\input{} commands"
    )
    parser.add_argument(
        "base_tex",
        type=Path,
        help="Base TeX file"
    )
    parser.add_argument(
        "output_tex",
        type=Path,
        help="Output compiled TeX file"
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Quiet mode"
    )

    args = parser.parse_args()

    success = compile_tex_structure(
        base_tex=args.base_tex,
        output_tex=args.output_tex,
        verbose=not args.quiet
    )

    exit(0 if success else 1)


if __name__ == "__main__":
    main()


# EOF
