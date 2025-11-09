#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-26 23:29:05 (ywatanabe)"
# File: ./paper/scripts/installation/download_containers.sh

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

PROJECT_ROOT="$(cd $THIS_DIR/../../ && pwd)"

echo
echo_info "Downloading containers for SciTeX compilation system..."

# Check for container runtime
get_container_runtime() {
    if command -v apptainer &> /dev/null; then
        echo "apptainer"
    elif command -v singularity &> /dev/null; then
        echo "singularity"
    else
        echo ""
    fi
}

RUNTIME=$(get_container_runtime)
if [ -z "$RUNTIME" ]; then
    echo_error "Neither Apptainer nor Singularity found. Please install one of them first."
    echo_info "  - Apptainer: https://apptainer.org/docs/admin/main/installation.html"
    echo_info "  - Singularity: https://sylabs.io/guides/3.0/user-guide/installation.html"
    exit 1
fi

echo_success "Found container runtime: $RUNTIME"

# Setup container directory
CONTAINER_DIR="$PROJECT_ROOT/.cache/containers"
mkdir -p "$CONTAINER_DIR"

# Download TeXLive container
TEXLIVE_SIF="$CONTAINER_DIR/texlive_container.sif"
if [ ! -f "$TEXLIVE_SIF" ]; then
    echo_info "Downloading TeXLive container (~2.3GB)..."
    $RUNTIME pull "$TEXLIVE_SIF" docker://texlive/texlive:latest
    if [ -f "$TEXLIVE_SIF" ]; then
        echo_success "TeXLive container downloaded successfully"
    else
        echo_error "Failed to download TeXLive container"
        exit 1
    fi
else
    echo_success "TeXLive container already exists"
fi

# Download Mermaid container
MERMAID_SIF="$CONTAINER_DIR/mermaid_container.sif"
if [ ! -f "$MERMAID_SIF" ]; then
    echo_info "Downloading Mermaid container (~750MB)..."
    $RUNTIME pull "$MERMAID_SIF" docker://minlag/mermaid-cli:latest
    if [ -f "$MERMAID_SIF" ]; then
        echo_success "Mermaid container downloaded successfully"
    else
        echo_error "Failed to download Mermaid container"
        exit 1
    fi
else
    echo_success "Mermaid container already exists"
fi

# Download ImageMagick container (optional but recommended)
IMAGEMAGICK_SIF="$CONTAINER_DIR/imagemagick_container.sif"
if [ ! -f "$IMAGEMAGICK_SIF" ]; then
    echo_info "Downloading ImageMagick container (~200MB)..."
    $RUNTIME pull "$IMAGEMAGICK_SIF" docker://dpokidov/imagemagick:latest
    if [ -f "$IMAGEMAGICK_SIF" ]; then
        echo_success "ImageMagick container downloaded successfully"
    else
        echo_warning "Failed to download ImageMagick container (optional)"
    fi
else
    echo_success "ImageMagick container already exists"
fi

# Create puppeteer config for Mermaid
PUPPETEER_CONFIG="$PROJECT_ROOT/.cache/puppeteer-config.json"
if [ ! -f "$PUPPETEER_CONFIG" ]; then
    echo_info "Creating Puppeteer configuration..."
    cat > "$PUPPETEER_CONFIG" << 'EOF'
{
  "executablePath": "/usr/bin/chromium-browser",
  "args": ["--no-sandbox", "--disable-setuid-sandbox"]
}
EOF
    echo_success "Puppeteer configuration created"
else
    echo_success "Puppeteer configuration already exists"
fi

echo
echo_success "Container setup complete!"
echo_info "Containers stored in: $CONTAINER_DIR"
ls -lah "$CONTAINER_DIR"/*.sif

# EOF