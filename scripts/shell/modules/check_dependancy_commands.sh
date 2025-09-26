#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-26 09:37:52 (ywatanabe)"
# File: ./paper/manuscript/scripts/shell/modules/check_dependancy_commands.sh

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

touch "$LOG_PATH" >/dev/null 2>&1
source ./config/config_manuscript.src

echo_info "Checking dependencies..."


# Load modules if available
if command -v module &> /dev/null; then
    if module avail texlive &> /dev/null 2>&1; then
        module load texlive
    fi
    if module avail parallel &> /dev/null 2>&1; then
        module load parallel
    fi
    if module avail nodejs &> /dev/null 2>&1; then
        module load nodejs
    fi
fi

# Detect package manager
detect_package_manager() {
    if command -v apt &> /dev/null; then
        echo "apt"
    elif command -v yum &> /dev/null; then
        echo "yum"
    else
        echo "unknown"
    fi
}

PKG_MANAGER=$(detect_package_manager)

# Check for module command availability
has_module_command() {
    command -v module &> /dev/null
}

# Standalone checker for each tool
check_pdflatex() {
    # if ! command -v pdflatex &> /dev/null; then
    #     if command -v module &> /dev/null && module avail texlive &> /dev/null; then
    #         module load texlive
    #     fi
    # fi

    if ! command -v pdflatex &> /dev/null; then
        echo "- pdflatex"
        if has_module_command; then
            echo "    - module load texlive"
        fi
        if [ "$PKG_MANAGER" = "apt" ]; then
            echo "    - sudo apt install texlive-latex-base"
        elif [ "$PKG_MANAGER" = "yum" ]; then
            echo "    - sudo yum install texlive-latex"
        fi
        return 1
    fi
    return 0
}

check_bibtex() {
    # if ! command -v bibtex &> /dev/null; then
    #     if command -v module &> /dev/null && module avail texlive &> /dev/null; then
    #         module load texlive
    #     fi
    # fi

    if ! command -v bibtex &> /dev/null; then
        echo "- bibtex"
        if has_module_command; then
            echo "    - module load texlive"
        fi
        if [ "$PKG_MANAGER" = "apt" ]; then
            echo "    - sudo apt install texlive-bibtex-extra"
        elif [ "$PKG_MANAGER" = "yum" ]; then
            echo "    - sudo yum install texlive-bibtex"
        fi
        return 1
    fi
    return 0
}


check_texcount() {
    # if ! command -v texcount &> /dev/null; then
    #     if command -v module &> /dev/null && module avail texlive &> /dev/null; then
    #         module load texlive
    #     fi
    # fi

    if ! command -v texcount &> /dev/null; then
        echo "- texcount"
        if has_module_command; then
            echo "    - module load texlive"
        fi
        if [ "$PKG_MANAGER" = "apt" ]; then
            echo "    - sudo apt install texlive-extra-utils"
        elif [ "$PKG_MANAGER" = "yum" ]; then
            echo "    - sudo yum install texlive-texcount"
        fi
        return 1
    fi
    return 0
}


check_xlsx2csv() {
    if ! command -v xlsx2csv &> /dev/null && ! python3 -c "import xlsx2csv" &> /dev/null 2>&1; then
        echo "  - xlsx2csv"
        if [ "$PKG_MANAGER" = "apt" ]; then
            echo "      sudo apt install xlsx2csv"
        elif [ "$PKG_MANAGER" = "yum" ]; then
            echo "      sudo yum install python3-xlsx2csv"
        fi
        echo "      pip install xlsx2csv"
        return 1
    fi
    return 0
}

check_csv2latex() {
    if ! command -v csv2latex &> /dev/null && ! python3 -c "import csv2latex" &> /dev/null 2>&1; then
        echo "  - csv2latex"
        if [ "$PKG_MANAGER" = "apt" ]; then
            echo "      sudo apt install csv2latex"
        fi
        echo "      pip install csv2latex"
        return 1
    fi
    return 0
}

check_parallel() {
    if ! command -v parallel &> /dev/null; then
        echo "- parallel"
        # if has_module_command; then
        #     echo "    - module load parallel"
        # fi
        if [ "$PKG_MANAGER" = "apt" ]; then
            echo "    - sudo apt install parallel"
        elif [ "$PKG_MANAGER" = "yum" ]; then
            echo "    - sudo yum install parallel"
        fi
        return 1
    fi
    return 0
}

check_opencv() {
    if command -v python3 &> /dev/null; then
        if ! python3 -c "import cv2" &> /dev/null; then
            echo "- opencv-python (optional, for --crop_tif)"
            echo "    - pip install opencv-python"
            return 1
        fi
    fi
    return 0
}

check_numpy() {
    if command -v python3 &> /dev/null; then
        if ! python3 -c "import numpy" &> /dev/null; then
            echo "- numpy (optional, for --crop_tif)"
            echo "    - pip install numpy"
            return 1
        fi
    fi
    return 0
}

check_mmdc() {
    if ! command -v npm &> /dev/null; then
        echo "- npm (optional, for Mermaid diagrams)"
        echo "    - module load nodejs"
        return 1
    fi

    if ! command -v mmdc &> /dev/null; then
        echo "- mmdc (optional, for Mermaid diagrams)"
        echo "    - npm install -g @mermaid-js/mermaid-cli"
        return 1
    fi

    return 0
}

# Check all required commands
check_all_dependencies() {
    local has_missing_required=false
    local has_missing_optional=false
    local required_output=""
    local optional_output=""

    # Required tools
    for checker in check_pdflatex check_bibtex check_texcount check_xlsx2csv check_csv2latex check_parallel; do
        output=$($checker)
        if [ -n "$output" ]; then
            required_output="${required_output}${output}\n\n"
        fi
    done

    # Optional tools
    for checker in check_opencv check_numpy check_mmdc; do
        output=$($checker)
        if [ -n "$output" ]; then
            has_missing_optional=true
            optional_output="${optional_output}${output}\n\n"
        fi
    done

    # Display results
    if [ -n "$required_output" ]; then
        echo "Missing required tools and potential installation commands:"
        echo -e "$required_output"
        exit 1
    else
        echo_success "All required tools are available."
    fi

    if [ -n "$optional_output" ]; then
        echo_warning "Missing optional tools and potential installation commands:"
        echo -e "$optional_output"
        exit 1
    fi
}

# Run checks
check_all_dependencies

# EOF