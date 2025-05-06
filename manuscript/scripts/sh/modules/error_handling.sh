#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-06 10:15:00 (ywatanabe)"
# File: ./manuscript/scripts/sh/modules/error_handling.sh

# Set default values for log files if not already defined
DEFAULT_LOG_DIR="./.logs"
DEFAULT_ERROR_LOG="${DEFAULT_LOG_DIR}/errors.log"
DEFAULT_DEBUG_LOG="${DEFAULT_LOG_DIR}/debug.log"

# Ensure log directory exists
mkdir -p "$DEFAULT_LOG_DIR"

# Color codes for terminal output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging levels
declare -A LOG_LEVELS=(
  ["DEBUG"]=0
  ["INFO"]=1
  ["WARNING"]=2
  ["ERROR"]=3
  ["CRITICAL"]=4
)

# Default log level - can be overridden by setting SCITEX_LOG_LEVEL
: ${SCITEX_LOG_LEVEL:="INFO"}

# Check if current log level allows output
should_log() {
  local requested_level=$1
  if [[ ${LOG_LEVELS[$requested_level]} -ge ${LOG_LEVELS[$SCITEX_LOG_LEVEL]} ]]; then
    return 0
  else
    return 1
  fi
}

# Logging function
log() {
  local level=$1
  local message=$2
  local log_file=$3
  local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
  
  if should_log "$level"; then
    # Terminal output with colors
    case $level in
      "DEBUG")
        echo -e "${BLUE}[DEBUG] $timestamp - $message${NC}" ;;
      "INFO")
        echo -e "[INFO] $timestamp - $message" ;;
      "WARNING")
        echo -e "${YELLOW}[WARNING] $timestamp - $message${NC}" ;;
      "ERROR")
        echo -e "${RED}[ERROR] $timestamp - $message${NC}" ;;
      "CRITICAL")
        echo -e "${RED}[CRITICAL] $timestamp - $message${NC}" ;;
    esac
  fi
  
  # Always log to file if specified
  if [[ -n "$log_file" ]]; then
    echo "[$level] $timestamp - $message" >> "$log_file"
  fi
}

# Convenience logging functions
log_debug() {
  log "DEBUG" "$1" "${2:-$DEFAULT_DEBUG_LOG}"
}

log_info() {
  log "INFO" "$1" "${2:-$DEFAULT_DEBUG_LOG}"
}

log_warning() {
  log "WARNING" "$1" "${2:-$DEFAULT_DEBUG_LOG}"
}

log_error() {
  log "ERROR" "$1" "${2:-$DEFAULT_ERROR_LOG}"
}

log_critical() {
  log "CRITICAL" "$1" "${2:-$DEFAULT_ERROR_LOG}"
}

# Error handling function that can be used with trap
handle_error() {
  local exit_code=$?
  local line_number=$1
  local command="$2"
  local script_name="$3"
  
  if [[ $exit_code -ne 0 ]]; then
    log_critical "Error in $script_name at line $line_number: Command '$command' exited with status $exit_code"
    # You can add additional error handling here, e.g., cleanup, notifications, etc.
  fi
}

# Setup error trapping for a script
setup_error_trap() {
  local script_name=$(basename "$0")
  trap 'handle_error ${LINENO} "$BASH_COMMAND" "$script_name"' ERR
}

# Function to check prerequisites
check_prerequisite() {
  local cmd=$1
  local package=$2  # Optional package name if different from command
  package=${package:-$cmd}
  
  if ! command -v "$cmd" &> /dev/null; then
    log_error "Required command '$cmd' not found. Please install it using 'sudo apt-get install $package' (or the appropriate method for your system)."
    return 1
  fi
  return 0
}

# Function to check multiple prerequisites at once
check_prerequisites() {
  local failed=0
  for cmd in "$@"; do
    if ! check_prerequisite "$cmd"; then
      failed=1
    fi
  done
  
  if [[ $failed -eq 1 ]]; then
    log_critical "One or more required dependencies are missing. Please install them and try again."
    return 1
  fi
  return 0
}

# Function to run a command with error checking
run_command() {
  local cmd="$1"
  local description="$2"
  local log_file="${3:-$DEFAULT_DEBUG_LOG}"
  
  log_info "Running: $description" "$log_file"
  
  if eval "$cmd" >> "$log_file" 2>&1; then
    log_info "Successfully completed: $description" "$log_file"
    return 0
  else
    local exit_code=$?
    log_error "Failed: $description (exit code: $exit_code)" "$DEFAULT_ERROR_LOG"
    log_error "Command was: $cmd" "$DEFAULT_ERROR_LOG"
    return $exit_code
  fi
}

# Run a command with output displayed and logged
run_command_verbose() {
  local cmd="$1"
  local description="$2"
  local log_file="${3:-$DEFAULT_DEBUG_LOG}"
  
  log_info "Running: $description" "$log_file"
  
  # Run command and tee output to both terminal and log file
  if eval "$cmd" 2>&1 | tee -a "$log_file"; then
    log_info "Successfully completed: $description" "$log_file"
    return 0
  else
    local exit_code=$?
    log_error "Failed: $description (exit code: $exit_code)" "$DEFAULT_ERROR_LOG"
    log_error "Command was: $cmd" "$DEFAULT_ERROR_LOG"
    return $exit_code
  fi
}

# Print a section header for better script output organization
print_section_header() {
  local title="$1"
  local width=50
  local padding=$(( (width - ${#title} - 2) / 2 ))
  local line=$(printf '%*s' "$width" | tr ' ' '=')
  
  echo -e "\n$line"
  printf "%*s%s%*s\n" $padding "" "$title" $padding ""
  echo -e "$line\n"
}

# Print success message
print_success() {
  local message="$1"
  echo -e "${GREEN}$message${NC}"
}

# Print warning message
print_warning() {
  local message="$1"
  echo -e "${YELLOW}$message${NC}"
}

# Print error message
print_error() {
  local message="$1"
  echo -e "${RED}$message${NC}"
}

# EOF