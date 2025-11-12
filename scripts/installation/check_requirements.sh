#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-26 22:46:00 (ywatanabe)"
# File: ./paper/scripts/installation/check_requirements.sh

ORIG_DIR="$(pwd)"
THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
PROJECT_ROOT="$(cd $THIS_DIR/../../ && pwd)"

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
echo
echo_info "Checking SciTeX system requirements..."
echo

MISSING_REQUIREMENTS=0

# Check for required commands
check_command() {
    local cmd=$1
    local description=$2
    local install_hint=$3
    
    if command -v $cmd &> /dev/null; then
        echo_success "✓ $description ($cmd found)"
    else
        echo_error "✗ $description ($cmd not found)"
        if [ -n "$install_hint" ]; then
            echo_info "  Install with: $install_hint"
        fi
        MISSING_REQUIREMENTS=$((MISSING_REQUIREMENTS + 1))
    fi
}

# Essential requirements
echo_info "Essential requirements:"
check_command "bash" "Bash shell" ""
check_command "yq" "YAML parser" "pip install yq or snap install yq"

echo
echo_info "Container runtime (need at least one):"
APPTAINER_FOUND=0
SINGULARITY_FOUND=0

if command -v apptainer &> /dev/null; then
    echo_success "✓ Apptainer found"
    APPTAINER_FOUND=1
else
    echo_warning "○ Apptainer not found"
fi

if command -v singularity &> /dev/null; then
    echo_success "✓ Singularity found"
    SINGULARITY_FOUND=1
else
    echo_warning "○ Singularity not found"
fi

if [ $APPTAINER_FOUND -eq 0 ] && [ $SINGULARITY_FOUND -eq 0 ]; then
    echo_error "✗ No container runtime found (need Apptainer or Singularity)"
    echo_info "  Install Apptainer: https://apptainer.org/docs/admin/main/installation.html"
    echo_info "  Install Singularity: https://sylabs.io/guides/3.0/user-guide/installation.html"
    MISSING_REQUIREMENTS=$((MISSING_REQUIREMENTS + 1))
fi

echo
echo_info "Optional tools (will use containers if not found):"

# Track optional tools separately
check_optional_command() {
    local cmd=$1
    local description=$2
    local install_hint=$3
    
    if command -v $cmd &> /dev/null; then
        echo_success "✓ $description ($cmd found)"
    else
        echo_warning "○ $description (will use container)"
    fi
}

check_optional_command "pdflatex" "LaTeX compiler"
check_optional_command "bibtex" "BibTeX processor"
check_optional_command "latexdiff" "LaTeX diff tool"
check_optional_command "mmdc" "Mermaid diagram tool"
check_optional_command "convert" "ImageMagick"

echo
echo_info "Python dependencies for bibliography tools:"
# Check Python packages
check_python_package() {
    local package=$1
    local description=$2
    local install_hint=$3

    if python3 -c "import $package" &> /dev/null; then
        echo_success "✓ $description ($package)"
    else
        echo_warning "○ $description ($package not found)"
        if [ -n "$install_hint" ]; then
            echo_info "  Install with: $install_hint"
        fi
    fi
}

check_python_package "bibtexparser" "BibTeX parser" "pip install bibtexparser"

echo
echo_info "Module system (for HPC):"
if command -v module &> /dev/null; then
    echo_success "✓ Module system found"
    # Check for texlive module
    if module avail texlive &> /dev/null 2>&1; then
        echo_success "  ✓ texlive module available"
    else
        echo_warning "  ○ texlive module not available"
    fi
else
    echo_warning "○ Module system not found (not required if using containers)"
fi

echo
echo_info "Checking container availability..."
CONTAINER_DIR="$PROJECT_ROOT/.cache/containers"

if [ -f "$CONTAINER_DIR/texlive.sif" ]; then
    SIZE=$(du -h "$CONTAINER_DIR/texlive.sif" | cut -f1)
    echo_success "✓ TeXLive container exists ($SIZE)"
else
    echo_warning "○ TeXLive container not found (will download on first use)"
fi

if [ -f "$CONTAINER_DIR/mermaid_container.sif" ]; then
    SIZE=$(du -h "$CONTAINER_DIR/mermaid_container.sif" | cut -f1)
    echo_success "✓ Mermaid container exists ($SIZE)"
else
    echo_warning "○ Mermaid container not found (will download on first use)"
fi

echo
if [ $MISSING_REQUIREMENTS -eq 0 ]; then
    echo_success "All essential requirements satisfied!"
    echo_info "Run './compile_manuscript' to compile your document"
else
    echo_error "Missing $MISSING_REQUIREMENTS essential requirement(s)"
    echo_info "Please install missing requirements and try again"
    exit 1
fi

# EOF