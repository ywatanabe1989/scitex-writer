#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-08 06:34:13 (ywatanabe)"
# File: ./config/load_config.sh

ORIG_DIR="$(pwd)"
THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
echo > "$LOG_PATH"

GIT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"

# Load version from pyproject.toml (single source of truth)
PYPROJECT_FILE=""
if [ -n "$GIT_ROOT" ] && [ -f "${GIT_ROOT}/pyproject.toml" ]; then
    PYPROJECT_FILE="${GIT_ROOT}/pyproject.toml"
elif [ -f "${THIS_DIR}/../pyproject.toml" ]; then
    PYPROJECT_FILE="${THIS_DIR}/../pyproject.toml"
elif [ -f "./pyproject.toml" ]; then
    PYPROJECT_FILE="./pyproject.toml"
fi

if [ -n "$PYPROJECT_FILE" ] && [ -f "$PYPROJECT_FILE" ]; then
    # Try yq first (faster), fallback to grep
    if command -v yq &> /dev/null; then
        SCITEX_WRITER_VERSION=$(yq -r '.project.version' "$PYPROJECT_FILE" 2>/dev/null || echo "unknown")
    else
        # Fallback: extract version with grep and sed
        SCITEX_WRITER_VERSION=$(grep '^version = ' "$PYPROJECT_FILE" | sed 's/version = "\(.*\)"/\1/' | head -1)
    fi
    # Remove quotes and whitespace if present
    SCITEX_WRITER_VERSION=$(echo "$SCITEX_WRITER_VERSION" | tr -d '"' | tr -d '[:space:]')
else
    SCITEX_WRITER_VERSION="unknown"
fi
export SCITEX_WRITER_VERSION

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
echo_warn() { echo -e "${YELLOW}WARN: $1${NC}"; }
echo_error_soft() { echo -e "${RED}ERRO: $1${NC}"; }
# ---------------------------------------

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Logging
CONFIG_LOADED=${CONFIG_LOADED:-false}
if [ "$CONFIG_LOADED" != "true" ]; then
    echo_header "SciTeX Writer v${SCITEX_WRITER_VERSION}"
    echo_info "Running $0..."
fi

# Manuscript Type
SCITEX_WRITER_DOC_TYPE="${1:-$SCITEX_WRITER_DOC_TYPE}"
CONFIG_FILE="$THIS_DIR/config_${SCITEX_WRITER_DOC_TYPE}.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "ERROR: Config file $CONFIG_FILE not found"
    echo "ERROR: Please check SCITEX_WRITER_DOC_TYPE is set correctly"
    echo "ERROR: (e.g., export SCITEX_WRITER_DOC_TYPE=manuscript # (manuscript, supplementary, or revision))"
    exit
fi

# Main
export SCITEX_WRITER_VERBOSE_PDFLATEX="${SCITEX_WRITER_VERBOSE_PDFLATEX:-$(yq -r '.verbosity.pdflatex' $CONFIG_FILE)}"
export SCITEX_WRITER_VERBOSE_BIBTEX="${SCITEX_WRITER_VERBOSE_BIBTEX:-$(yq -r '.verbosity.bibtex' $CONFIG_FILE)}"

export SCITEX_WRITER_CITATION_STYLE="${SCITEX_WRITER_CITATION_STYLE:-$(yq -r '.citation.style' $CONFIG_FILE)}"

export STWX_ROOT_DIR="$(yq -r '.paths.doc_root_dir' $CONFIG_FILE)"
export LOG_DIR="$(yq -r '.paths.doc_log_dir' $CONFIG_FILE)"
export SCITEX_WRITER_GLOBAL_LOG_FILE="$(yq -r '.paths.global_log_file' $CONFIG_FILE)"
export SCITEX_WRITER_BASE_TEX="$(yq -r '.paths.base_tex' $CONFIG_FILE)"
export SCITEX_WRITER_COMPILED_TEX="$(yq -r '.paths.compiled_tex' $CONFIG_FILE)"
export SCITEX_WRITER_COMPILED_PDF="$(yq -r '.paths.compiled_pdf' $CONFIG_FILE)"
export SCITEX_WRITER_DIFF_TEX="$(yq -r '.paths.diff_tex' $CONFIG_FILE)"
export SCITEX_WRITER_DIFF_PDF="$(yq -r '.paths.diff_pdf' $CONFIG_FILE)"
export SCITEX_WRITER_VERSIONS_DIR="$(yq -r '.paths.archive_dir' $CONFIG_FILE)"
export SCITEX_WRITER_VERSION_COUNTER_TXT="$(yq -r '.paths.version_counter_txt' $CONFIG_FILE)"
export SCITEX_WRITER_TEXLIVE_APPTAINER_SIF="$(yq -r '.paths.texlive_apptainer_sif' $CONFIG_FILE)"
export SCITEX_WRITER_MERMAID_APPTAINER_SIF="$(yq -r '.paths.mermaid_apptainer_sif' $CONFIG_FILE)"


export SCITEX_WRITER_FIGURE_DIR="$(yq -r '.figures.dir' $CONFIG_FILE)"
export SCITEX_WRITER_FIGURE_CAPTION_MEDIA_DIR="$(yq -r '.figures.caption_media_dir' $CONFIG_FILE)"
export SCITEX_WRITER_FIGURE_JPG_DIR="$(yq -r '.figures.jpg_dir' $CONFIG_FILE)"
export SCITEX_WRITER_FIGURE_COMPILED_DIR="$(yq -r '.figures.compiled_dir' $CONFIG_FILE)"
export SCITEX_WRITER_FIGURE_COMPILED_FILE="$(yq -r '.figures.compiled_file' $CONFIG_FILE)"
export SCITEX_WRITER_FIGURE_TEMPLATES_DIR="$(yq -r '.figures.templates_dir' $CONFIG_FILE)"
export SCITEX_WRITER_FIGURE_TEMPLATE_TEX="$(yq -r '.figures.template_tex' $CONFIG_FILE)"
export SCITEX_WRITER_FIGURE_TEMPLATE_JPG="$(yq -r '.figures.template_jpg' $CONFIG_FILE)"
export SCITEX_WRITER_FIGURE_TEMPLATE_PPTX="$(yq -r '.figures.template_pptx' $CONFIG_FILE)"
export SCITEX_WRITER_FIGURE_TEMPLATE_JNT="$(yq -r '.figures.template_jnt' $CONFIG_FILE)"

export SCITEX_WRITER_TABLE_DIR="$(yq -r '.tables.dir' $CONFIG_FILE)"
export SCITEX_WRITER_TABLE_CAPTION_MEDIA_DIR="$(yq -r '.tables.caption_media_dir' $CONFIG_FILE)"
export SCITEX_WRITER_TABLE_COMPILED_DIR="$(yq -r '.tables.compiled_dir' $CONFIG_FILE)"
export SCITEX_WRITER_TABLE_COMPILED_FILE="$(yq -r '.tables.compiled_file' $CONFIG_FILE)"

export SCITEX_WRITER_WORDCOUNT_DIR="$(yq -r '.misc.wordcount_dir' $CONFIG_FILE)"
export SCITEX_WRITER_TREE_TXT="$(yq -r '.misc.tree_txt' $CONFIG_FILE)"


if [ "$CONFIG_LOADED" != "true" ]; then
    echo_success "    Configuration Loaded for $SCITEX_WRITER_DOC_TYPE (v${SCITEX_WRITER_VERSION})"
    export CONFIG_LOADED=true
fi

# EOF