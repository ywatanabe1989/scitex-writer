#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-08 10:42:00 (ywatanabe)"
# File: ./scripts/shell/modules/apply_citation_style.sh

# ============================================================================
# Apply Citation Style from Config to LaTeX Bibliography File
# ============================================================================
# This script reads the citation style from SCITEX_WRITER_CITATION_STYLE environment
# variable and updates the bibliography.tex file to use that style.
#
# Usage:
#   source config/load_config.sh
#   ./scripts/shell/modules/apply_citation_style.sh
#
# Or call it from compilation scripts after loading config
# ============================================================================

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo_success() { echo -e "${GREEN}SUCC: $1${NC}"; }
echo_warning() { echo -e "${YELLOW}WARN: $1${NC}"; }
echo_error() { echo -e "${RED}ERRO: $1${NC}"; exit 1; }

# Check if SCITEX_WRITER_CITATION_STYLE is set
if [ -z "${SCITEX_WRITER_CITATION_STYLE:-}" ]; then
    echo_warning "SCITEX_WRITER_CITATION_STYLE not set, skipping citation style update"
    echo_warning "Using default style in 00_shared/latex_styles/bibliography.tex"
    exit 0
fi

# Path to bibliography file
BIBLIOGRAPHY_FILE="./00_shared/latex_styles/bibliography.tex"

if [ ! -f "$BIBLIOGRAPHY_FILE" ]; then
    echo_error "Bibliography file not found: $BIBLIOGRAPHY_FILE"
fi

# Current style
CURRENT_STYLE=$(grep '^\\bibliographystyle' "$BIBLIOGRAPHY_FILE" | sed 's/\\bibliographystyle{\(.*\)}/\1/')

if [ "$CURRENT_STYLE" = "$SCITEX_WRITER_CITATION_STYLE" ]; then
    echo_success "Citation style already set to: $SCITEX_WRITER_CITATION_STYLE"
    exit 0
fi

# Create backup
BACKUP_FILE="${BIBLIOGRAPHY_FILE}.bak"
cp "$BIBLIOGRAPHY_FILE" "$BACKUP_FILE"

# Update the bibliography style
# This will comment out the current active style and uncomment the target style
# If target style is not in the file, it will add it

# First, comment out all uncommented \bibliographystyle commands
sed -i '/^\\bibliographystyle/s/^/% /' "$BIBLIOGRAPHY_FILE"

# Check if the target style exists as a commented line
if grep -q "^% \\\\bibliographystyle{${SCITEX_WRITER_CITATION_STYLE}}" "$BIBLIOGRAPHY_FILE"; then
    # Uncomment the first occurrence of the target style
    sed -i "0,/^% \\\\bibliographystyle{${SCITEX_WRITER_CITATION_STYLE}}/{s/^% //}" "$BIBLIOGRAPHY_FILE"
    echo_success "Updated citation style to: $SCITEX_WRITER_CITATION_STYLE (from commented line)"
else
    # Add the new style after line 20 (after OPTION 1 header)
    sed -i "20a\\\\bibliographystyle{${SCITEX_WRITER_CITATION_STYLE}}" "$BIBLIOGRAPHY_FILE"
    echo_success "Updated citation style to: $SCITEX_WRITER_CITATION_STYLE (added new)"
fi

echo_success "Citation style changed: $CURRENT_STYLE → $SCITEX_WRITER_CITATION_STYLE"
echo_success "Backup saved to: $BACKUP_FILE"

# EOF
