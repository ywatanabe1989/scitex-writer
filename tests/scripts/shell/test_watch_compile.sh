#!/bin/bash
# -*- coding: utf-8 -*-
# Test file for: watch_compile.sh

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(realpath "$THIS_DIR/../..")"

# Test counter
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

assert_success() {
    local cmd="$1"
    local desc="${2:-$cmd}"
    ((TESTS_RUN++))
    if eval "$cmd" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $desc"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} $desc"
        ((TESTS_FAILED++))
    fi
}

assert_file_exists() {
    local file="$1"
    ((TESTS_RUN++))
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} File exists: $file"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} File missing: $file"
        ((TESTS_FAILED++))
    fi
}

# Add your tests here
test_placeholder() {
    echo "TODO: Add tests for watch_compile.sh"
}

# Run tests
main() {
    echo "Testing: watch_compile.sh"
    echo "========================================"

    test_placeholder

    echo "========================================"
    echo "Results: $TESTS_PASSED/$TESTS_RUN passed"
    [ $TESTS_FAILED -gt 0 ] && exit 1
    exit 0
}

main "$@"

# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/scitex-writer/scripts/shell/watch_compile.sh
# --------------------------------------------------------------------------------
# #!/bin/bash
# # -*- coding: utf-8 -*-
# # Timestamp: "$(date '+%Y-%m-%d %H:%M:%S') ($(whoami))"
# # File: ./paper/scripts/shell/watch_compile.sh
# 
# # Hot-recompile script with file watching and lock management
# 
# ORIG_DIR="$(pwd)"
# THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
# PROJECT_ROOT="$(cd "$THIS_DIR/../.." && pwd)"
# 
# # Colors for output
# GIT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
# 
# GRAY='\033[0;90m'
# GREEN='\033[0;32m'
# YELLOW='\033[0;33m'
# RED='\033[0;31m'
# NC='\033[0m' # No Color
# 
# echo_info() { echo -e "${GRAY}INFO: $1${NC}"; }
# echo_success() { echo -e "${GREEN}SUCC: $1${NC}"; }
# echo_warning() { echo -e "${YELLOW}WARN: $1${NC}"; }
# echo_error() { echo -e "${RED}ERRO: $1${NC}"; }
# echo_header() { echo_info "=== $1 ==="; }
# # ---------------------------------------
# 
# # Lock file path
# LOCK_FILE="$PROJECT_ROOT/.compile.lock"
# WATCH_PID_FILE="$PROJECT_ROOT/.watch.pid"
# 
# # Function to check if compilation is locked
# is_locked() {
#     if [ -f "$LOCK_FILE" ]; then
#         local lock_pid=$(cat "$LOCK_FILE" 2>/dev/null)
#         # Check if the process is still running
#         if [ -n "$lock_pid" ] && kill -0 "$lock_pid" 2>/dev/null; then
#             return 0  # Locked and process is running
#         else
#             # Process is dead, remove stale lock
#             rm -f "$LOCK_FILE"
#             return 1
#         fi
#     fi
#     return 1  # Not locked
# }
# 
# # Function to acquire lock
# acquire_lock() {
#     local max_wait=60  # Maximum seconds to wait for lock
#     local waited=0
#     
#     while is_locked; do
#         if [ $waited -eq 0 ]; then
#             echo_warning "Compilation in progress, waiting for lock..."
#         fi
#         sleep 1
#         waited=$((waited + 1))
#         if [ $waited -ge $max_wait ]; then
#             echo_error "Timeout waiting for compilation lock"
#             return 1
#         fi
#     done
#     
#     # Create lock with our PID
#     echo $$ > "$LOCK_FILE"
#     return 0
# }
# 
# # Function to release lock
# release_lock() {
#     if [ -f "$LOCK_FILE" ]; then
#         local lock_pid=$(cat "$LOCK_FILE" 2>/dev/null)
#         if [ "$lock_pid" = "$$" ]; then
#             rm -f "$LOCK_FILE"
#         fi
#     fi
# }
# 
# # Cleanup function
# cleanup() {
#     echo_info "Stopping watch mode..."
#     release_lock
#     rm -f "$WATCH_PID_FILE"
#     exit 0
# }
# 
# # Trap signals for cleanup
# trap cleanup EXIT INT TERM
# 
# # Load configuration from YAML
# CONFIG_FILE="$PROJECT_ROOT/config/config_manuscript.yaml"
# 
# # Function to parse YAML value
# get_yaml_value() {
#     local key="$1"
#     local file="${2:-$CONFIG_FILE}"
#     grep "^$key:" "$file" | sed 's/^[^:]*:[[:space:]]*//' | sed 's/[[:space:]]*#.*//'
# }
# 
# # Function to get YAML array values
# get_yaml_array() {
#     local key="$1"
#     local file="${2:-$CONFIG_FILE}"
#     awk "/^$key:/{flag=1; next} /^[^ ]/{flag=0} flag && /^[[:space:]]*-/" "$file" | sed 's/^[[:space:]]*-[[:space:]]*//'
# }
# 
# # Load hot-recompile configuration
# # Note: YAML key uses "enabled" not "enable"
# HOT_RECOMPILE_ENABLED=$(awk '/^hot-recompile:/{flag=1} flag && /^[[:space:]]*enabled:/{print $2; exit}' "$CONFIG_FILE" | grep -o "true\|false")
# COMPILE_MODE="${1:-$(get_yaml_value "hot-recompile.mode")}"  # Use arg or config
# COMPILE_MODE="${COMPILE_MODE:-restart}"  # Default to restart if not specified
# STABLE_LINK=$(get_yaml_value "hot-recompile.stable_link")
# STABLE_LINK="${STABLE_LINK:-./01_manuscript/manuscript-latest.pdf}"
# 
# # Function to compile manuscript
# compile_with_lock() {
#     local compilation_start_file="$PROJECT_ROOT/.compile_start_time"
#     
#     # Check if compilation is running
#     if is_locked; then
#         local lock_pid=$(cat "$LOCK_FILE" 2>/dev/null)
#         
#         if [ "$COMPILE_MODE" = "restart" ]; then
#             # Check how long compilation has been running
#             if [ -f "$compilation_start_file" ]; then
#                 local start_time=$(cat "$compilation_start_file")
#                 local current_time=$(date +%s)
#                 local elapsed=$((current_time - start_time))
#                 
#                 if [ $elapsed -lt 3 ]; then
#                     # Just started, kill and restart
#                     echo_warning "$(date '+%H:%M:%S') - Stopping current compilation (just started)..."
#                     kill -TERM "$lock_pid" 2>/dev/null
#                     sleep 0.5
#                     rm -f "$LOCK_FILE" "$compilation_start_file"
#                 elif [ $elapsed -gt 15 ]; then
#                     # Taking too long, kill and restart
#                     echo_warning "$(date '+%H:%M:%S') - Stopping stuck compilation (>${elapsed}s)..."
#                     kill -TERM "$lock_pid" 2>/dev/null
#                     sleep 0.5
#                     rm -f "$LOCK_FILE" "$compilation_start_file"
#                 else
#                     # In the middle, let it finish
#                     echo_info "$(date '+%H:%M:%S') - Waiting for current compilation to finish (${elapsed}s elapsed)..."
#                     return 1
#                 fi
#             fi
#         else
#             # Wait mode
#             echo_warning "$(date '+%H:%M:%S') - Compilation in progress, waiting..."
#             return 1
#         fi
#     fi
#     
#     if acquire_lock; then
#         echo_info "$(date '+%H:%M:%S') - Starting compilation..."
#         date +%s > "$compilation_start_file"
#         cd "$PROJECT_ROOT"
#         ./compile -m
#         local status=$?
#         release_lock
#         rm -f "$compilation_start_file"
#         
#         if [ $status -eq 0 ]; then
#             echo_success "$(date '+%H:%M:%S') - Compilation successful"
#             # Load configuration to get environment variables
#             source ./config/load_config.sh manuscript >/dev/null 2>&1
# 
#             # Update symlink to latest archive version (prevents viewing corrupted PDFs during compilation)
#             local archive_dir="${SCITEX_WRITER_VERSIONS_DIR}"
#             local latest_archive=$(ls -1 "$archive_dir"/${SCITEX_WRITER_DOC_TYPE}_v[0-9]*.pdf 2>/dev/null | grep -v "_diff.pdf" | sort -V | tail -1)
# 
#             if [ -n "$latest_archive" ]; then
#                 # Create relative symlink to archive
#                 cd "${SCITEX_WRITER_ROOT_DIR}"
#                 ln -sf "archive/$(basename "$latest_archive")" "${SCITEX_WRITER_DOC_TYPE}-latest.pdf"
#                 cd - > /dev/null
#                 echo_info "    Symlink updated: ${SCITEX_WRITER_DOC_TYPE}-latest.pdf -> archive/$(basename "$latest_archive")"
#             else
#                 # Fallback if no archive exists
#                 cd "${SCITEX_WRITER_ROOT_DIR}"
#                 ln -sf "${SCITEX_WRITER_DOC_TYPE}.pdf" "${SCITEX_WRITER_DOC_TYPE}-latest.pdf"
#                 cd - > /dev/null
#                 echo_info "    Symlink updated: ${SCITEX_WRITER_DOC_TYPE}-latest.pdf -> ${SCITEX_WRITER_DOC_TYPE}.pdf (no archive yet)"
#             fi
#         else
#             echo_error "$(date '+%H:%M:%S') - Compilation failed"
#         fi
#         return $status
#     else
#         echo_warning "$(date '+%H:%M:%S') - Could not acquire lock"
#         return 1
#     fi
# }
# 
# # Function to get list of files to watch from config
# get_watch_files() {
#     # Read watch patterns from YAML config
#     local patterns=$(awk '/^  watching_files:/,/^[^ ]/' "$CONFIG_FILE" | \
#                     grep '^[[:space:]]*-' | \
#                     sed 's/^[[:space:]]*-[[:space:]]*//' | \
#                     sed 's/"//g')
#     
#     # Expand patterns and find matching files
#     for pattern in $patterns; do
#         # Skip comments
#         [[ "$pattern" =~ ^# ]] && continue
#         
#         # Expand the pattern (handles wildcards)
#         if [[ "$pattern" == *"**"* ]]; then
#             # Handle recursive patterns
#             local base_dir=$(echo "$pattern" | sed 's/\/\*\*.*//')
#             local file_pattern=$(echo "$pattern" | sed 's/.*\*\*\///')
#             find "$PROJECT_ROOT/$base_dir" -type f -name "$file_pattern" 2>/dev/null
#         elif [[ "$pattern" == *"*"* ]]; then
#             # Handle simple wildcards
#             ls $PROJECT_ROOT/$pattern 2>/dev/null
#         else
#             # Direct file
#             [ -f "$PROJECT_ROOT/$pattern" ] && echo "$PROJECT_ROOT/$pattern"
#         fi
#     done | sort -u
# }
# 
# # Main watch loop
# main() {
#     # Save PID for external monitoring
#     echo $$ > "$WATCH_PID_FILE"
#     
#     # Check if hot-recompile is enabled
#     if [ "$HOT_RECOMPILE_ENABLED" != "true" ]; then
#         echo_warning "Hot-recompile is disabled in config. Set hot-recompile.enabled: true to enable."
#         exit 0
#     fi
#     
#     # Count files being watched
#     local watch_count=$(get_watch_files | wc -l)
#     
#     echo_success "==========================================
# Hot-Recompile Watch Mode Started
# ==========================================
# Config: $CONFIG_FILE
# Mode: ${COMPILE_MODE} (use 'wait' or 'restart' as argument)
# Monitoring: $watch_count files from config patterns
# Stable PDF: $STABLE_LINK
# 
# For rsync: rsync -avL $STABLE_LINK remote:/path/
#            (The -L flag follows symlinks)
#   
# Press Ctrl+C to stop
# =========================================="
# 
#     # Initial compilation
#     compile_with_lock
#     
#     # Check for inotifywait (preferred) or fall back to polling
#     if command -v inotifywait >/dev/null 2>&1; then
#         echo_info "Using inotify for file watching (efficient)"
#         
#         # Watch for changes using inotify
#         while true; do
#             inotifywait -r -q -e modify,create,delete,move \
#                 "$PROJECT_ROOT/01_manuscript/contents/" \
#                 --exclude '(~$|\.swp$|\.tmp$|#.*#$|\.git)' \
#                 2>/dev/null
#             
#             # Small delay to batch rapid changes
#             sleep 0.5
#             
#             # Compile if not locked
#             compile_with_lock
#             
#             echo_info "$(date '+%H:%M:%S') - Waiting for changes..."
#         done
#     else
#         echo_warning "inotifywait not found, using polling mode (less efficient)"
#         echo_info "Install inotify-tools for better performance"
#         
#         # Polling fallback
#         declare -A file_times
#         
#         # Initialize file timestamps
#         while IFS= read -r file; do
#             if [ -f "$file" ]; then
#                 file_times["$file"]=$(stat -c %Y "$file" 2>/dev/null)
#             fi
#         done < <(get_watch_files)
#         
#         # Poll for changes
#         while true; do
#             changed=false
#             
#             while IFS= read -r file; do
#                 if [ -f "$file" ]; then
#                     current_time=$(stat -c %Y "$file" 2>/dev/null)
#                     if [ "${file_times[$file]}" != "$current_time" ]; then
#                         echo_info "Change detected: $file"
#                         file_times["$file"]=$current_time
#                         changed=true
#                     fi
#                 fi
#             done < <(get_watch_files)
#             
#             if [ "$changed" = true ]; then
#                 compile_with_lock
#                 echo_info "$(date '+%H:%M:%S') - Waiting for changes..."
#             fi
#             
#             sleep 2  # Poll interval
#         done
#     fi
# }
# 
# # Check if another watch instance is running
# if [ -f "$WATCH_PID_FILE" ]; then
#     old_pid=$(cat "$WATCH_PID_FILE" 2>/dev/null)
#     if [ -n "$old_pid" ] && kill -0 "$old_pid" 2>/dev/null; then
#         echo_error "Another watch instance is already running (PID: $old_pid)"
#         echo_info "Stop it first with: kill $old_pid"
#         exit 1
#     else
#         rm -f "$WATCH_PID_FILE"
#     fi
# fi
# 
# # Start watching
# main "$@"
# 
# # EOF
# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/scitex-writer/scripts/shell/watch_compile.sh
# --------------------------------------------------------------------------------
