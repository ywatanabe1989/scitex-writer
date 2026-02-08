#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: 2026-02-09
# File: scripts/shell/check_project.sh
# Purpose: Validate project structure, naming conventions, and references before compilation
# Usage: check_project.sh [-h|--help]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
DIM='\033[0;90m'
BOLD='\033[1m'
NC='\033[0m'

# Counters
PASS_COUNT=0
WARN_COUNT=0
FAIL_COUNT=0

# Help
if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
    echo "Usage: $(basename "$0") [-h|--help]"
    echo ""
    echo "Validate project structure and naming conventions before compilation."
    echo ""
    echo "Checks:"
    echo "  1. Required content files exist"
    echo "  2. Figure naming conventions (must start with [0-9]+_)"
    echo "  3. Table naming conventions (must start with [0-9]+_)"
    printf "  4. Caption content (\\\\caption{} required)\n"
    echo "  5. Bibliography files"
    printf "  6. Cross-references (\\\\ref{fig:*}, \\\\ref{tab:*})\n"
    echo ""
    echo "Naming Rules:"
    echo "  Figures:  01_name.{jpg,png,tif,svg,...} + 01_name.tex (caption)"
    echo "  Panels:   01a_name.jpg (NO caption file for panels)"
    echo "  Tables:   01_name.csv + 01_name.tex (caption)"
    echo "  Bibtex:   00_shared/bib_files/*.bib (bibliography.bib is reserved)"
    exit 0
fi

cd "$PROJECT_ROOT"

# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
log_pass() {
    echo -e "  ${GREEN}[PASS]${NC} $1"
    PASS_COUNT=$((PASS_COUNT + 1))
}

log_warn() {
    echo -e "  ${YELLOW}[WARN]${NC} $1"
    WARN_COUNT=$((WARN_COUNT + 1))
}

log_fail() {
    echo -e "  ${RED}[FAIL]${NC} $1"
    FAIL_COUNT=$((FAIL_COUNT + 1))
}

log_detail() {
    echo -e "    ${DIM}$1${NC}"
}

