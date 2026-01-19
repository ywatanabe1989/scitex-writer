#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-27 15:20:00 (ywatanabe)"
# File: ./paper/scripts/shell/compile_supplementary.sh

# shellcheck disable=SC1091  # Don't follow sourced files

export ORIG_DIR
ORIG_DIR="$(pwd)"
THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_PATH="$THIS_DIR/.$(basename "$0").log"

# Resolve project root from script location (safe for nested repos)
# Allow override via environment variable for moved projects
PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$THIS_DIR/../.." && pwd)}"
export PROJECT_ROOT

# Change to project root to ensure relative paths work
cd "$PROJECT_ROOT" || exit 1

GRAY='\033[0;90m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BOLD_CYAN='\033[1;36m'
NC='\033[0m' # No Color

echo_info() { echo -e "${GRAY}INFO: $1${NC}"; }
echo_success() { echo -e "${GREEN}SUCC: $1${NC}"; }
echo_warning() { echo -e "${YELLOW}WARN: $1${NC}"; }
echo_error() { echo -e "${RED}ERRO: $1${NC}"; }
echo_header() { echo_info "=== $1 ==="; }
# ---------------------------------------

# Timestamp tracking functions
STAGE_START_TIME=0
COMPILATION_START_TIME=$(date +%s)

log_stage_start() {
    local stage_name="$1"
    STAGE_START_TIME=$(date +%s)
    local timestamp=$(date '+%H:%M:%S')
    echo_info "[$timestamp] Starting: $stage_name"
}

log_stage_end() {
    local stage_name="$1"
    local end_time=$(date +%s)
    local elapsed=$((end_time - STAGE_START_TIME))
    local total_elapsed=$((end_time - COMPILATION_START_TIME))
    local timestamp=$(date '+%H:%M:%S')
    echo_success "[$timestamp] Completed: $stage_name (${elapsed}s elapsed, ${total_elapsed}s total)"
}

# Configurations
export SCITEX_WRITER_DOC_TYPE="supplementary"
source ./config/load_config.sh "$SCITEX_WRITER_DOC_TYPE"
echo

# Log
touch $LOG_PATH >/dev/null 2>&1
mkdir -p "$LOG_DIR" && touch "$SCITEX_WRITER_GLOBAL_LOG_FILE"

# Shell options
set -e
set -o pipefail

# Default values for arguments
do_p2t=false
no_figs=false
no_tables=false
do_verbose=false
do_crop_tif=false
do_force=false
no_diff=false
draft_mode=false
dark_mode=false

usage() {
    echo ""
    echo -e "${BOLD_CYAN}━━━ compile_supplementary.sh ━━━${NC}"
    echo -e "${GRAY}Compile supplementary materials${NC}"
    echo ""
    echo -e "${BOLD_CYAN}━━━ Structure ━━━${NC}"
    echo -e "  ${GREEN}02_supplementary/${NC}"
    echo -e "    contents/"
    echo -e "      ${YELLOW}methods.tex${NC}         ${GRAY}# Supplementary Methods${NC}"
    echo -e "      ${YELLOW}results.tex${NC}         ${GRAY}# Supplementary Results${NC}"
    echo -e "      figures/caption_and_media/  ${GRAY}# Supplementary Figures${NC}"
    echo -e "      tables/caption_and_media/   ${GRAY}# Supplementary Tables${NC}"
    echo -e "    ${GRAY}supplementary.pdf${NC}   ${GRAY}# Output${NC}"
    echo ""
    echo -e "${BOLD_CYAN}━━━ Editable Files ━━━${NC}"
    echo -e "${GREEN}00_shared:${NC}"
    echo -e "  ${GRAY}$PROJECT_ROOT/00_shared/${NC}title.tex"
    echo -e "  ${GRAY}$PROJECT_ROOT/00_shared/${NC}authors.tex"
    echo -e "  ${GRAY}$PROJECT_ROOT/00_shared/${NC}keywords.tex"
    echo -e "  ${GRAY}$PROJECT_ROOT/00_shared/${NC}journal_name.tex"
    echo -e "  ${GRAY}$PROJECT_ROOT/00_shared/bib_files/${NC}*.bib"
    echo ""
    echo -e "${GREEN}02_supplementary:${NC}"
    echo -e "  ${GRAY}$PROJECT_ROOT/02_supplementary/contents/${NC}methods.tex"
    echo -e "  ${GRAY}$PROJECT_ROOT/02_supplementary/contents/${NC}results.tex"
    echo -e "  ${GRAY}$PROJECT_ROOT/02_supplementary/contents/figures/${NC}caption_and_media/"
    echo -e "  ${GRAY}$PROJECT_ROOT/02_supplementary/contents/tables/${NC}caption_and_media/"
    echo ""
    echo -e "${BOLD_CYAN}━━━ Options ━━━${NC}"
    echo "  -nf,  --no_figs       Skip figure processing (~4s faster)"
    echo "  -nt,  --no_tables     Skip table processing (~4s faster)"
    echo "  -nd,  --no_diff       Skip diff generation (~17s faster)"
    echo "  -d,   --draft         Single-pass compilation (~5s faster)"
    echo "  -dm,  --dark_mode     Dark mode: black background, white text"
    echo "  -p2t, --ppt2tif       Convert PowerPoint to TIF (WSL)"
    echo "  -c,   --crop_tif      Crop TIF whitespace"
    echo "  -q,   --quiet         Minimal output"
    echo "  --force               Force full recompilation"
    echo "  -h,   --help          Show this help"
    echo ""
    echo -e "${GRAY}Note: Options accept both hyphens and underscores${NC}"
    echo ""
    echo -e "${BOLD_CYAN}━━━ Document Structure (base.tex) ━━━${NC}"
    echo -e "  ${GRAY}$PROJECT_ROOT/02_supplementary/${NC}base.tex"
    echo -e "  Controls section order via \\\\input{} commands:"
    echo -e "    ${GRAY}\\\\input{./02_supplementary/contents/${NC}authors${GRAY}}${NC}"
    echo -e "    ${GRAY}\\\\input{./02_supplementary/contents/${NC}methods${GRAY}}${NC}"
    echo -e "    ${GRAY}\\\\input{./02_supplementary/contents/${NC}results${GRAY}}${NC}"
    echo -e "  To add/remove sections: edit base.tex \\\\input{} lines"
    echo -e "  Comment out with %% to disable a section"
    echo ""
    echo -e "${BOLD_CYAN}━━━ Adding Figures ━━━${NC}"
    echo -e "  ${GREEN}Location:${NC} ${YELLOW}02_supplementary/contents/figures/caption_and_media/${NC}"
    echo -e "  ${GREEN}Supported:${NC} PNG, JPEG, PDF, SVG, TIFF, Mermaid (.mmd)"
    echo ""
    echo -e "  ${GREEN}Naming Rule:${NC} Prefix with S + 2-digit number for ordering"
    echo -e "    ${YELLOW}S01_my_figure.png${NC}  ${GRAY}# Media file${NC}"
    echo -e "    ${YELLOW}S01_my_figure.tex${NC}  ${GRAY}# Caption file (same base name)${NC}"
    echo ""
    echo -e "  ${GREEN}Caption File Format:${NC}"
    echo -e "    ${GRAY}%% Figure caption${NC}"
    echo -e "    ${GRAY}\\\\caption{Your caption here.}${NC}"
    echo -e "    ${GRAY}\\\\label{fig:supplementary_my_figure_01}${NC}"
    echo ""
    echo -e "  ${GREEN}Citing in Text:${NC} Use ${YELLOW}\\\\ref{fig:supplementary_my_figure_01}${NC}"
    echo ""
    echo -e "${BOLD_CYAN}━━━ Adding Tables ━━━${NC}"
    echo -e "  ${GREEN}Location:${NC} ${YELLOW}02_supplementary/contents/tables/caption_and_media/${NC}"
    echo -e "  ${GREEN}Format:${NC} CSV auto-converts to LaTeX table"
    echo ""
    echo -e "  ${GREEN}Naming Rule:${NC} Prefix with S + 2-digit number for ordering"
    echo -e "    ${YELLOW}S01_my_table.csv${NC}   ${GRAY}# Data file (CSV format)${NC}"
    echo -e "    ${YELLOW}S01_my_table.tex${NC}   ${GRAY}# Caption file (same base name)${NC}"
    echo ""
    echo -e "  ${GREEN}Caption File Format:${NC}"
    echo -e "    ${GRAY}%% Table caption${NC}"
    echo -e "    ${GRAY}\\\\caption{Your caption here.}${NC}"
    echo -e "    ${GRAY}\\\\label{tab:supplementary_my_table_01}${NC}"
    echo ""
    echo -e "  ${GREEN}Citing in Text:${NC} Use ${YELLOW}\\\\ref{tab:supplementary_my_table_01}${NC}"
    echo ""
    echo -e "${BOLD_CYAN}━━━ Managing Bibliography ━━━${NC}"
    echo -e "  Place .bib files in: ${YELLOW}$PROJECT_ROOT/00_shared/bib_files/${NC}"
    echo -e "  Multiple .bib files auto-merge with deduplication"
    echo -e "  Citation style: ${YELLOW}$PROJECT_ROOT/config/config_supplementary.yaml${NC}"
    echo -e "  Styles: ${GREEN}unsrtnat${NC}, ${GREEN}plainnat${NC}, ${GREEN}apalike${NC}, ${GREEN}IEEEtran${NC}, ${GREEN}naturemag${NC}"
    echo ""
    exit 0
}

parse_arguments() {
    while [[ "$#" -gt 0 ]]; do
        # Normalize option: replace underscores with hyphens for matching
        local normalized_opt=$(echo "$1" | tr '_' '-')

        case $normalized_opt in
        -h | --help) usage ;;
        -p2t | --ppt2tif) do_p2t=true ;;
        -nf | --no-figs) no_figs=true ;;
        -nt | --no-tables) no_tables=true ;;
        -nd | --no-diff) no_diff=true ;;
        -d | --draft) draft_mode=true ;;
        -dm | --dark-mode) dark_mode=true ;;
        -c | --crop-tif) do_crop_tif=true ;;
        -v | --verbose) do_verbose=true ;;
        -q | --quiet) do_verbose=false ;;
        --force) do_force=true ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
        esac
        shift
    done
}

