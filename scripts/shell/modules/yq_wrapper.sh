#!/bin/bash
# Universal yq wrapper - handles both Python and Go versions
# Provides consistent interface regardless of which yq is installed

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" >&2
}

log_debug() {
    if [[ "${YQ_DEBUG:-}" == "1" ]]; then
        echo -e "${GREEN}[DEBUG]${NC} $1" >&2
    fi
}

detect_yq_type() {
    if ! command -v yq &> /dev/null; then
        log_error "yq not found. Please install yq first."
        log_error "  Go version: https://github.com/mikefarah/yq"
        log_error "  Or run: requirements/install.sh --yq-only"
        return 2
    fi

    # Check version string
    local version_output
    version_output=$(yq --version 2>&1)

    if echo "$version_output" | grep -q "mikefarah"; then
        echo "go"
        return 0
    elif echo "$version_output" | grep -qi "kislyuk\|jq"; then
        echo "python"
        return 0
    else
        # Feature detection fallback
        if echo 'test: value' | yq eval '.test = "new"' - &>/dev/null 2>&1; then
            echo "go"
            return 0
        elif echo 'test: value' | yq -y '.test = "new"' - &>/dev/null 2>&1; then
            echo "python"
            return 0
        else
            log_error "Unknown yq version. Cannot determine type."
            return 1
        fi
    fi
}

yq_set() {
    local file="$1"
    local path="$2"
    local value="$3"

    if [[ -z "$file" ]] || [[ -z "$path" ]] || [[ -z "$value" ]]; then
        log_error "Usage: yq_set <file> <path> <value>"
        return 1
    fi

    if [[ ! -f "$file" ]]; then
        log_error "File not found: $file"
        return 1
    fi

    local yq_type
    yq_type=$(detect_yq_type) || return $?

    log_debug "Detected yq type: $yq_type"
    log_debug "Setting $path = \"$value\" in $file"

    case "$yq_type" in
        go)
            yq eval -i "${path} = \"${value}\"" "$file"
            ;;
        python)
            local temp_file="${file}.tmp.$$"
            yq -y "${path} = \"${value}\"" "$file" > "$temp_file"
            mv "$temp_file" "$file"
            ;;
        *)
            log_error "Unknown yq type: $yq_type"
            return 1
            ;;
    esac
}

yq_get() {
    local file="$1"
    local path="$2"

    if [[ -z "$file" ]] || [[ -z "$path" ]]; then
        log_error "Usage: yq_get <file> <path>"
        return 1
    fi

    if [[ ! -f "$file" ]]; then
        log_error "File not found: $file"
        return 1
    fi

    local yq_type
    yq_type=$(detect_yq_type) || return $?

    log_debug "Detected yq type: $yq_type"
    log_debug "Getting $path from $file"

    case "$yq_type" in
        go)
            yq eval "$path" "$file"
            ;;
        python)
            yq -r "$path" "$file"
            ;;
        *)
            log_error "Unknown yq type: $yq_type"
            return 1
            ;;
    esac
}

yq_delete() {
    local file="$1"
    local path="$2"

    if [[ -z "$file" ]] || [[ -z "$path" ]]; then
        log_error "Usage: yq_delete <file> <path>"
        return 1
    fi

    if [[ ! -f "$file" ]]; then
        log_error "File not found: $file"
        return 1
    fi

    local yq_type
    yq_type=$(detect_yq_type) || return $?

    log_debug "Detected yq type: $yq_type"
    log_debug "Deleting $path from $file"

    case "$yq_type" in
        go)
            yq eval -i "del(${path})" "$file"
            ;;
        python)
            local temp_file="${file}.tmp.$$"
            yq -y "del(${path})" "$file" > "$temp_file"
            mv "$temp_file" "$file"
            ;;
        *)
            log_error "Unknown yq type: $yq_type"
            return 1
            ;;
    esac
}

yq_merge() {
    local file1="$1"
    local file2="$2"
    local output="$3"

    if [[ -z "$file1" ]] || [[ -z "$file2" ]]; then
        log_error "Usage: yq_merge <file1> <file2> [output_file]"
        return 1
    fi

    if [[ ! -f "$file1" ]] || [[ ! -f "$file2" ]]; then
        log_error "Input files not found"
        return 1
    fi

    local yq_type
    yq_type=$(detect_yq_type) || return $?

    log_debug "Detected yq type: $yq_type"
    log_debug "Merging $file1 and $file2"

    case "$yq_type" in
        go)
            if [[ -n "$output" ]]; then
                yq eval-all '. as $item ireduce ({}; . * $item)' "$file1" "$file2" > "$output"
            else
                yq eval-all '. as $item ireduce ({}; . * $item)' "$file1" "$file2"
            fi
            ;;
        python)
            log_warn "Merge operation not fully supported with Python yq"
            log_warn "Consider installing Go-based yq: requirements/install.sh --yq-only"
            if [[ -n "$output" ]]; then
                yq -y -s '.[0] * .[1]' "$file1" "$file2" > "$output"
            else
                yq -y -s '.[0] * .[1]' "$file1" "$file2"
            fi
            ;;
        *)
            log_error "Unknown yq type: $yq_type"
            return 1
            ;;
    esac
}

show_usage() {
    cat << EOF
Usage: $0 <command> <args...>

Universal yq wrapper - works with both Python and Go versions of yq

COMMANDS:
    set <file> <path> <value>     Set a value in YAML file
    get <file> <path>              Get a value from YAML file
    delete <file> <path>           Delete a key from YAML file
    merge <file1> <file2> [out]    Merge two YAML files
    detect                         Detect which yq version is installed

EXAMPLES:
    $0 set config.yaml '.citation.style' 'unsrtnat'
    $0 get config.yaml '.citation.style'
    $0 delete config.yaml '.old_key'
    $0 merge base.yaml override.yaml output.yaml
    $0 detect

ENVIRONMENT:
    YQ_DEBUG=1    Enable debug output

EOF
}

main() {
    case "${1:-}" in
        set)
            shift
            yq_set "$@"
            ;;
        get)
            shift
            yq_get "$@"
            ;;
        delete|del)
            shift
            yq_delete "$@"
            ;;
        merge)
            shift
            yq_merge "$@"
            ;;
        detect)
            local yq_type
            yq_type=$(detect_yq_type) || exit $?
            echo "Detected yq type: $yq_type"
            yq --version
            ;;
        -h|--help|help)
            show_usage
            exit 0
            ;;
        "")
            log_error "No command specified"
            show_usage
            exit 1
            ;;
        *)
            log_error "Unknown command: $1"
            show_usage
            exit 1
            ;;
    esac
}

main "$@"
