#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-12 09:05:04 (ywatanabe)"
# File: ./config/load_config.sh

ORIG_DIR="$(pwd)"
THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
echo >"$LOG_PATH"

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

echo_warn() { echo -e "${YELLOW}WARN: $1${NC}"; }
echo_error_soft() { echo -e "${RED}ERRO: $1${NC}"; }

# Skip if already loaded (prevents redundant 4s overhead per load)
if [ "$CONFIG_LOADED" = "true" ]; then
    return 0
fi

# Load version from pyproject.toml (single source of truth)
VERSION_FILE=""
if [ -f "${THIS_DIR}/../VERSION" ]; then
    VERSION_FILE="${THIS_DIR}/../VERSION"
elif [ -f "./VERSION" ]; then
    VERSION_FILE="./VERSION"
fi

if [ -n "$VERSION_FILE" ] && [ -f "$VERSION_FILE" ]; then
    SCITEX_WRITER_VERSION=$(cat "$VERSION_FILE")
else
    SCITEX_WRITER_VERSION="unknown"
fi
export SCITEX_WRITER_VERSION

# Logging (quiet by default)
CONFIG_LOADED=${CONFIG_LOADED:-false}
if [ "$CONFIG_LOADED" != "true" ] && [ "${SCITEX_LOG_LEVEL:-1}" -ge 2 ]; then
    echo_info "Loading configuration for ${SCITEX_WRITER_VERSION}..."
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

# Main - Use GNU parallel for speed (with fallback to sequential)
if command -v parallel &>/dev/null; then
    # Fast path: Use GNU parallel for truly parallel yq calls
    export CONFIG_FILE # Export so parallel subshells can access it
    eval "$(parallel -k --colsep ':' "echo \"export {1}=\\\"\$(yq -r '{2}' '$CONFIG_FILE')\\\"\"" ::: \
        'SCITEX_WRITER_VERBOSE_PDFLATEX:.verbosity.pdflatex' \
        'SCITEX_WRITER_VERBOSE_BIBTEX:.verbosity.bibtex' \
        'SCITEX_WRITER_CITATION_STYLE:.citation.style' \
        'SCITEX_WRITER_ROOT_DIR:.paths.doc_root_dir' \
        'LOG_DIR:.paths.doc_log_dir' \
        'SCITEX_WRITER_GLOBAL_LOG_FILE:.paths.global_log_file' \
        'SCITEX_WRITER_BASE_TEX:.paths.base_tex' \
        'SCITEX_WRITER_COMPILED_TEX:.paths.compiled_tex' \
        'SCITEX_WRITER_COMPILED_PDF:.paths.compiled_pdf' \
        'SCITEX_WRITER_DIFF_TEX:.paths.diff_tex' \
        'SCITEX_WRITER_DIFF_PDF:.paths.diff_pdf' \
        'SCITEX_WRITER_VERSIONS_DIR:.paths.archive_dir' \
        'SCITEX_WRITER_TEXLIVE_APPTAINER_SIF:.paths.texlive_apptainer_sif' \
        'SCITEX_WRITER_MERMAID_APPTAINER_SIF:.paths.mermaid_apptainer_sif' \
        'SCITEX_WRITER_FIGURE_DIR:.figures.dir' \
        'SCITEX_WRITER_FIGURE_CAPTION_MEDIA_DIR:.figures.caption_media_dir' \
        'SCITEX_WRITER_FIGURE_JPG_DIR:.figures.jpg_dir' \
        'SCITEX_WRITER_FIGURE_COMPILED_DIR:.figures.compiled_dir' \
        'SCITEX_WRITER_FIGURE_COMPILED_FILE:.figures.compiled_file' \
        'SCITEX_WRITER_FIGURE_TEMPLATES_DIR:.figures.templates_dir' \
        'SCITEX_WRITER_FIGURE_TEMPLATE_TEX:.figures.template_tex' \
        'SCITEX_WRITER_FIGURE_TEMPLATE_JPG:.figures.template_jpg' \
        'SCITEX_WRITER_FIGURE_TEMPLATE_PPTX:.figures.template_pptx' \
        'SCITEX_WRITER_FIGURE_TEMPLATE_JNT:.figures.template_jnt' \
        'SCITEX_WRITER_TABLE_DIR:.tables.dir' \
        'SCITEX_WRITER_TABLE_CAPTION_MEDIA_DIR:.tables.caption_media_dir' \
        'SCITEX_WRITER_TABLE_COMPILED_DIR:.tables.compiled_dir' \
        'SCITEX_WRITER_TABLE_COMPILED_FILE:.tables.compiled_file' \
        'SCITEX_WRITER_WORDCOUNT_DIR:.misc.wordcount_dir' \
        'SCITEX_WRITER_TREE_TXT:.misc.tree_txt')"
