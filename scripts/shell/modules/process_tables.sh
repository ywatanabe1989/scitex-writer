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


function create_table_header() {
    # Create a header/template table when no real tables exist
    local header_file="$SCITEX_WRITER_TABLE_COMPILED_DIR/00_Tables_Header.tex"

    cat >"$header_file" <<'EOF'
% Template table when no actual tables are present
\begin{table}[htbp]
    \centering
      \caption{\textbf{Placeholder table demonstrating the table format for this manuscript template}\\
    \smallskip
    To add tables to your manuscript, place CSV files in \texttt{caption\_and\_media/} with format \texttt{XX\_description.csv}, create matching caption files \texttt{XX\_description.tex}, and reference in text using \texttt{Table\textasciitilde\textbackslash ref\{tab:XX\_description\}}. Example can be seen at \texttt{01\_seizure\_count.csv} with \texttt{01\_seizure\_count.tex}
    }
    \label{tab:0_Tables_Header}
    \begin{tabular}{p{0.3\textwidth}p{0.6\textwidth}}
        \toprule
        \textbf{Step} & \textbf{Instructions} \\
        \midrule
        1. Add CSV & Place file like \texttt{01\_data.csv} in \texttt{caption\_and\_media/} \\
        2. Add Caption & Create \texttt{01\_data.tex} with table caption \\
        3. Compile & Run \texttt{./compile -m} to process tables \\
        4. Reference & Use \texttt{\textbackslash ref\{tab:01\_data\}} in manuscript \\
        \bottomrule
    \end{tabular}
\end{table}
EOF
    echo_info "    Created table header template with instructions"
}

function gather_table_tex_files() {
    # Gather all table tex files into the final compiled file
    output_file="${SCITEX_WRITER_TABLE_COMPILED_FILE}"
    rm -f "$output_file" >/dev/null 2>&1
    echo "% Auto-generated file containing all table inputs" >"$output_file"
    echo "% Generated by gather_table_tex_files()" >>"$output_file"
    echo "" >>"$output_file"

    # First check if there are any real table files.
    # mapfile handles filenames with spaces and avoids the SC2207 array-split pitfall.
    local table_files=()
    mapfile -t table_files < <(find "$SCITEX_WRITER_TABLE_COMPILED_DIR" -maxdepth 1 -name "[0-9]*.tex" 2>/dev/null | grep -v "00_Tables_Header.tex" | sort)
    local has_real_tables=false
    if [ ${#table_files[@]} -gt 0 ]; then
        has_real_tables=true
    fi

    # If no real tables, create the header/template
    if [ "$has_real_tables" = false ]; then
        create_table_header
    fi

    # Count available tables
    table_count=0
    for table_tex in $(find "$SCITEX_WRITER_TABLE_COMPILED_DIR" -maxdepth 1 -name "[0-9]*.tex" 2>/dev/null | sort); do
        if [ -f "$table_tex" ] || [ -L "$table_tex" ]; then
            # Skip header if we have real tables
            local basename
            basename=$(basename "$table_tex")
            if [[ "$basename" == "00_Tables_Header.tex" ]] && [ "$has_real_tables" = true ]; then
                continue
            fi

            # For header template when no real tables exist
            if [[ "$basename" == "00_Tables_Header.tex" ]] && [ "$has_real_tables" = false ]; then
                echo "\\input{$table_tex}" >>"$output_file"
            else
                # For real tables: write a number-keyed PLACEABLE copy so the
                # author can drop \scitextab{<number>} in the body (controlled
                # inline placement), and emit the end-block input GUARDED so a
                # table placed inline is not also duplicated here. Unplaced
                # tables still collect at the end (default behaviour).
                local _tbl_base="${basename%.tex}"
                local _tbl_num="${_tbl_base%%_*}"
                local _tbl_placeable_dir="$SCITEX_WRITER_TABLE_COMPILED_DIR/_placeable"
                mkdir -p "$_tbl_placeable_dir" 2>/dev/null
                cp -f "$table_tex" "$_tbl_placeable_dir/${_tbl_num}.tex"
                echo "% Table from: $basename" >>"$output_file"
                echo "\\ifcsname scitextabplaced@${_tbl_num}\\endcsname\\else\\input{$table_tex}\\fi" >>"$output_file"
            fi
            echo "" >>"$output_file"
            table_count=$((table_count + 1))
        fi
    done

    if [ $table_count -eq 0 ]; then
        echo_warning "    No tables were found to compile."
        echo_warning "    → Fix: place \`XX_name.csv\` (data) + \`XX_name.tex\` (caption) in"
        echo_warning "           \`$SCITEX_WRITER_TABLE_CAPTION_MEDIA_DIR\`."
        echo_warning "    → Why: tables rendered at compile time from CSV are chain-verifiable;"
        echo_warning "           inline \\begin{table} blocks are NOT (data is invisible to Clew)."
    else
        echo_success "    $table_count tables compiled"
    fi
}

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
