#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-26 22:48:00 (ywatanabe)"
# File: ./paper/scripts/installation/install_ubuntu.sh

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

# EOF