#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-27 16:05:15 (ywatanabe)"
# File: ./paper/config/load_config.sh

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

echo_info() { echo -e "${GRAY}INFO: $1${NC}"; }
echo_success() { echo -e "${GREEN}SUCC: $1${NC}"; }
echo_warn() { echo -e "${YELLOW}WARN: $1${NC}"; }
echo_error_soft() { echo -e "${RED}ERRO: $1${NC}"; }
echo_error() { echo -e "${RED}ERRO: $1${NC}"; exit 1; }

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Logging
CONFIG_LOADED=${CONFIG_LOADED:-false}
if [ "$CONFIG_LOADED" != "true" ]; then
    echo_info "Running $0..."
fi

# Manuscript Type
STXW_DOC_TYPE="${1:-$STXW_DOC_TYPE}"
CONFIG_FILE="$THIS_DIR/config_${STXW_DOC_TYPE}.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "ERROR: Config file $CONFIG_FILE not found"
    echo "ERROR: Please check STXW_DOC_TYPE is set correctly"
    echo "ERROR: (e.g., export STXW_DOC_TYPE=manuscript # (manuscript, supplementary, or revision))"
    exit
fi

# Main
# NOTE: Using -r flag for yq v3 compatibility (container uses v3.4.3, outputs with quotes by default)
export STXW_VERBOSE_PDFLATEX="${STXW_VERBOSE_PDFLATEX:-$(yq -r '.verbosity.pdflatex' $CONFIG_FILE)}"
export STXW_VERBOSE_BIBTEX="${STXW_VERBOSE_BIBTEX:-$(yq -r '.verbosity.bibtex' $CONFIG_FILE)}"

export STWX_ROOT_DIR="$(yq -r '.paths.doc_root_dir' $CONFIG_FILE)"
export LOG_DIR="$(yq -r '.paths.doc_log_dir' $CONFIG_FILE)"
export STXW_GLOBAL_LOG_FILE="$(yq -r '.paths.global_log_file' $CONFIG_FILE)"
export STXW_BASE_TEX="$(yq -r '.paths.base_tex' $CONFIG_FILE)"
export STXW_COMPILED_TEX="$(yq -r '.paths.compiled_tex' $CONFIG_FILE)"
export STXW_COMPILED_PDF="$(yq -r '.paths.compiled_pdf' $CONFIG_FILE)"
export STXW_DIFF_TEX="$(yq -r '.paths.diff_tex' $CONFIG_FILE)"
export STXW_DIFF_PDF="$(yq -r '.paths.diff_pdf' $CONFIG_FILE)"
export STXW_VERSIONS_DIR="$(yq -r '.paths.archive_dir' $CONFIG_FILE)"
export STXW_VERSION_COUNTER_TXT="$(yq -r '.paths.version_counter_txt' $CONFIG_FILE)"
export STXW_TEXLIVE_APPTAINER_SIF="$(yq -r '.paths.texlive_apptainer_sif' $CONFIG_FILE)"
export STXW_MERMAID_APPTAINER_SIF="$(yq -r '.paths.mermaid_apptainer_sif' $CONFIG_FILE)"


export STXW_FIGURE_DIR="$(yq -r '.figures.dir' $CONFIG_FILE)"
export STXW_FIGURE_CAPTION_MEDIA_DIR="$(yq -r '.figures.caption_media_dir' $CONFIG_FILE)"
export STXW_FIGURE_JPG_DIR="$(yq -r '.figures.jpg_dir' $CONFIG_FILE)"
export STXW_FIGURE_COMPILED_DIR="$(yq -r '.figures.compiled_dir' $CONFIG_FILE)"
export STXW_FIGURE_COMPILED_FILE="$(yq -r '.figures.compiled_file' $CONFIG_FILE)"
export STXW_FIGURE_TEMPLATES_DIR="$(yq -r '.figures.templates_dir' $CONFIG_FILE)"
export STXW_FIGURE_TEMPLATE_TEX="$(yq -r '.figures.template_tex' $CONFIG_FILE)"
export STXW_FIGURE_TEMPLATE_JPG="$(yq -r '.figures.template_jpg' $CONFIG_FILE)"
export STXW_FIGURE_TEMPLATE_PPTX="$(yq -r '.figures.template_pptx' $CONFIG_FILE)"
export STXW_FIGURE_TEMPLATE_JNT="$(yq -r '.figures.template_jnt' $CONFIG_FILE)"

export STXW_TABLE_DIR="$(yq -r '.tables.dir' $CONFIG_FILE)"
export STXW_TABLE_CAPTION_MEDIA_DIR="$(yq -r '.tables.caption_media_dir' $CONFIG_FILE)"
export STXW_TABLE_COMPILED_DIR="$(yq -r '.tables.compiled_dir' $CONFIG_FILE)"
export STXW_TABLE_COMPILED_FILE="$(yq -r '.tables.compiled_file' $CONFIG_FILE)"

export STXW_WORDCOUNT_DIR="$(yq -r '.misc.wordcount_dir' $CONFIG_FILE)"
export STXW_TREE_TXT="$(yq -r '.misc.tree_txt' $CONFIG_FILE)"


if [ "$CONFIG_LOADED" != "true" ]; then
    echo_success "    Configuration Loaded for $STXW_DOC_TYPE"
    export CONFIG_LOADED=true
fi

# EOF