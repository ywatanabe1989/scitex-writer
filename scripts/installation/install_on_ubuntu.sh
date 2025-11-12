#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-26 23:31:10 (ywatanabe)"
# File: ./paper/scripts/installation/install_on_ubuntu.sh

ORIG_DIR="$(pwd)"
THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
echo > "$LOG_PATH"

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

# Install system dependencies for Ubuntu/Debian

set -e

echo "Installing system dependencies for Ubuntu..."

# Update package list
sudo apt-get update

# Install essential tools
sudo apt-get install -y \
    yq \
    git \
    wget \
    curl

# Install Apptainer if not present
if ! command -v apptainer &> /dev/null; then
    echo "Installing Apptainer..."
    # Add Apptainer PPA
    sudo add-apt-repository -y ppa:apptainer/ppa
    sudo apt-get update
    sudo apt-get install -y apptainer
fi

# Optional: Install native LaTeX (large, ~5GB)
read -p "Install native LaTeX? (large, ~5GB) [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo apt-get install -y \
        texlive-full \
        latexdiff
fi

echo "Installation complete!"
echo "Run './scripts/installation/check_requirements.sh' to verify"

# sudo apt update
# sudo apt-get install texlive-full -y
# sudo apt-get install tree -y
# sudo apt-get install bibtex -y
# sudo apt-get install xlsx2csv csv2latex -y
# # sudo apt-get install diffpdf -y


# # ./scripts/shell/install_on_ubuntu.sh

# EOF