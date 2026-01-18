#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: compile_tex_structure.py

import os
import sys
from pathlib import Path

# Add scripts/python to path for imports
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts" / "python"))


# Add your tests here
def test_placeholder():
    """TODO: Add tests for compile_tex_structure.py"""
    pass


if __name__ == "__main__":
    import pytest

    pytest.main([os.path.abspath(__file__), "-v"])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/scitex-writer/scripts/python/compile_tex_structure.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-11-12 14:19:14 (ywatanabe)"
#
# """
# Fast recursive TeX structure compiler.
#
# Replaces \input{} commands with file contents in single pass.
# Performance: O(n) instead of O(n²).
# """
#
# import argparse
# import os
# import re
# from datetime import datetime
# from pathlib import Path
# from typing import Set
#
#
# def generate_signature(source_file: Path = None) -> str:
#     """
#     Generate compilation signature comment block.
#
#     Args:
#         source_file: Original source file path (optional)
#
#     Returns:
#         Formatted signature as comment block
#     """
#     # Read version
#     version_file = Path("VERSION")
#     try:
#         with open(version_file, "r") as f:
#             version = f.read().strip()
#     except:
#         version = "unknown"
#
#     # Get engine
#     engine = (
#         os.getenv("SCITEX_WRITER_SELECTED_ENGINE", "")
#         or os.getenv("SCITEX_WRITER_ENGINE", "")
#         or "auto"
#     )
#
#     # Get timestamp
#     timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#
#     # Format signature
#     signature = f"""% {'=' * 78}
# % SciTeX Writer {version} (https://scitex.ai)
# % LaTeX compilation engine: {engine}
# % Compiled: {timestamp}
# """
#
#     if source_file:
#         signature += f"% Source: {source_file}\n"
#
#     signature += f"""% {'=' * 78}
#
# """
#     return signature
#
#
# def expand_inputs(
#     file_path: Path,
#     processed: Set[Path] = None,
#     depth: int = 0,
#     max_depth: int = 10,
# ) -> str:
#     """
#     Recursively expand \input{} commands.
#
#     Args:
#         file_path: TeX file to process
#         processed: Set of already processed files (prevents infinite loops)
#         depth: Current recursion depth
#         max_depth: Maximum recursion depth
#
#     Returns:
#         Expanded content as string
#     """
#     if processed is None:
#         processed = set()
#
#     if depth > max_depth:
#         return f"% ERROR: Max recursion depth ({max_depth}) exceeded\n"
#
#     if not file_path.exists():
#         return f"% SKIPPED: \\input{{{file_path}}} (file not found)\n"
#
#     # Prevent infinite loops
#     file_path = file_path.resolve()
#     if file_path in processed:
#         return f"% SKIPPED: \\input{{{file_path}}} (already processed - circular reference)\n"
#
#     processed.add(file_path)
#
#     # Read file
#     try:
#         with open(file_path, "r", encoding="utf-8") as f:
#             content = f.read()
#     except Exception as e:
#         return f"% ERROR: Could not read {file_path}: {e}\n"
#
#     # Find all \input{} commands (but not commented lines)
#     lines = content.split("\n")
#     result_lines = []
#
#     for line in lines:
#         # Skip commented lines
#         if re.match(r"^\s*%", line):
#             result_lines.append(line)
#             continue
#
#         # Check for \input{} command
#         match = re.search(r"\\input\{([^}]+)\}", line)
#
#         if match:
#             input_file = match.group(1)
#
#             # Add .tex if not present
#             if not input_file.endswith(".tex"):
#                 input_file += ".tex"
#
#             input_path = Path(input_file)
#
#             # If relative path starting with ./, resolve from git root (current working directory)
#             # Otherwise resolve relative to current file's directory
#             if not input_path.is_absolute():
#                 if input_file.startswith("./"):
#                     # Path like ./03_revision/... should be from git root
#                     input_path = Path(input_file)
#                 else:
#                     # Path like contents/... is relative to current file
#                     input_path = file_path.parent / input_path
#
#             # Add header comment
#             result_lines.append("")
#             result_lines.append("% " + "=" * 70)
#             result_lines.append(f"% File: {input_file}")
#             result_lines.append("% " + "=" * 70)
#
#             # Recursively expand
#             expanded = expand_inputs(
#                 input_path,
#                 processed=processed,
#                 depth=depth + 1,
#                 max_depth=max_depth,
#             )
#
#             result_lines.append(expanded)
#             result_lines.append("")
#
#         else:
#             # No \input command, keep line as-is
#             result_lines.append(line)
#
#     return "\n".join(result_lines)
#
#
# def compile_tex_structure(
#     base_tex: Path,
#     output_tex: Path,
#     verbose: bool = True,
#     dark_mode: bool = False,
#     tectonic_mode: bool = False,
# ) -> bool:
#     """
#     Compile TeX structure by expanding all \input{} commands.
#
#     Args:
#         base_tex: Base TeX file with \input commands
#         output_tex: Output compiled TeX file
#         verbose: Print progress
#         dark_mode: Enable dark mode (black background, white text)
#         tectonic_mode: Disable incompatible packages for tectonic engine
#
#     Returns:
#         True if successful
#     """
#     if not base_tex.exists():
#         print(f"ERROR: Base file not found: {base_tex}")
#         return False
#
#     if verbose:
#         print(f"Compiling TeX structure: {base_tex}")
#         print(f"Output: {output_tex}")
#         if dark_mode:
#             print(f"Dark mode: enabled")
#         if tectonic_mode:
#             print(f"Tectonic mode: enabled (disabling incompatible packages)")
#
#     # Expand all inputs recursively
#     expanded_content = expand_inputs(base_tex)
#
#     # Prepend signature
#     signature = generate_signature(source_file=base_tex)
#     expanded_content = signature + expanded_content
#
#     # Check for SciTeX citation
#     # Color codes (matching bash scripts)
#     GREEN = "\033[0;32m"
#     YELLOW = "\033[0;33m"
#     NC = "\033[0m"  # No Color
#
#     if (
#         r"\cite{watanabe2025scitex" in expanded_content
#         or r"\citep{watanabe2025scitex" in expanded_content
#         or r"\citet{watanabe2025scitex" in expanded_content
#     ):
#         print(f"{GREEN}{'=' * 78}{NC}")
#         print(f"{GREEN}Thank you for citing SciTeX Writer! 🙏{NC}")
#         print("")
#         print(
#             f"{GREEN}Your support helps maintain this open-source project.{NC}"
#         )
#         print(f"{GREEN}Citation found: \\cite{{{{watanabe2025scitex}}}}{NC}")
#         print(f"{GREEN}{'=' * 78}{NC}")
#         print("")
#     else:
#         print(f"{YELLOW}{'=' * 78}{NC}")
#         print(f"{YELLOW}WARN: SciTeX Writer citation not found!{NC}")
#         print("")
#         print(
#             f"{YELLOW}Please consider citing SciTeX Writer in your manuscript:{NC}"
#         )
#         print("  \\cite{watanabe2025scitex")
#         print("")
#         print(f"{YELLOW}Add this to your bibliography by including:{NC}")
#         print("  00_shared/bib_files/scitex-system.bib")
#         print("")
#         print(
#             f"{YELLOW}Or merge it with your existing bibliography files.{NC}"
#         )
#         print(f"{YELLOW}{'=' * 78}{NC}")
#         print("")
#
#     # Apply tectonic compatibility if enabled
#     if tectonic_mode:
#         # Comment out incompatible packages
#         expanded_content = re.sub(
#             r"(\\usepackage\{[^}]*lineno[^}]*\})",
#             r"% \1  % Disabled for tectonic",
#             expanded_content,
#         )
#         expanded_content = re.sub(
#             r"(\\usepackage\{[^}]*bashful[^}]*\})",
#             r"% \1  % Disabled for tectonic",
#             expanded_content,
#         )
#         # Comment out \linenumbers command
#         expanded_content = re.sub(
#             r"(^\\linenumbers)",
#             r"% \1  % Disabled for tectonic",
#             expanded_content,
#             flags=re.MULTILINE,
#         )
#
#         # Replace \readwordcount{file} with actual file contents
#         # Find all \readwordcount commands
#         def replace_wordcount(match):
#             file_path = match.group(1)
#             try:
#                 # Resolve file path (could be relative or absolute)
#                 if not file_path.startswith("/"):
#                     # Paths starting with ./ are relative to project root, not base_tex
#                     if file_path.startswith("./"):
#                         # Use current working directory as base (should be project root)
#                         full_path = Path(file_path)
#                     else:
#                         # Relative to base_tex directory
#                         full_path = base_tex.parent / file_path
#                 else:
#                     full_path = Path(file_path)
#
#                 # Read the count value
#                 with open(full_path, "r") as f:
#                     count_value = f.read().strip()
#
#                 return count_value
#             except Exception as e:
#                 # If file can't be read, return a placeholder with debug info
#                 return f"??({e})"
#
#         expanded_content = re.sub(
#             r"\\readwordcount\{([^}]+)\}", replace_wordcount, expanded_content
#         )
#
#     # Inject dark mode styling if enabled
#     if dark_mode:
#         # Find \begin{document} and insert dark mode style before it
#         dark_mode_injection = (
#             "\n% Dark mode styling (injected at compile time)\n"
#             "\\input{../00_shared/latex_styles/dark_mode.tex}\n"
#         )
#
#         expanded_content = expanded_content.replace(
#             r"\begin{document}", dark_mode_injection + r"\begin{document}"
#         )
#
#     # Write output
#     try:
#         output_tex.parent.mkdir(parents=True, exist_ok=True)
#         with open(output_tex, "w", encoding="utf-8") as f:
#             f.write(expanded_content)
#
#         if verbose:
#             line_count = len(expanded_content.split("\n"))
#             print(f"✓ Compiled: {line_count} lines")
#             print(f"  Output: {output_tex}")
#
#         return True
#
#     except Exception as e:
#         print(f"ERROR: Failed to write output: {e}")
#         return False
#
#
# def main():
#     """Command-line interface."""
#     import os
#
#     parser = argparse.ArgumentParser(
#         description="Compile TeX structure by expanding \\input{} commands"
#     )
#     parser.add_argument("base_tex", type=Path, help="Base TeX file")
#     parser.add_argument(
#         "output_tex", type=Path, help="Output compiled TeX file"
#     )
#     parser.add_argument(
#         "-q", "--quiet", action="store_true", help="Quiet mode"
#     )
#     parser.add_argument(
#         "--dark-mode",
#         action="store_true",
#         help="Enable dark mode (black background, white text)",
#     )
#     parser.add_argument(
#         "--tectonic-mode",
#         action="store_true",
#         help="Enable tectonic compatibility (disable incompatible packages)",
#     )
#
#     args = parser.parse_args()
#
#     # Check environment variables if arguments not provided
#     dark_mode = (
#         args.dark_mode
#         or os.getenv("SCITEX_WRITER_DARK_MODE", "false").lower() == "true"
#     )
#     tectonic_mode = (
#         args.tectonic_mode
#         or os.getenv("SCITEX_WRITER_ENGINE", "") == "tectonic"
#         or os.getenv("SCITEX_WRITER_SELECTED_ENGINE", "") == "tectonic"
#     )
#
#     success = compile_tex_structure(
#         base_tex=args.base_tex,
#         output_tex=args.output_tex,
#         verbose=not args.quiet,
#         dark_mode=dark_mode,
#         tectonic_mode=tectonic_mode,
#     )
#
#     exit(0 if success else 1)
#
#
# if __name__ == "__main__":
#     main()
#
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/scitex-writer/scripts/python/compile_tex_structure.py
# --------------------------------------------------------------------------------
