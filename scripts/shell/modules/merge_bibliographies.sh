#!/bin/bash
# -*- coding: utf-8 -*-
# ROLE: engine-vendored — DO NOT edit here. `scitex-writer update-project`
# overwrites this file on every re-vendor; fix it upstream in the
# scitex-writer package instead (local edits are lost, and update-project
# may set it read-only in the consumer workspace after vendoring).
# Timestamp: "2025-11-10 00:00:00 (ywatanabe)"
# File: ./scripts/shell/modules/merge_bibliographies.sh

# ============================================================================
# Merge Multiple Bibliography Files
# ============================================================================
# This script checks if multiple .bib files exist in 00_shared/bib_files/
# and merges them into a single bibliography.bib file with deduplication.
#
# Features:
# - Smart deduplication by DOI and title+year
# - Hash-based caching (skips merge if files unchanged)
# - Automatic during compilation
#
# Usage:
#   source ./scripts/shell/modules/merge_bibliographies.sh
# ============================================================================

BIB_DIR="./00_shared/bib_files"
BIB_OUTPUT="bibliography.bib"
MERGE_SCRIPT="./scripts/python/merge_bibliographies.py"

# Count EVERY .bib file, the output included. The merge used to be skipped when
# bibliography.bib was the only one -- but a repeated cite key INSIDE it (e.g.
# scholar appended a stub for a key the author already had) is exactly what makes
# bibtex emit "Repeated entry ... I'm skipping whatever remains of this entry",
# drop the reference, and exit non-zero. Skipping the merge in that case is what
# let the duplicate reach bibtex at all, so: if there is any .bib, de-duplicate it.
bib_file_count=$(find "$BIB_DIR" -maxdepth 1 -name "*.bib" -type f 2>/dev/null | wc -l)

if [ "$bib_file_count" -gt 0 ]; then
    if [ -f "$MERGE_SCRIPT" ]; then
        # --include-output: bibliography.bib is CONSUMER-OWNED (the manuscript
        # cites it via the contents/ symlink), so it is merged as an INPUT.
        # Without this the merge regenerates it from the OTHER .bib files only
        # and silently destroys every entry that lived just in bibliography.bib.
        python3 "$MERGE_SCRIPT" "$BIB_DIR" -o "$BIB_OUTPUT" --include-output -q
    else
        echo_warning "Bibliography files found but merge script missing: $MERGE_SCRIPT"
        echo_warning "Skipping bibliography merge"
    fi
else
    echo_warning "No bibliography files found in $BIB_DIR"
    echo_warning "→ Fix: place a \`bibliography.bib\` in \`$BIB_DIR\`,"
    echo_warning "       or drop multiple \`*.bib\` files in that directory to be auto-merged."
    echo_warning "→ Why: without a bib file, \\cite{...} keys in the manuscript cannot resolve"
    echo_warning "       and scitex-scholar cannot run verification."
fi

# ============================================================================
# Bib freshness guard
# ============================================================================
# Force a bibtex rerun when a source .bib is newer than the compiled .bbl.
# Under latexmk -output-directory + custom BIBINPUTS, a source-only .bib edit
# can leave the .bbl/.fdb_latexmk looking up-to-date, so bibtex is skipped and
# the PDF ships with the OLD bibliography (silent wrong output). Clearing the
# stale .bbl (and latexmk's fdb) forces regeneration. Confirmed on neurovista's
# manuscript. Safe: worst case is one extra bibtex pass.
if [ -n "${LOG_DIR:-}" ] && [ -n "${SCITEX_WRITER_DOC_TYPE:-}" ]; then
    _bbl="${LOG_DIR}/${SCITEX_WRITER_DOC_TYPE}.bbl"
    if [ -f "$_bbl" ]; then
        for _bib in "$BIB_DIR"/*.bib ./"$BIB_OUTPUT"; do
            [ -f "$_bib" ] || continue
            if [ "$_bib" -nt "$_bbl" ]; then
                echo_info "Source bib $_bib newer than $_bbl → clearing stale .bbl to force bibtex"
                rm -f "$_bbl" "${LOG_DIR}/${SCITEX_WRITER_DOC_TYPE}.fdb_latexmk"
                break
            fi
        done
    fi
fi

# EOF
