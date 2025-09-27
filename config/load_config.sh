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
export STXW_VERBOSE_PDFLATEX="${STXW_VERBOSE_PDFLATEX:-$(yq '.verbosity.pdflatex' $CONFIG_FILE)}"
export STXW_VERBOSE_BIBTEX="${STXW_VERBOSE_BIBTEX:-$(yq '.verbosity.bibtex' $CONFIG_FILE)}"

export STWX_ROOT_DIR="$(yq '.paths.doc_root_dir' $CONFIG_FILE)"
export LOG_DIR="$(yq '.paths.doc_log_dir' $CONFIG_FILE)"
export STXW_GLOBAL_LOG_FILE="$(yq '.paths.global_log_file' $CONFIG_FILE)"
export STXW_BASE_TEX="$(yq '.paths.base_tex' $CONFIG_FILE)"
export STXW_COMPILED_TEX="$(yq '.paths.compiled_tex' $CONFIG_FILE)"
export STXW_COMPILED_PDF="$(yq '.paths.compiled_pdf' $CONFIG_FILE)"
export STXW_DIFF_TEX="$(yq '.paths.diff_tex' $CONFIG_FILE)"
export STXW_DIFF_PDF="$(yq '.paths.diff_pdf' $CONFIG_FILE)"
export STXW_VERSIONS_DIR="$(yq '.paths.archive_dir' $CONFIG_FILE)"
export STXW_VERSION_COUNTER_TXT="$(yq '.paths.version_counter_txt' $CONFIG_FILE)"
export STXW_TEXLIVE_APPTAINER_SIF="$(yq '.paths.texlive_apptainer_sif' $CONFIG_FILE)"
export STXW_MERMAID_APPTAINER_SIF="$(yq '.paths.mermaid_apptainer_sif' $CONFIG_FILE)"


export STXW_FIGURE_DIR="$(yq '.figures.dir' $CONFIG_FILE)"
export STXW_FIGURE_CAPTION_MEDIA_DIR="$(yq '.figures.caption_media_dir' $CONFIG_FILE)"
export STXW_FIGURE_JPG_DIR="$(yq '.figures.jpg_dir' $CONFIG_FILE)"
export STXW_FIGURE_COMPILED_DIR="$(yq '.figures.compiled_dir' $CONFIG_FILE)"
export STXW_FIGURE_COMPILED_FILE="$(yq '.figures.compiled_file' $CONFIG_FILE)"
export STXW_FIGURE_TEMPLATES_DIR="$(yq '.figures.templates_dir' $CONFIG_FILE)"
export STXW_FIGURE_TEMPLATE_TEX="$(yq '.figures.template_tex' $CONFIG_FILE)"
export STXW_FIGURE_TEMPLATE_JPG="$(yq '.figures.template_jpg' $CONFIG_FILE)"
export STXW_FIGURE_TEMPLATE_PPTX="$(yq '.figures.template_pptx' $CONFIG_FILE)"
export STXW_FIGURE_TEMPLATE_JNT="$(yq '.figures.template_jnt' $CONFIG_FILE)"

export STXW_TABLE_DIR="$(yq '.tables.dir' $CONFIG_FILE)"
export STXW_TABLE_CAPTION_MEDIA_DIR="$(yq '.tables.caption_media_dir' $CONFIG_FILE)"
export STXW_TABLE_COMPILED_DIR="$(yq '.tables.compiled_dir' $CONFIG_FILE)"
export STXW_TABLE_COMPILED_FILE="$(yq '.tables.compiled_file' $CONFIG_FILE)"

export STXW_WORDCOUNT_DIR="$(yq '.misc.wordcount_dir' $CONFIG_FILE)"
export STXW_TREE_TXT="$(yq '.misc.tree_txt' $CONFIG_FILE)"


if [ "$CONFIG_LOADED" != "true" ]; then
    echo_success "    Configuration Loaded for $STXW_DOC_TYPE"
    export CONFIG_LOADED=true
fi

# EOF