# --------------------------------------------------------------------------
# 1. Required content files
# --------------------------------------------------------------------------
check_required_files() {
    local issues=()

    local shared_files=(
        "00_shared/title.tex"
        "00_shared/authors.tex"
        "00_shared/keywords.tex"
        "00_shared/journal_name.tex"
    )

    local manuscript_files=(
        "01_manuscript/base.tex"
        "01_manuscript/contents/abstract.tex"
        "01_manuscript/contents/introduction.tex"
        "01_manuscript/contents/methods.tex"
        "01_manuscript/contents/results.tex"
        "01_manuscript/contents/discussion.tex"
    )

    for f in "${shared_files[@]}" "${manuscript_files[@]}"; do
        if [ ! -f "$f" ]; then
            issues+=("missing: $f")
        fi
    done

    if [ ${#issues[@]} -eq 0 ]; then
        log_pass "Required content files"
    else
        log_fail "Required content files"
        for i in "${issues[@]}"; do
            log_detail "$i"
        done
    fi
}

# --------------------------------------------------------------------------
# 2. Figure naming validation
# --------------------------------------------------------------------------
check_figures() {
    local doc_dir="$1"
    local doc_label="$2"
    local fig_dir="$doc_dir/contents/figures/caption_and_media"

    if [ ! -d "$fig_dir" ]; then
        log_pass "Figure naming ($doc_label) - no figures directory"
        return
    fi

    local issues=()
    local media_exts="tif tiff jpg jpeg png svg mmd pptx pdf"

    # Check media files that DON'T match required pattern
    for f in "$fig_dir"/*; do
        [ -e "$f" ] || continue
        [ -d "$f" ] && continue # skip directories
        local fname
        fname=$(basename "$f")
        local ext="${fname##*.}"

        # Skip .tex files (checked separately), hidden files, templates
        [[ "$fname" == *.tex ]] && continue
        [[ "$fname" == .* ]] && continue
        [[ "$fname" == templates ]] && continue

        # Check if extension is a media type
        local is_media=false
        for mext in $media_exts; do
            [[ "$ext" == "$mext" ]] && is_media=true && break
        done
        $is_media || continue

        # Must start with digits
        if ! [[ "$fname" =~ ^[0-9] ]]; then
            issues+=("$fname: does not start with digits (will be ignored by compilation)")
        fi
    done

    # Check main figures have caption files (skip panels)
    for f in "$fig_dir"/[0-9]*; do
        [ -e "$f" ] || continue
        [ -d "$f" ] && continue
        local fname
        fname=$(basename "$f")
        local ext="${fname##*.}"
        [[ "$ext" == "tex" ]] && continue

        local is_media=false
        for mext in $media_exts; do
            [[ "$ext" == "$mext" ]] && is_media=true && break
        done
        $is_media || continue

        local base="${fname%.*}"

        # Skip panels (they must NOT have captions)
        if [[ "$base" =~ ^[0-9]+[a-zA-Z]_ ]]; then
            # Check if panel incorrectly has a caption
            if [ -f "$fig_dir/${base}.tex" ]; then
                issues+=("$base.tex: panel caption file (will be auto-deleted during compilation)")
            fi
            continue
        fi

        # Main figure: must have caption
        if [ ! -f "$fig_dir/${base}.tex" ]; then
            issues+=("$fname: missing caption file ${base}.tex")
        fi
    done

    # Check for orphaned caption files (tex with no media)
    for f in "$fig_dir"/[0-9]*.tex; do
        [ -e "$f" ] || continue
        local fname
        fname=$(basename "$f")
        local base="${fname%.tex}"

        # Skip panel patterns
        [[ "$base" =~ ^[0-9]+[a-zA-Z]_ ]] && continue

        local has_media=false
        for mext in $media_exts; do
            [ -f "$fig_dir/${base}.${mext}" ] && has_media=true && break
        done

        if ! $has_media; then
            issues+=("$fname: orphaned caption (no matching media file)")
        fi
    done

    if [ ${#issues[@]} -eq 0 ]; then
        log_pass "Figure naming ($doc_label)"
    else
        log_warn "Figure naming ($doc_label)"
        for i in "${issues[@]}"; do
            log_detail "$i"
        done
    fi
}

# --------------------------------------------------------------------------
# 3. Table naming validation
# --------------------------------------------------------------------------
check_tables() {
    local doc_dir="$1"
    local doc_label="$2"
    local tbl_dir="$doc_dir/contents/tables/caption_and_media"

    if [ ! -d "$tbl_dir" ]; then
        log_pass "Table naming ($doc_label) - no tables directory"
        return
    fi

    local issues=()

    # Check CSV/XLSX files that DON'T match required pattern
    for f in "$tbl_dir"/*.{csv,xlsx,xls}; do
        [ -e "$f" ] || continue
        local fname
        fname=$(basename "$f")

        if ! [[ "$fname" =~ ^[0-9] ]]; then
            issues+=("$fname: does not start with digits (will be ignored by compilation)")
        fi
    done

    # Check data files have caption files
    for f in "$tbl_dir"/[0-9]*.{csv,xlsx,xls}; do
        [ -e "$f" ] || continue
        local fname
        fname=$(basename "$f")
        local base="${fname%.*}"

        if [ ! -f "$tbl_dir/${base}.tex" ]; then
            issues+=("$fname: missing caption file ${base}.tex")
        fi
    done

    # Check for orphaned caption files
    for f in "$tbl_dir"/[0-9]*.tex; do
        [ -e "$f" ] || continue
        local fname
        fname=$(basename "$f")
        local base="${fname%.tex}"

        local has_data=false
        for dext in csv xlsx xls; do
            [ -f "$tbl_dir/${base}.${dext}" ] && has_data=true && break
        done

        if ! $has_data; then
            issues+=("$fname: orphaned caption (no matching CSV/XLSX)")
        fi
    done

    if [ ${#issues[@]} -eq 0 ]; then
        log_pass "Table naming ($doc_label)"
    else
        log_warn "Table naming ($doc_label)"
        for i in "${issues[@]}"; do
            log_detail "$i"
        done
    fi
}

# --------------------------------------------------------------------------
# 4. Caption content validation
# --------------------------------------------------------------------------
check_captions() {
    local doc_dir="$1"
    local doc_label="$2"
    local issues=()

    # Figure captions
    local fig_dir="$doc_dir/contents/figures/caption_and_media"
    if [ -d "$fig_dir" ]; then
        for f in "$fig_dir"/[0-9]*.tex; do
            [ -e "$f" ] || continue
            local fname
            fname=$(basename "$f")
            local base="${fname%.tex}"
            # Skip panels
            [[ "$base" =~ ^[0-9]+[a-zA-Z]_ ]] && continue

            if ! grep -q '\\caption{' "$f" 2>/dev/null; then
                issues+=("figures/$fname: missing \\caption{}")
            fi
        done
    fi

    # Table captions
    local tbl_dir="$doc_dir/contents/tables/caption_and_media"
    if [ -d "$tbl_dir" ]; then
        for f in "$tbl_dir"/[0-9]*.tex; do
            [ -e "$f" ] || continue
            local fname
            fname=$(basename "$f")

            if ! grep -q '\\caption{' "$f" 2>/dev/null; then
                issues+=("tables/$fname: missing \\caption{}")
            fi
        done
    fi

    if [ ${#issues[@]} -eq 0 ]; then
        log_pass "Caption content ($doc_label)"
    else
        log_warn "Caption content ($doc_label)"
        for i in "${issues[@]}"; do
            log_detail "$i"
        done
    fi
}

# --------------------------------------------------------------------------
# 5. Bibliography validation
# --------------------------------------------------------------------------
check_bibliography() {
    local bib_dir="00_shared/bib_files"
    local issues=()

    if [ ! -d "$bib_dir" ]; then
        log_fail "Bibliography files"
        log_detail "directory not found: $bib_dir"
        return
    fi

    # Count non-reserved bib files
    local source_count=0
    for f in "$bib_dir"/*.bib; do
        [ -e "$f" ] || continue
        local fname
        fname=$(basename "$f")
        [[ "$fname" == "bibliography.bib" ]] && continue
        [[ "$fname" == "merged_all.bib" ]] && continue
        [[ "$fname" == "enriched_all.bib" ]] && continue
        [[ "$fname" == "enriched_all_v2.bib" ]] && continue
        source_count=$((source_count + 1))
    done

    local total_bib=0
    for f in "$bib_dir"/*.bib; do
        [ -e "$f" ] || continue
        total_bib=$((total_bib + 1))
    done

    if [ "$total_bib" -eq 0 ]; then
        issues+=("no .bib files found in $bib_dir")
    elif [ "$source_count" -eq 0 ] && [ -f "$bib_dir/bibliography.bib" ]; then
        # Only bibliography.bib exists - that's fine for a template or simple project
        :
    fi

    if [ ${#issues[@]} -eq 0 ]; then
        log_pass "Bibliography files ($total_bib file(s))"
    else
        log_fail "Bibliography files"
        for i in "${issues[@]}"; do
            log_detail "$i"
        done
    fi
}

# --------------------------------------------------------------------------
# 6. Cross-reference check
# --------------------------------------------------------------------------
check_crossrefs() {
    local doc_dir="$1"
    local doc_label="$2"
    local content_dir="$doc_dir/contents"
    local issues=()

    if [ ! -d "$content_dir" ]; then
        log_pass "Cross-references ($doc_label) - no contents"
        return
    fi

    # Collect existing figure IDs
    local fig_ids=()
    local fig_dir="$content_dir/figures/caption_and_media"
    if [ -d "$fig_dir" ]; then
        for f in "$fig_dir"/[0-9]*.tex; do
            [ -e "$f" ] || continue
            local base
            base=$(basename "$f" .tex)
            [[ "$base" =~ ^[0-9]+[a-zA-Z]_ ]] && continue
            fig_ids+=("$base")
        done
    fi

    # Collect existing table IDs
    local tab_ids=()
    local tbl_dir="$content_dir/tables/caption_and_media"
    if [ -d "$tbl_dir" ]; then
        for f in "$tbl_dir"/[0-9]*.tex; do
            [ -e "$f" ] || continue
            local base
            base=$(basename "$f" .tex)
            tab_ids+=("$base")
        done
    fi

    # Scan content .tex files for references
    for tex_file in "$content_dir"/*.tex; do
        [ -e "$tex_file" ] || continue
        local fname
        fname=$(basename "$tex_file")

        # Check figure references
        while IFS= read -r ref; do
            local found=false
            for fid in "${fig_ids[@]:-}"; do
                [[ "$fid" == "$ref" ]] && found=true && break
            done
            if ! $found; then
                issues+=("$fname: \\ref{fig:$ref} - no matching figure")
            fi
        done < <(grep -oP '\\ref\{fig:([^}]+)\}' "$tex_file" 2>/dev/null | sed 's/\\ref{fig://;s/}//' || true)

        # Check table references
        while IFS= read -r ref; do
            local found=false
            for tid in "${tab_ids[@]:-}"; do
                [[ "$tid" == "$ref" ]] && found=true && break
            done
            if ! $found; then
                issues+=("$fname: \\ref{tab:$ref} - no matching table")
            fi
        done < <(grep -oP '\\ref\{tab:([^}]+)\}' "$tex_file" 2>/dev/null | sed 's/\\ref{tab://;s/}//' || true)
    done

    if [ ${#issues[@]} -eq 0 ]; then
        log_pass "Cross-references ($doc_label)"
    else
        log_warn "Cross-references ($doc_label)"
        for i in "${issues[@]}"; do
            log_detail "$i"
        done
    fi
}

# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
echo ""
echo -e "${CYAN}${BOLD}=== SciTeX Writer: Project Check ===${NC}"
echo ""

check_required_files

# Check each document type
for doc_dir in 01_manuscript 02_supplementary; do
    doc_label="${doc_dir#[0-9]*_}"
    if [ -d "$doc_dir/contents" ]; then
        check_figures "$doc_dir" "$doc_label"
        check_tables "$doc_dir" "$doc_label"
        check_captions "$doc_dir" "$doc_label"
        check_crossrefs "$doc_dir" "$doc_label"
    fi
done

check_bibliography

# Summary
echo ""
echo -e "${BOLD}Summary:${NC} ${GREEN}${PASS_COUNT} passed${NC}, ${YELLOW}${WARN_COUNT} warnings${NC}, ${RED}${FAIL_COUNT} errors${NC}"

if [ "$FAIL_COUNT" -gt 0 ]; then
    echo ""
    echo -e "${RED}Fix errors before compilation.${NC}"
    exit 1
elif [ "$WARN_COUNT" -gt 0 ]; then
    echo ""
    echo -e "${YELLOW}Warnings may cause issues during compilation.${NC}"
    exit 0
else
    echo ""
    echo -e "${GREEN}All checks passed.${NC}"
    exit 0
fi

###% EOF
