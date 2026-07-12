#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_utils/_caption_footnote.py

r"""Split an author-declared ``\captionfootnote{...}`` out of a caption body.

Absorbs ``scripts/python/caption_footnote_split.py`` into the package: the shell
figure assembler shelled out to it through a ``mktemp`` file per figure
(``printf | python3 helper --footnote-out /tmp/...``); the Python pipeline calls
this function directly.

A ``\footnote`` inside a float (``figure*``/``table*``) does NOT render -- the
caption argument is reprocessed and the footnote is lost or fatal. The blessed
split is::

    \caption[short]{long\protect\footnotemark}   % inside the float
    \footnotetext{...}                            % AFTER \end{figure*}

So an author writes the marker inline::

    \caption{\textbf{Title}\\ Legend.\captionfootnote{Funding disclosure.}}

and the pipeline feeds the caption body through :func:`split_caption_footnote`,
which rewrites the marker to ``\protect\footnotemark`` and hands back the
disclosure text for a ``\footnotetext`` emitted right after the float closes.

``\captionfootnote`` is a COMPILE-TIME marker only -- it is stripped here and
never reaches LaTeX, so no preamble macro is needed. With no marker the body is
returned byte-for-byte unchanged, so default manuscripts are unaffected.
"""

from __future__ import annotations

from typing import Optional, Tuple

MARKER = r"\captionfootnote"
REPLACEMENT = r"\protect\footnotemark"


def split_caption_footnote(text: str) -> Tuple[str, Optional[str]]:
    r"""Return ``(caption_body, footnote_text)`` for one caption body.

    Finds the FIRST ``\captionfootnote{...}`` (brace-matched, honoring escaped
    braces), replaces it in place with ``\protect\footnotemark``, and returns the
    stripped inner text. A missing or unbalanced marker leaves the body unchanged
    and reports ``None`` -- corrupting a caption is worse than ignoring a
    malformed marker, which the caption-footnote check flags separately.
    """
    start_marker = text.find(MARKER)
    if start_marker == -1:
        return text, None

    cursor = start_marker + len(MARKER)
    length = len(text)
    while cursor < length and text[cursor] in " \t\r\n":
        cursor += 1
    if cursor >= length or text[cursor] != "{":
        return text, None

    inner_start = cursor + 1
    depth = 1
    cursor = inner_start
    while cursor < length and depth:
        char = text[cursor]
        if char == "\\":
            cursor += 2  # skip an escaped char (incl. \{ \} \\)
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                break
        cursor += 1
    if depth != 0:
        return text, None

    footnote = text[inner_start:cursor].strip()
    body = text[:start_marker] + REPLACEMENT + text[cursor + 1 :]
    return body, footnote


__all__ = ["MARKER", "REPLACEMENT", "split_caption_footnote"]

# EOF
