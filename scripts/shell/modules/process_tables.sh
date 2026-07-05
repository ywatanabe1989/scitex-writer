#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2026-01-19 02:59:33 (ywatanabe)"
# File: ./scripts/shell/modules/process_tables.sh

# Literal LaTeX backslashes are written via "\\…" in echo throughout this
# module; SC2028's "echo may not expand escape sequences" is a false positive
# for that pattern here.
# shellcheck disable=SC2028
# shellcheck disable=SC2034  # ORIG_DIR exported from standard module header
ORIG_DIR="$(pwd)"
THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_PATH="$THIS_DIR/.$(basename "$0").log"
echo >"$LOG_PATH"

# shellcheck disable=SC2034  # GIT_ROOT exported from standard module header
GIT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"

GRAY='\033[0;90m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo_info() { echo -e "${GRAY}INFO: $1${NC}"; }
echo_success() { echo -e "${GREEN}SUCC: $1${NC}"; }
echo_warning() { echo -e "${YELLOW}WARN: $1${NC}"; }
echo_error() { echo -e "${RED}ERRO: $1${NC}"; }
echo_header() { echo_info "=== $1 ==="; }
# ---------------------------------------

# Quick check for --no_tables BEFORE expensive config loading
NO_TABLES_ARG="${1:-false}"
if [ "$NO_TABLES_ARG" = true ]; then
    echo -e "\033[0;90mINFO: Running $0 ...\033[0m"
    echo -e "\033[0;90mINFO:     Skipping all table processing (--no_tables specified)\033[0m"
    exit 0
fi

log_info() {
    if [ "${SCITEX_LOG_LEVEL:-1}" -ge 2 ]; then
        echo -e "  \033[0;90m→ $1\033[0m"
    fi
}

# Timestamp tracking for table processing
TABLE_STAGE_START=0
log_table_stage_start() {
    TABLE_STAGE_START=$(date +%s)
    local timestamp
    timestamp=$(date '+%H:%M:%S')
    echo_info "  [$timestamp] $1"
}

log_table_stage_end() {
    local end
    end=$(date +%s)
    local elapsed
    elapsed=$((end - TABLE_STAGE_START))
    local timestamp
    timestamp=$(date '+%H:%M:%S')
    echo_success "  [$timestamp] $1 (${elapsed}s)"
}

# Configurations
# shellcheck source=/dev/null
source ./config/load_config.sh "$SCITEX_WRITER_DOC_TYPE"

# Logging
touch "$LOG_PATH" >/dev/null 2>&1
echo
log_info "Running $0 ..."

function init_tables() {
    # Cleanup and prepare directories
    rm -f "$SCITEX_WRITER_TABLE_COMPILED_DIR"/*.tex
    mkdir -p "$SCITEX_WRITER_TABLE_DIR" >/dev/null
    mkdir -p "$SCITEX_WRITER_TABLE_CAPTION_MEDIA_DIR" >/dev/null
    mkdir -p "$SCITEX_WRITER_TABLE_COMPILED_DIR" >/dev/null
    echo >"$SCITEX_WRITER_TABLE_COMPILED_FILE"
}

function xlsx2csv_convert() {
    # Convert Excel files to CSV if xlsx2csv is available
    if command -v xlsx2csv >/dev/null 2>&1; then
        for xlsx_file in "$SCITEX_WRITER_TABLE_CAPTION_MEDIA_DIR"/[0-9]*.{xlsx,xls}; do
            [ -e "$xlsx_file" ] || continue

            base_name=$(basename "$xlsx_file" | sed 's/\.\(xlsx\|xls\)$//')
            csv_file="${SCITEX_WRITER_TABLE_CAPTION_MEDIA_DIR}/${base_name}.csv"

            # Convert only if CSV doesn't exist or is older than Excel file
            if [ ! -f "$csv_file" ] || [ "$xlsx_file" -nt "$csv_file" ]; then
                echo_info "    Converting $xlsx_file to CSV..."
                if xlsx2csv "$xlsx_file" "$csv_file"; then
                    echo_success "    Created $csv_file from Excel"
                else
                    echo_warning "    Failed to convert $xlsx_file"
                fi
            fi
        done
    fi
}

function ensure_caption() {
    # Create default captions for any table without one
    for csv_file in "$SCITEX_WRITER_TABLE_CAPTION_MEDIA_DIR"/[0-9]*.csv; do
        [ -e "$csv_file" ] || continue
        local base_name
        base_name=$(basename "$csv_file" .csv)
        # Extract table number from filename like 01_seizure_count
        local table_number=""
        if [[ "$base_name" =~ ^([0-9]+)_ ]]; then
            table_number="${BASH_REMATCH[1]}"
        else
            table_number="$base_name"
        fi
        local caption_file="${SCITEX_WRITER_TABLE_CAPTION_MEDIA_DIR}/${base_name}.tex"

        if [ ! -f "$caption_file" ] && [ ! -L "$caption_file" ]; then
            echo_info "    Creating default caption for table $base_name"
            mkdir -p "$(dirname "$caption_file")"
            local rel_path="${caption_file#./}"
            local escaped_path="${rel_path//_/\\_}"
            cat >"$caption_file" <<EOF
%% Edit this file: $rel_path
\\caption{\\textbf{TABLE TITLE HERE}\\\\
\\smallskip
TABLE CAPTION HERE. Edit this caption at \\texttt{$escaped_path}.
}
EOF
        fi
    done
}

# Function removed - no longer needed for new naming convention

function check_csv_for_special_chars() {
    # Check CSV file for potential problematic characters
    local csv_file="$1"
    local problem_chars="[&%$#_{}^~\\|<>]"
    local problems
    problems=$(grep -n "$problem_chars" "$csv_file" 2>/dev/null || echo "")
    if [ -n "$problems" ]; then
        echo_warn "    Potential LaTeX special characters found in $csv_file:"
        echo -e "${YELLOW}"
        echo "$problems" | head -5
        echo "These may need proper LaTeX escaping."
        echo -e "${NC}"
    fi
}

# --- CSV->TeX generation functions (extracted module) ---
source "$THIS_DIR/process_tables_modules/03_csv2tex.src"


# --- Table gather / final-assembly functions (extracted module) ---
# create_table_header + gather_table_tex_files. Extracted so the no-tables
# fallback (no stray placeholder "Table") is unit-testable in isolation.
source "$THIS_DIR/process_tables_modules/04_gather.src"

# Main execution
log_table_stage_start "Initializing tables"
init_tables
log_table_stage_end "Initializing tables"

log_table_stage_start "Converting XLSX to CSV"
xlsx2csv_convert # Convert Excel files to CSV first
log_table_stage_end "Converting XLSX to CSV"

log_table_stage_start "Ensuring captions exist"
ensure_caption
log_table_stage_end "Ensuring captions exist"

log_table_stage_start "Converting CSV to LaTeX"
csv2tex
log_table_stage_end "Converting CSV to LaTeX"

log_table_stage_start "Gathering table files"
gather_table_tex_files
log_table_stage_end "Gathering table files"

# EOF