else
    # Fallback: Sequential yq calls (slower but works without GNU parallel)
    echo_warning "    GNU parallel not found - using slower sequential config loading"
    echo_warning "    Install parallel for 5x faster startup: apt install parallel"

    export SCITEX_WRITER_VERBOSE_PDFLATEX="$(yq -r '.verbosity.pdflatex' "$CONFIG_FILE")"
    export SCITEX_WRITER_VERBOSE_BIBTEX="$(yq -r '.verbosity.bibtex' "$CONFIG_FILE")"
    export SCITEX_WRITER_CITATION_STYLE="$(yq -r '.citation.style' "$CONFIG_FILE")"
    export SCITEX_WRITER_ROOT_DIR="$(yq -r '.paths.doc_root_dir' "$CONFIG_FILE")"
    export LOG_DIR="$(yq -r '.paths.doc_log_dir' "$CONFIG_FILE")"
    export SCITEX_WRITER_GLOBAL_LOG_FILE="$(yq -r '.paths.global_log_file' "$CONFIG_FILE")"
    export SCITEX_WRITER_BASE_TEX="$(yq -r '.paths.base_tex' "$CONFIG_FILE")"
    export SCITEX_WRITER_COMPILED_TEX="$(yq -r '.paths.compiled_tex' "$CONFIG_FILE")"
    export SCITEX_WRITER_COMPILED_PDF="$(yq -r '.paths.compiled_pdf' "$CONFIG_FILE")"
    export SCITEX_WRITER_DIFF_TEX="$(yq -r '.paths.diff_tex' "$CONFIG_FILE")"
    export SCITEX_WRITER_DIFF_PDF="$(yq -r '.paths.diff_pdf' "$CONFIG_FILE")"
    export SCITEX_WRITER_VERSIONS_DIR="$(yq -r '.paths.archive_dir' "$CONFIG_FILE")"
    export SCITEX_WRITER_TEXLIVE_APPTAINER_SIF="$(yq -r '.paths.texlive_apptainer_sif' "$CONFIG_FILE")"
    export SCITEX_WRITER_MERMAID_APPTAINER_SIF="$(yq -r '.paths.mermaid_apptainer_sif' "$CONFIG_FILE")"
    export SCITEX_WRITER_FIGURE_DIR="$(yq -r '.figures.dir' "$CONFIG_FILE")"
    export SCITEX_WRITER_FIGURE_CAPTION_MEDIA_DIR="$(yq -r '.figures.caption_media_dir' "$CONFIG_FILE")"
    export SCITEX_WRITER_FIGURE_JPG_DIR="$(yq -r '.figures.jpg_dir' "$CONFIG_FILE")"
    export SCITEX_WRITER_FIGURE_COMPILED_DIR="$(yq -r '.figures.compiled_dir' "$CONFIG_FILE")"
    export SCITEX_WRITER_FIGURE_COMPILED_FILE="$(yq -r '.figures.compiled_file' "$CONFIG_FILE")"
    export SCITEX_WRITER_FIGURE_TEMPLATES_DIR="$(yq -r '.figures.templates_dir' "$CONFIG_FILE")"
    export SCITEX_WRITER_FIGURE_TEMPLATE_TEX="$(yq -r '.figures.template_tex' "$CONFIG_FILE")"
    export SCITEX_WRITER_FIGURE_TEMPLATE_JPG="$(yq -r '.figures.template_jpg' "$CONFIG_FILE")"
    export SCITEX_WRITER_FIGURE_TEMPLATE_PPTX="$(yq -r '.figures.template_pptx' "$CONFIG_FILE")"
    export SCITEX_WRITER_FIGURE_TEMPLATE_JNT="$(yq -r '.figures.template_jnt' "$CONFIG_FILE")"
    export SCITEX_WRITER_TABLE_DIR="$(yq -r '.tables.dir' "$CONFIG_FILE")"
    export SCITEX_WRITER_TABLE_CAPTION_MEDIA_DIR="$(yq -r '.tables.caption_media_dir' "$CONFIG_FILE")"
    export SCITEX_WRITER_TABLE_COMPILED_DIR="$(yq -r '.tables.compiled_dir' "$CONFIG_FILE")"
    export SCITEX_WRITER_TABLE_COMPILED_FILE="$(yq -r '.tables.compiled_file' "$CONFIG_FILE")"
    export SCITEX_WRITER_WORDCOUNT_DIR="$(yq -r '.misc.wordcount_dir' "$CONFIG_FILE")"
    export SCITEX_WRITER_TREE_TXT="$(yq -r '.misc.tree_txt' "$CONFIG_FILE")"
fi

if [ "$CONFIG_LOADED" != "true" ]; then
    # Only show in verbose mode
    if [ "${SCITEX_LOG_LEVEL:-1}" -ge 2 ]; then
        echo_success "    Configuration loaded: $SCITEX_WRITER_DOC_TYPE (${SCITEX_WRITER_VERSION})"
    fi
    export CONFIG_LOADED=true
fi

# EOF
