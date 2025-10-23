#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-27 15:10:53 (ywatanabe)"
# File: ./paper/scripts/shell/compile_revision

ORIG_DIR="$(pwd)"
THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
echo > "$LOG_PATH"

BLACK='\033[0;30m'
LIGHT_GRAY='\033[0;37m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo_info() { echo -e "${LIGHT_GRAY}$1${NC}"; }
echo_success() { echo -e "${GREEN}$1${NC}"; }
echo_warning() { echo -e "${YELLOW}$1${NC}"; }
echo_error() { echo -e "${RED}$1${NC}"; }
# ---------------------------------------

################################################################################
# Description: Compiles revision response document
# Processes reviewer comments and author responses with diff highlighting
################################################################################

# Configurations
export STXW_DOC_TYPE="revision"
source ./config/load_config.sh "$STXW_DOC_TYPE"
echo

# Log
touch $LOG_PATH >/dev/null 2>&1
mkdir -p "$LOG_DIR" && touch "$STXW_GLOBAL_LOG_FILE"

# Shell options
set -e
set -o pipefail

echo -e "${BLUE}INFO: Running compile_revision.sh...${NC}"

# 1. Check dependencies
./scripts/shell/modules/check_dependancy_commands.sh
if [ $? -ne 0 ]; then
    echo -e "${RED}ERRO: Dependency check failed${NC}"
    exit 1
fi

# 2. Check revision structure
echo ""
echo -e "${BLUE}INFO: Checking revision response structure...${NC}"

# Expected structure with simplified naming (allowing optional descriptive suffixes):
# Editor: E_01_comments[_description].tex, E_01_response[_description].tex, ...
# Reviewer1: R1_01_comments[_description].tex, R1_01_response[_description].tex, ...
# Reviewer2: R2_01_comments[_description].tex, R2_01_response[_description].tex, ...
# Examples:
#   E_01_comments_about-methodology.tex
#   R1_02_response_statistical-analysis.tex

check_revision_files() {
    local dir="$1"
    local prefix="$2"  # E, R1, or R2
    local name="$3"    # editor, reviewer1, reviewer2 for display

    if [ ! -d "$dir" ]; then
        echo -e "${YELLOW}WARN: Directory $dir not found${NC}"
        return 1
    fi

    echo -e "${BLUE}  Checking $name responses...${NC}"

    # Check for comment/response pairs with simplified naming (supporting descriptive suffixes)
    local found_files=0
    for comment_file in "$dir"/${prefix}_*_comments*.tex; do
        if [ -f "$comment_file" ]; then
            # Extract the base ID (e.g., E_01, R1_02)
            local base_id=$(echo "$(basename $comment_file)" | sed -E "s/(${prefix}_[0-9]+)_comments.*/\1/")

            # Look for corresponding response file (may have different description)
            local response_found=false
            for response_file in "$dir"/${base_id}_response*.tex; do
                if [ -f "$response_file" ]; then
                    echo -e "${GREEN}    ✓ $(basename $comment_file) & $(basename $response_file)${NC}"
                    found_files=$((found_files + 1))
                    response_found=true
                    break
                fi
            done

            if [ "$response_found" = false ]; then
                echo -e "${YELLOW}    ⚠ Missing response for: $(basename $comment_file)${NC}"
            fi
        fi
    done

    if [ $found_files -eq 0 ]; then
        echo -e "${YELLOW}    No comment/response pairs found in $dir${NC}"
    else
        echo -e "${GREEN}    Found $found_files comment/response pair(s)${NC}"
    fi

    return 0
}

# Check each reviewer directory with simplified prefixes
check_revision_files "./03_revision/contents/editor" "E" "Editor"
check_revision_files "./03_revision/contents/reviewer1" "R1" "Reviewer 1"
check_revision_files "./03_revision/contents/reviewer2" "R2" "Reviewer 2"

# 3. Process figures (minimal for revision)
echo ""
echo -e "${BLUE}INFO: Processing figures...${NC}"
./scripts/shell/modules/process_figures.sh \
    true \
    false \
    false \
    false

# 4. Process tables
echo ""
echo -e "${BLUE}INFO: Processing tables...${NC}"
./scripts/shell/modules/process_tables.sh

# 5. Compile structure
echo ""
echo -e "${BLUE}INFO: Compiling document structure...${NC}"
./scripts/shell/modules/compilation_structure_tex_to_compiled_tex.sh

# 6. Compile to PDF
echo ""
echo -e "${BLUE}INFO: Compiling to PDF...${NC}"
./scripts/shell/modules/compilation_compiled_tex_to_compiled_pdf.sh

# 7. Skip diff generation for revision (revision document already shows changes)
# The revision document itself contains track changes with \DIFadd and \DIFdel commands
echo ""
echo -e "${BLUE}INFO: Skipping diff generation (revision document shows changes inline)${NC}"

# 8. Archive
echo ""
echo -e "${BLUE}INFO: Archiving...${NC}"
./scripts/shell/modules/process_archive.sh

# 9. Cleanup
echo ""
echo -e "${BLUE}INFO: Cleaning up...${NC}"
./scripts/shell/modules/cleanup.sh

echo ""
echo -e "${GREEN}SUCC: ==========================================${NC}"
echo -e "${GREEN}SUCC: Revision compilation completed${NC}"
echo -e "${GREEN}SUCC: PDF: $STXW_COMPILED_PDF${NC}"
echo -e "${GREEN}SUCC: ==========================================${NC}"
