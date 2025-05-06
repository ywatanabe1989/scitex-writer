#!/usr/bin/env bash
# Configuration loading utility for SciTex shell scripts
# This script uses yq to parse the YAML configuration file

# Default config file path
DEFAULT_CONFIG_PATH="$(dirname "$(dirname "$(dirname "$0")")")/config.yaml"

# Function to check if yq is installed
check_yq() {
    if ! command -v yq &> /dev/null; then
        echo "Error: 'yq' is required but not installed. Install it with:"
        echo "  pip install yq"
        echo "  or"
        echo "  go install github.com/mikefarah/yq/v4@latest"
        return 1
    fi
    return 0
}

# Function to get a configuration value using a key path
# Usage: get_config "latex.compiler"
get_config() {
    local key_path="$1"
    local default_value="$2"
    local config_path="${CONFIG_PATH:-$DEFAULT_CONFIG_PATH}"
    
    if [ ! -f "$config_path" ]; then
        echo "Warning: Config file not found: $config_path" >&2
        echo "Using default value: $default_value" >&2
        echo "$default_value"
        return 1
    fi
    
    # Check if yq is installed
    if ! check_yq; then
        echo "$default_value"
        return 1
    fi
    
    # Read the value using yq
    local value
    value=$(yq eval ".$key_path" "$config_path" 2>/dev/null)
    
    # Check if the value is null or empty
    if [ "$value" = "null" ] || [ -z "$value" ]; then
        echo "Warning: Key '$key_path' not found in config file" >&2
        echo "Using default value: $default_value" >&2
        echo "$default_value"
        return 1
    fi
    
    echo "$value"
    return 0
}

# Function to get a path from the configuration and resolve it
# Usage: get_config_path "paths.scripts_dir"
get_config_path() {
    local key_path="$1"
    local default_value="$2"
    local config_path="${CONFIG_PATH:-$DEFAULT_CONFIG_PATH}"
    local config_dir=$(dirname "$config_path")
    
    local value
    value=$(get_config "$key_path" "$default_value")
    
    # If the path is relative, make it relative to the config file directory
    if [[ "$value" != /* ]]; then
        value="$config_dir/$value"
    fi
    
    echo "$value"
}

# Function to load all core configuration values into environment variables
# This can be used to load commonly used values at the start of a script
load_core_config() {
    # Only proceed if yq is available
    if ! check_yq; then
        return 1
    fi
    
    local config_path="${CONFIG_PATH:-$DEFAULT_CONFIG_PATH}"
    
    # LaTeX configuration
    export SCITEX_LATEX_COMPILER=$(get_config "latex.compiler" "pdflatex")
    export SCITEX_LATEX_FLAGS=$(get_config "latex.flags" "-interaction=nonstopmode")
    export SCITEX_LATEX_MAX_RUNS=$(get_config "latex.max_runs" "3")
    
    # Path configuration
    export SCITEX_SCRIPTS_DIR=$(get_config_path "paths.scripts_dir" "./scripts")
    export SCITEX_PYTHON_SCRIPTS=$(get_config_path "paths.python_scripts" "./scripts/py")
    export SCITEX_SHELL_SCRIPTS=$(get_config_path "paths.shell_scripts" "./scripts/sh")
    export SCITEX_FIGURES_SRC=$(get_config_path "paths.figures_src" "./manuscript/src/figures/src")
    export SCITEX_FIGURES_COMPILED=$(get_config_path "paths.figures_compiled" "./manuscript/src/figures/compiled")
    export SCITEX_TABLES_SRC=$(get_config_path "paths.tables_src" "./manuscript/src/tables/src")
    export SCITEX_TABLES_COMPILED=$(get_config_path "paths.tables_compiled" "./manuscript/src/tables/compiled")
    
    # Figure configuration
    export SCITEX_FIGURE_DPI=$(get_config "figures.dpi" "300")
    
    # Logging configuration
    export SCITEX_LOG_LEVEL=$(get_config "logging.level" "info")
    
    return 0
}

# Usage example if this script is called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
        echo "SciTex Configuration Loader"
        echo "Usage:"
        echo "  . $(basename "$0")                     # Source this script to use functions"
        echo "  $(basename "$0") get KEY [DEFAULT]     # Get a single config value"
        echo "  $(basename "$0") path KEY [DEFAULT]    # Get a path from config"
        echo "  $(basename "$0") list                  # List all core config values"
        echo ""
        echo "Example:"
        echo "  $(basename "$0") get latex.compiler pdflatex"
        exit 0
    fi
    
    # Handle command line arguments
    if [ "$1" == "get" ] && [ -n "$2" ]; then
        get_config "$2" "${3:-}"
    elif [ "$1" == "path" ] && [ -n "$2" ]; then
        get_config_path "$2" "${3:-}"
    elif [ "$1" == "list" ]; then
        # Load all core variables then print them
        load_core_config
        echo "SciTex Configuration:"
        env | grep "^SCITEX_" | sort
    else
        echo "Unknown command. Use --help for usage information."
        exit 1
    fi
fi