main() {
    parse_arguments "$@"

    # Log command options
    options_display=""
    $do_p2t && options_display="${options_display} --ppt2tif"
    $no_figs && options_display="${options_display} --no_figs"
    $no_tables && options_display="${options_display} --no_tables"
    $no_diff && options_display="${options_display} --no_diff"
    $draft_mode && options_display="${options_display} --draft"
    $dark_mode && options_display="${options_display} --dark_mode"
    $do_crop_tif && options_display="${options_display} --crop_tif"
    $do_verbose && options_display="${options_display} --verbose"
    echo_info "Running $0${options_display}..."

    # Verbosity
    export SCITEX_WRITER_VERBOSE_PDFLATEX=$do_verbose
    export SCITEX_WRITER_VERBOSE_BIBTEX=$do_verbose

    # Draft mode (single-pass compilation)
    export SCITEX_WRITER_DRAFT_MODE=$draft_mode

    # Dark mode (black background, white text)
    export SCITEX_WRITER_DARK_MODE=$dark_mode

    # Check dependencies
    log_stage_start "Dependency Check"
    ./scripts/shell/modules/check_dependancy_commands.sh
    log_stage_end "Dependency Check"

    # Merge bibliography files if multiple exist
    log_stage_start "Bibliography Merge"
    ./scripts/shell/modules/merge_bibliographies.sh
    log_stage_end "Bibliography Merge"

    # Apply citation style from config
    log_stage_start "Citation Style"
    ./scripts/shell/modules/apply_citation_style.sh
    log_stage_end "Citation Style"

    # Run independent processing in parallel for speed
    local parallel_start=$(date +%s)
    local timestamp=$(date '+%H:%M:%S')
    echo_info "[$timestamp] Starting: Parallel Processing (Figures, Tables, Word Count)"

    # Create temp files for parallel job outputs
    local temp_dir=$(mktemp -d)
    local fig_log="$temp_dir/figures.log"
    local tbl_log="$temp_dir/tables.log"
    local wrd_log="$temp_dir/words.log"

    # Run all three in parallel
    (
        ./scripts/shell/modules/process_figures.sh "$no_figs" "$do_p2t" "$do_verbose" "$do_crop_tif" >"$fig_log" 2>&1
        echo $? >"$temp_dir/fig_exit"
    ) &
    local fig_pid=$!

    (
        ./scripts/shell/modules/process_tables.sh "$no_tables" >"$tbl_log" 2>&1
        echo $? >"$temp_dir/tbl_exit"
    ) &
    local tbl_pid=$!

    (
        ./scripts/shell/modules/count_words.sh >"$wrd_log" 2>&1
        echo $? >"$temp_dir/wrd_exit"
    ) &
    local wrd_pid=$!

    # Wait for all parallel jobs
    wait $fig_pid $tbl_pid $wrd_pid

    # Display outputs in order
    echo_info "  Figure Processing:"
    cat "$fig_log" | sed 's/^/    /'

    echo_info "  Table Processing:"
    cat "$tbl_log" | sed 's/^/    /'

    echo_info "  Word Count:"
    cat "$wrd_log" | sed 's/^/    /'

    # Check exit codes
    local fig_exit=$(cat "$temp_dir/fig_exit")
    local tbl_exit=$(cat "$temp_dir/tbl_exit")
    local wrd_exit=$(cat "$temp_dir/wrd_exit")

    rm -rf "$temp_dir"

    # Fail if any job failed
    if [ "$fig_exit" -ne 0 ] || [ "$tbl_exit" -ne 0 ] || [ "$wrd_exit" -ne 0 ]; then
        echo_error "Parallel processing failed (fig=$fig_exit, tbl=$tbl_exit, wrd=$wrd_exit)"
        exit 1
    fi

    local parallel_end=$(date +%s)
    local parallel_elapsed=$((parallel_end - parallel_start))
    local total_elapsed=$((parallel_end - COMPILATION_START_TIME))
    timestamp=$(date '+%H:%M:%S')
    echo_success "[$timestamp] Completed: Parallel Processing (${parallel_elapsed}s elapsed, ${total_elapsed}s total)"

    # Compile documents
    log_stage_start "TeX Compilation (Structure)"
    ./scripts/shell/modules/compilation_structure_tex_to_compiled_tex.sh
    log_stage_end "TeX Compilation (Structure)"

    # TeX to PDF
    log_stage_start "PDF Generation"
    ./scripts/shell/modules/compilation_compiled_tex_to_compiled_pdf.sh
    log_stage_end "PDF Generation"

    # Diff (skip if --no_diff specified)
    if [ "$no_diff" = false ]; then
        log_stage_start "Diff Generation"
        ./scripts/shell/modules/process_diff.sh
        log_stage_end "Diff Generation"
    else
        echo_info "Skipping diff generation (--no_diff specified)"
    fi

    # Versioning
    log_stage_start "Archive/Versioning"
    ./scripts/shell/modules/process_archive.sh
    log_stage_end "Archive/Versioning"

    # Cleanup
    log_stage_start "Cleanup"
    ./scripts/shell/modules/cleanup.sh
    log_stage_end "Cleanup"

    # Final steps
    log_stage_start "Directory Tree"
    ./scripts/shell/modules/custom_tree.sh
    log_stage_end "Directory Tree"

    # Logging
    echo

    local final_time=$(date +%s)
    local total_compilation_time=$((final_time - COMPILATION_START_TIME))
    echo_success "===================================================="
    echo_success "TOTAL COMPILATION TIME: ${total_compilation_time}s"
    echo_success "===================================================="
    echo_success "See $SCITEX_WRITER_GLOBAL_LOG_FILE"
}

main "$@" 2>&1 | tee -a "$LOG_PATH" "$SCITEX_WRITER_GLOBAL_LOG_FILE"

# EOF
