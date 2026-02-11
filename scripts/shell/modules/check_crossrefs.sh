#!/bin/bash
# -*- coding: utf-8 -*-
# File: scripts/shell/modules/check_crossrefs.sh
# Purpose: Cross-reference validation for check_project.sh
# Sourced by check_project.sh - requires log_pass, log_warn, log_detail functions

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

###% EOF
