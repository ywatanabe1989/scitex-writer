#!/bin/bash
# Universal dependency installer for scitex-writer
# Handles system and Python dependencies across platforms

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

install_yq() {
    log_info "Checking yq installation..."

    # Check if Go-based yq is already installed
    if command -v yq &> /dev/null && yq --version 2>&1 | grep -q "mikefarah"; then
        log_info "yq (Go version) already installed: $(yq --version)"
        return 0
    fi

    log_info "Installing yq (Go version)..."

    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo wget -qO /usr/local/bin/yq \
            https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64
        sudo chmod +x /usr/local/bin/yq
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        sudo wget -qO /usr/local/bin/yq \
            https://github.com/mikefarah/yq/releases/latest/download/yq_darwin_amd64
        sudo chmod +x /usr/local/bin/yq
    else
        log_warn "Unsupported OS for automatic yq installation. Please install manually."
        return 1
    fi

    log_info "yq installed: $(yq --version)"
}

install_debian_deps() {
    log_info "Installing Debian/Ubuntu system dependencies..."

    sudo apt-get update

    # Install from file
    if [ -f "$SCRIPT_DIR/system-debian.txt" ]; then
        log_info "Installing packages from system-debian.txt..."
        xargs sudo apt-get install -y < "$SCRIPT_DIR/system-debian.txt"
    else
        log_error "system-debian.txt not found!"
        return 1
    fi

    log_info "Debian/Ubuntu dependencies installed successfully!"
}

install_macos_deps() {
    log_info "Installing macOS system dependencies..."

    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        log_error "Homebrew not found. Please install from https://brew.sh"
        return 1
    fi

    # Install from file
    if [ -f "$SCRIPT_DIR/system-macos.txt" ]; then
        log_info "Installing packages from system-macos.txt..."
        while IFS= read -r package || [ -n "$package" ]; do
            # Skip comments and empty lines
            [[ "$package" =~ ^#.*$ ]] && continue
            [[ -z "$package" ]] && continue
            brew install "$package" || log_warn "Failed to install $package"
        done < "$SCRIPT_DIR/system-macos.txt"
    else
        log_error "system-macos.txt not found!"
        return 1
    fi

    log_info "macOS dependencies installed successfully!"
    log_warn "Remember to update TeX Live Manager:"
    log_warn "  sudo tlmgr update --self"
    log_warn "  sudo tlmgr install collection-latexextra collection-fontsrecommended"
}

install_python_deps() {
    log_info "Installing Python dependencies..."

    # Check if pip is available
    if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
        log_error "pip not found. Please install Python and pip first."
        return 1
    fi

    local PIP_CMD="pip"
    command -v pip3 &> /dev/null && PIP_CMD="pip3"

    if [ -f "$SCRIPT_DIR/python.txt" ]; then
        log_info "Installing packages from python.txt..."
        $PIP_CMD install -r "$SCRIPT_DIR/python.txt"
    else
        log_error "python.txt not found!"
        return 1
    fi

    log_info "Python dependencies installed successfully!"
}

detect_and_install() {
    log_info "Detecting system and installing dependencies..."

    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt-get &> /dev/null; then
            log_info "Detected: Debian/Ubuntu"
            install_debian_deps
        elif command -v yum &> /dev/null; then
            log_error "Red Hat/CentOS not yet supported. Please install dependencies manually."
            log_error "Or use the container: ./compile.sh manuscript"
            return 1
        else
            log_error "Unsupported Linux distribution"
            return 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        log_info "Detected: macOS"
        install_macos_deps
    else
        log_error "Unsupported operating system: $OSTYPE"
        log_error "Please use the container: ./compile.sh manuscript"
        return 1
    fi

    # Install yq (works on both Linux and macOS)
    install_yq

    # Install Python dependencies (cross-platform)
    install_python_deps
}

show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Install all dependencies for scitex-writer project.

OPTIONS:
    --system-only    Install only system dependencies
    --python-only    Install only Python dependencies
    --yq-only        Install only yq
    -h, --help       Show this help message

EXAMPLES:
    $0                    # Install all dependencies
    $0 --system-only      # Install only system packages
    $0 --python-only      # Install only Python packages

EOF
}

main() {
    case "${1:-}" in
        --system-only)
            log_info "Installing system dependencies only..."
            if [[ "$OSTYPE" == "linux-gnu"* ]]; then
                install_debian_deps
            elif [[ "$OSTYPE" == "darwin"* ]]; then
                install_macos_deps
            fi
            install_yq
            ;;
        --python-only)
            log_info "Installing Python dependencies only..."
            install_python_deps
            ;;
        --yq-only)
            install_yq
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        "")
            detect_and_install
            ;;
        *)
            log_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac

    echo ""
    log_info "✅ All dependencies installed successfully!"
    log_info "You can now run: ./compile.sh manuscript"
}

main "$@"
