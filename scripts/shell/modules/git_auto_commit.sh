#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-12 (ywatanabe)"
# File: ./scripts/shell/modules/git_auto_commit.sh
# Description: Git auto-commit module for version control

# Load version control configuration
if [ -f "./config/version_control.conf" ]; then
    source ./config/version_control.conf
fi

# Logging functions (if not already defined)
if ! command -v echo_info &> /dev/null; then
    GRAY='\033[0;90m'
    GREEN='\033[0;32m'
    YELLOW='\033[0;33m'
    RED='\033[0;31m'
    NC='\033[0m'
    echo_info() { echo -e "${GRAY}INFO: $1${NC}"; }
    echo_success() { echo -e "${GREEN}SUCC: $1${NC}"; }
    echo_warning() { echo -e "${YELLOW}WARN: $1${NC}"; }
    echo_error() { echo -e "${RED}ERRO: $1${NC}"; }
fi

# Main git auto-commit function
git_auto_commit() {
    # Check if git auto-commit is enabled
    if [[ "$GIT_AUTO_COMMIT_ENABLED" != "true" ]]; then
        return 0
    fi

    echo_info "    Git auto-commit: Starting..."

    # Verify we're in a git repository
    if ! git rev-parse --git-dir &>/dev/null; then
        echo_warning "    Not a git repository, skipping auto-commit"
        return 0
    fi

    # Get document type and version
    local doc_type="${SCITEX_WRITER_DOC_TYPE:-unknown}"
    local version_file="${SCITEX_WRITER_VERSION_COUNTER_TXT}"

    if [ ! -f "$version_file" ]; then
        echo_warning "    Version counter not found: $version_file"
        return 1
    fi

    # Read ONLY the first line (version number)
    local version="$(head -n 1 "$version_file" | tr -d '[:space:]')"
    local version_tag="v${version}"

    # Build list of ONLY the files created/modified by this compilation
    # This ensures atomic, minimal commits
    local files_to_commit=()
    local archive_dir="${SCITEX_WRITER_VERSIONS_DIR}"

    echo_info "    Building atomic commit (only files from this compilation)..."

    # 1. Add the 4 archived files for this specific version ONLY
    local archive_base="${archive_dir}/${doc_type}_v${version}"
    [ -f "${archive_base}.pdf" ] && files_to_commit+=("${archive_base}.pdf")
    [ -f "${archive_base}.tex" ] && files_to_commit+=("${archive_base}.tex")
    [ -f "${archive_base}_diff.pdf" ] && files_to_commit+=("${archive_base}_diff.pdf")
    [ -f "${archive_base}_diff.tex" ] && files_to_commit+=("${archive_base}_diff.tex")

    # 2. Add the version counter file (this was modified)
    [ -f "$version_file" ] && files_to_commit+=("$version_file")

    # 3. Add cleanup history file if it exists and was just modified
    local cleanup_log="${archive_dir}/.cleanup_history.txt"
    if [ -f "$cleanup_log" ]; then
        # Only add if modified in last 5 seconds (just created by cleanup)
        if [ $(($(date +%s) - $(stat -c %Y "$cleanup_log" 2>/dev/null || echo 0))) -lt 5 ]; then
            files_to_commit+=("$cleanup_log")
        fi
    fi

    # Verify we have files to commit
    if [ ${#files_to_commit[@]} -eq 0 ]; then
        echo_warning "    No archive files found to commit"
        return 0
    fi

    # Check if files exist and have changes
    local files_with_changes=()
    for file in "${files_to_commit[@]}"; do
        if [ -f "$file" ]; then
            # Check if file is new or modified
            if ! git ls-files --error-unmatch "$file" &>/dev/null || \
               ! git diff --quiet HEAD -- "$file" 2>/dev/null; then
                files_with_changes+=("$file")
            fi
        fi
    done

    if [ ${#files_with_changes[@]} -eq 0 ]; then
        echo_info "    No changes to commit (files unchanged)"
        return 0
    fi

    echo_info "    Committing ${#files_with_changes[@]} files (preserving staging area)..."

    # Create commit message
    local msg="${GIT_COMMIT_MESSAGE_TEMPLATE//%DOC_TYPE%/$doc_type}"
    msg="${msg//%VERSION%/$version_tag}"

    # Add detailed information with file list
    local commit_body="
Auto-generated during compilation.

Document: ${doc_type}
Version: ${version_tag}
Timestamp: $(date '+%Y-%m-%d %H:%M:%S')
User: $(git config user.name 2>/dev/null || echo 'unknown')

Files committed (atomic):
"

    # Add list of committed files
    for file in "${files_with_changes[@]}"; do
        commit_body="${commit_body}  - ${file}
"
    done

    # Set commit author if specified in config
    local author_args=""
    if [ -n "$GIT_COMMIT_AUTHOR_NAME" ] && [ -n "$GIT_COMMIT_AUTHOR_EMAIL" ]; then
        author_args="--author=\"$GIT_COMMIT_AUTHOR_NAME <$GIT_COMMIT_AUTHOR_EMAIL>\""
    fi

    # CRITICAL: For new untracked files, we need to add them first
    # Then commit ONLY those files (not other staged files)
    # Ref: https://git-scm.com/docs/git-commit

    # First, add only the files we want to commit
    # Use -f (force) to add files that might be in .gitignore
    local add_success=true
    for file in "${files_with_changes[@]}"; do
        if ! git add -f -- "$file" 2>/dev/null; then
            echo_warning "    Failed to add: $file"
            add_success=false
        fi
    done

    if [ "$add_success" != "true" ]; then
        echo_error "    Some files failed to stage, aborting commit"
        return 1
    fi

    # Now commit ONLY these specific files
    # Build an array of file arguments for git commit
    local commit_args=()
    for file in "${files_with_changes[@]}"; do
        commit_args+=("$file")
    done

    # Perform the commit using the array
    if git commit "${commit_args[@]}" -m "$msg" -m "$commit_body" $author_args >> "$LOG_PATH" 2>&1; then
        echo_success "    Git commit: ${doc_type} ${version_tag}"

        # Create git tag if enabled
        if [[ "$GIT_TAG_ENABLED" == "true" ]]; then
            local tag="${GIT_TAG_PREFIX//%DOC_TYPE%/$doc_type}${version_tag}"

            # Check if tag already exists
            if git rev-parse "$tag" >/dev/null 2>&1; then
                echo_warning "    Tag already exists: $tag"
            else
                if git tag -a "$tag" -m "Auto-tag: ${doc_type} ${version_tag}" >> "$LOG_PATH" 2>&1; then
                    echo_success "    Git tag: $tag"
                else
                    echo_warning "    Failed to create tag: $tag"
                fi
            fi
        fi

        # Push to remote if enabled
        if [[ "$GIT_PUSH_ENABLED" == "true" ]]; then
            local push_remote="${GIT_PUSH_REMOTE:-origin}"
            local push_branch="${GIT_PUSH_BRANCH:-$(git branch --show-current)}"

            echo_info "    Pushing to remote: $push_remote/$push_branch"
            if git push "$push_remote" "$push_branch" 2>&1 | tee -a "$LOG_PATH"; then
                echo_success "    Git push succeeded"

                # Push tags if enabled
                if [[ "$GIT_TAG_ENABLED" == "true" ]]; then
                    git push "$push_remote" --tags 2>&1 | tee -a "$LOG_PATH" || true
                fi
            else
                echo_warning "    Git push failed (continuing anyway)"
            fi
        fi

        return 0
    else
        echo_error "    Git commit failed"
        if [[ "$FAIL_ON_GIT_ERROR" == "true" ]]; then
            return 1
        else
            echo_warning "    Continuing despite git error (FAIL_ON_GIT_ERROR=false)"
            return 0
        fi
    fi
}

# Export function for use in other scripts
export -f git_auto_commit

# EOF
