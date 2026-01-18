#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-09 19:00:00 (ywatanabe)"
# File: ./scripts/maintenance/update.sh
# Description: Update scitex-writer while preserving user content

set -e

ORIG_DIR="$(pwd)"
THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
PROJECT_ROOT="$(cd $THIS_DIR/.. && pwd)"

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

# Read current version from pyproject.toml (single source of truth)
PYPROJECT_FILE="${PROJECT_ROOT}/pyproject.toml"
if [ -f "$PYPROJECT_FILE" ]; then
    if command -v yq &> /dev/null; then
        CURRENT_VERSION=$(yq -r '.project.version' "$PYPROJECT_FILE" 2>/dev/null || echo "unknown")
    else
        CURRENT_VERSION=$(grep '^version = ' "$PYPROJECT_FILE" | sed 's/version = "\(.*\)"/\1/' | head -1 | tr -d '"' | tr -d '[:space:]')
    fi
else
    CURRENT_VERSION="unknown"
fi

echo
echo_header "SciTeX Writer Update Tool"
echo_info "Current version: v${CURRENT_VERSION}"
echo

# Check if we're in a git repository
if [ ! -d "${PROJECT_ROOT}/.git" ]; then
    echo_error "Not a git repository. Please clone from GitHub:"
    echo_error "  git clone https://github.com/ywatanabe1989/scitex-writer.git"
    exit 1
fi

# Fetch latest changes
echo_info "Checking for updates..."
git fetch origin main 2>/dev/null || {
    echo_error "Failed to fetch updates. Check your network connection."
    exit 1
}

# Get remote version from pyproject.toml
REMOTE_VERSION=$(git show origin/main:pyproject.toml 2>/dev/null | grep '^version = ' | sed 's/version = "\(.*\)"/\1/' | head -1 | tr -d '"' | tr -d '[:space:]' || echo "unknown")
echo_info "Latest version: v${REMOTE_VERSION}"
echo

# Check if update is needed
if [ "$CURRENT_VERSION" == "$REMOTE_VERSION" ]; then
    echo_success "Already up to date (v${CURRENT_VERSION})"
    exit 0
fi

# Show what will be updated
echo_warning "Update available: v${CURRENT_VERSION} → v${REMOTE_VERSION}"
echo
echo_info "What will be updated:"
echo_info "  ✓ scripts/         (shell scripts)"
echo_info "  ✓ config/          (configuration files)"
echo_info "  ✓ docs/            (documentation)"
echo_info "  ✓ Makefile         (build system)"
echo_info "  ✓ VERSION          (version file)"
echo
echo_info "What will be preserved:"
echo_info "  ✓ 01_manuscript/contents/    (your manuscript)"
echo_info "  ✓ 02_supplementary/contents/ (your supplementary)"
echo_info "  ✓ 03_revision/contents/      (your revision)"
echo_info "  ✓ 00_shared/bib_files/          (your bibliography)"
echo_info "  ✓ archive/                   (your archived versions)"
echo

# Ask for confirmation
read -p "Proceed with update? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo_info "Update cancelled."
    exit 0
fi

# Create backup
BACKUP_DIR="${PROJECT_ROOT}/.backup_$(date +%Y%m%d_%H%M%S)"
echo_info "Creating backup at: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# Backup critical user files
echo_info "Backing up user content..."
for dir in 01_manuscript/contents 02_supplementary/contents 03_revision/contents 00_shared/bib_files archive; do
    if [ -d "${PROJECT_ROOT}/$dir" ]; then
        mkdir -p "$BACKUP_DIR/$(dirname $dir)"
        cp -r "${PROJECT_ROOT}/$dir" "$BACKUP_DIR/$dir" 2>/dev/null || true
    fi
done

# Check for local modifications
if ! git diff --quiet || ! git diff --cached --quiet; then
    echo_warning "You have local modifications."
    echo_info "Stashing local changes..."
    git stash push -m "Auto-stash before update to v${REMOTE_VERSION}"
    STASHED=true
else
    STASHED=false
fi

# Update system files
echo_info "Updating system files..."
git checkout origin/main -- scripts/ config/ docs/ Makefile pyproject.toml src/ 2>/dev/null || {
    echo_error "Failed to update files."
    if [ "$STASHED" = true ]; then
        git stash pop
    fi
    exit 1
}

# Update templates (but not user content)
echo_info "Updating templates..."
for doc_type in 01_manuscript 02_supplementary 03_revision; do
    # Update structure but preserve contents/
    git checkout origin/main -- \
        ${doc_type}/base.tex \
        ${doc_type}/compiled/ \
        ${doc_type}/diff/ \
        2>/dev/null || true
done

# Restore stashed changes if any
if [ "$STASHED" = true ]; then
    echo_info "Restoring your local changes..."
    if git stash pop; then
        echo_success "Local changes restored"
    else
        echo_warning "Conflicts detected. Please resolve manually:"
        echo_warning "  git status"
        echo_warning "  git stash list"
    fi
fi

# Verify update by reading from pyproject.toml
if [ -f "$PYPROJECT_FILE" ]; then
    if command -v yq &> /dev/null; then
        NEW_VERSION=$(yq -r '.project.version' "$PYPROJECT_FILE" 2>/dev/null || echo "unknown")
    else
        NEW_VERSION=$(grep '^version = ' "$PYPROJECT_FILE" | sed 's/version = "\(.*\)"/\1/' | head -1 | tr -d '"' | tr -d '[:space:]')
    fi
else
    NEW_VERSION="unknown"
fi
echo
if [ "$NEW_VERSION" == "$REMOTE_VERSION" ]; then
    echo_success "Successfully updated to v${NEW_VERSION}!"
    echo
    echo_info "Backup created at: $BACKUP_DIR"
    echo_info "You can remove it once you verify everything works."
    echo
    echo_info "Next steps:"
    echo_info "  1. Test compilation: ./compile.sh"
    echo_info "  2. Review changes: git log v${CURRENT_VERSION}..v${NEW_VERSION}"
    echo_info "  3. Remove backup if all looks good: rm -rf $BACKUP_DIR"
else
    echo_error "Update verification failed."
    echo_error "Expected v${REMOTE_VERSION}, got v${NEW_VERSION}"
    exit 1
fi

# EOF
