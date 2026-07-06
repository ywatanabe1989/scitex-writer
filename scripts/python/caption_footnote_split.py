#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: scripts/python/caption_footnote_split.py
# Purpose: Turn an author-declared \captionfootnote{...} marker inside a figure
#          caption body into the blessed footnote-in-caption LaTeX split.
#
#          A \footnote inside a float (figure*/table*) does NOT render -- the
#          caption argument is reprocessed and the footnote is lost/fatal. The
#          blessed pattern is:
#
#              \caption[short]{long\protect\footnotemark}   % inside the float
#              \footnotetext{...}                            % AFTER \end{figure*}
#
#          So an author writes their caption body with an inline marker:
#
#              \caption{\textbf{Title}\\ Legend text.\captionfootnote{Disclosure.}}
#
#          and the figure float-wrapper (process_figures_modules/04_compilation.src)
#          feeds the caption body through this helper. This helper:
#            - rewrites the FIRST \captionfootnote{...} to \protect\footnotemark
#              (brace-matched, so nested braces inside the disclosure are kept), and
#            - reports the extracted disclosure text so the caller can emit
#              \footnotetext{...} immediately after the float closes.
#
#          No marker -> the caption body is returned byte-for-byte unchanged and
#          no footnote text is reported, so a default manuscript is unaffected.
#
#          \captionfootnote is a COMPILE-TIME marker only: it is stripped here and
#          never reaches LaTeX, so no preamble macro definition is required.
#
# Usage (from the shell assembler):
#   printf '%s' "$caption_body" | \
#     python3 caption_footnote_split.py --footnote-out /path/to/footnote.txt
#   # stdout = transformed caption body
#   # footnote.txt = disclosure text (only written when a marker was found)
#
# Self-contained: stdlib only.

import argparse
import sys
from pathlib import Path

_MARKER = r"\captionfootnote"
_REPLACEMENT = r"\protect\footnotemark"


def split_caption_footnote(text):
    r"""Split a caption body into (transformed_caption, footnote_text).

    Finds the FIRST ``\captionfootnote{...}`` marker (brace-matched, honoring
    escaped braces), replaces it in place with ``\protect\footnotemark``, and
    returns the extracted inner text (stripped). When no valid marker is present
    the input is returned unchanged and ``footnote_text`` is ``None``.
    """
    idx = text.find(_MARKER)
    if idx == -1:
        return text, None

    i = idx + len(_MARKER)
    n = len(text)
    # Allow whitespace between the marker and its brace.
    while i < n and text[i] in " \t\r\n":
        i += 1
    if i >= n or text[i] != "{":
        # Not a well-formed \captionfootnote{...} call -- leave untouched.
        return text, None

    start = i + 1
    depth = 1
    j = start
    while j < n and depth:
        ch = text[j]
        if ch == "\\":
            j += 2  # skip an escaped char (incl. \{ \} \\)
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                break
        j += 1
    if depth != 0:
        # Unbalanced braces -- leave untouched rather than corrupt the caption.
        return text, None

    footnote = text[start:j]
    transformed = text[:idx] + _REPLACEMENT + text[j + 1 :]
    return transformed, footnote.strip()


def main():
    parser = argparse.ArgumentParser(
        description="Rewrite a \\captionfootnote{...} marker in a caption body to "
        "\\protect\\footnotemark and report the disclosure text."
    )
    parser.add_argument(
        "--footnote-out",
        help="Path to write the extracted footnote text (only written when a "
        "marker is found).",
    )
    args = parser.parse_args()

    text = sys.stdin.read()
    transformed, footnote = split_caption_footnote(text)

    sys.stdout.write(transformed)

    if args.footnote_out and footnote:
        Path(args.footnote_out).write_text(footnote, encoding="utf-8")

    return 0


if __name__ == "__main__":
    sys.exit(main())
