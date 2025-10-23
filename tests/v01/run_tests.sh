#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-03 15:10:18 (ywatanabe)"
# File: ./run_tests.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
touch "$LOG_PATH" >/dev/null 2>&1


# PATH Configurations
LOG_PATH_TMP="$THIS_DIR/.$(basename $0).log-tmp"
PYTEST_INI_PATH="$THIS_DIR/tests/pytest.ini"

# Default Values
DELETE_CACHE=false
SYNC_TESTS_WITH_SOURCE=false
VERBOSE=false
SPECIFIC_TEST=""
ROOT_DIR=$THIS_DIR
# N_WORKERS=$(nproc)
# if [ $? -ne 0 ]; then
#     N_WORKERS=$(sysctl -n hw.ncpu 2>/dev/null || echo 1)
# fi
# N_WORKERS=$((N_WORKERS * 2 / 4))  # Use 50% of cores
N_WORKERS=1
N_RUNS=1


usage() {
    echo "Usage: $0 [options] [test_path]"
    echo
    echo "Options:"
    echo "  -c, --cache        Delete Python cache files (default: $DELETE_CACHE)"
    echo "  -s, --sync         Sync tests directory with source (default: $SYNC_TESTS_WITH_SOURCE)"
    echo "  -n, --n_runs       Number of test executions (default: $N_RUNS)"
    echo "  -j, --n_workers    Number of workers (default: $N_WORKERS, auto-parallel if >1)"
    echo "  -v, --verbose      Run tests in verbose mode (default: $VERBOSE)"
    echo "  -h, --help         Display this help message"
    echo
    echo "Arguments:"
    echo "  test_path          Optional path to specific test file or directory"
    echo
    echo "Example:"
    echo "  $0 -c              Clean cache before running tests"
    echo "  $0 -n 10           Run tests 10 times in sequence"
    echo "  $0 -j 4            Run tests in parallel with 4 workers"
    echo "  $0 tests/mngs/core Run only tests in core module"
    exit 1
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -c|--cache)
                DELETE_CACHE=true
                shift
                ;;
            -s|--sync)
                SYNC_TESTS_WITH_SOURCE=true
                shift
                ;;
            -n|--n_workers)
                N_RUNS="$2"
                shift 2
                ;;
            -j|--n_workers)
                N_WORKERS="$2"
                shift 2
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -h|--help)
                usage
                ;;
            *)
                if [[ -e "$1" ]]; then
                    SPECIFIC_TEST="$1"
                    shift
                else
                    echo "Unknown option or file not found: $1"
                    usage
                fi
                ;;
        esac
    done
}

check_existing_runtests_processes() {
    # Get only processes that contain run_tests.sh in the command, excluding grep itself and the current process
    existing_processes=$(ps aux | grep "run_tests.sh" | grep -v "grep" | grep -v $$ | awk '{print $2}')

    if [ -n "$existing_processes" ]; then
        echo "Found existing run_tests.sh processes:"
        for pid in $existing_processes; do
            # Double check if process actually exists
            if ps -p $pid > /dev/null; then
                echo "PID: $pid"
                return 1
            fi
        done
    fi

    # No legitimate processes found
    return 0
}

kill_existing_runtests_processes() {
    existing_pids=$(ps aux | grep "run_tests.sh" | grep -v "grep" | grep -v $$ | awk '{print $2}')
    if [ -n "$existing_pids" ]; then
        echo "Killing existing run_tests.sh processes: $existing_pids"
        kill -9 $existing_pids 2>/dev/null
    fi
}

clear_cache() {
    echo "Cleaning Python cache..."
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc*" -type f -exec rm -f {} + 2>/dev/null || true
}

remove_python_output_directories() {
    echo "Delete Python output directories..."
    find "./tests/" -name "test_*_out" -type d -exec rm -rf {} + 2>/dev/null || true
}

sync_tests_with_source() {
    echo "Updating test structure..."
    "$THIS_DIR/tests/sync_tests_with_source.sh"
}

run_tests() {
    PYTEST_ARGS="-c $PYTEST_INI_PATH"

    cat "$PYTEST_INI_PATH" | tee -a "$LOG_PATH_TMP"

    # PYTEST_ARGS="$PYTEST_ARGS --no-header --no-summary -q"
    # # Add these options for simpler output
    # PYTEST_ARGS="$PYTEST_ARGS --no-header --no-summary -q"

    # # Only show failures
    # PYTEST_ARGS="$PYTEST_ARGS -xvs"

    # # For even more concise output, add this
    # PYTEST_ARGS="$PYTEST_ARGS --tb=short"

    # Timestamp
    date >> "$LOG_PATH_TMP" 2>&1

    # ROOT DIR
    if [[ -n $ROOT_DIR ]]; then
        echo "ROOT_DIR: $ROOT_DIR"
        PYTEST_ARGS="$PYTEST_ARGS --rootdir $ROOT_DIR"
    fi

    # N_WORKERS
    if [[ $N_WORKERS -gt 1 ]]; then
        echo "Running in parallel mode with $N_WORKERS workers"
        PYTEST_ARGS="$PYTEST_ARGS -n $N_WORKERS"
    fi

    # # VERBOSE
    # if [[ $VERBOSE == true ]]; then
    #     PYTEST_ARGS="$PYTEST_ARGS -v"
    # fi

    # SPECIFIC TEST
    if [[ -n "$SPECIFIC_TEST" ]]; then
        echo "Running specific test: $SPECIFIC_TEST"
        PYTEST_ARGS="$PYTEST_ARGS $SPECIFIC_TEST"
    fi

    # Main
    echo "Running pytest..."
    pytest $PYTEST_ARGS | tee -a "$LOG_PATH_TMP" 2>&1
}

main() {
    kill_existing_runtests_processes
    remove_python_output_directories
    if check_existing_runtests_processes; then
        echo "No existing processes found. Continuing execution."
        parse_args "$@"

        for i_run in `seq 1 $N_RUNS`; do
            # clear

            # Clear the temporary log file
            > "$LOG_PATH_TMP"

            echo "LOG_PATH: $LOG_PATH" | tee -a "$LOG_PATH_TMP"
            echo "LOG_PATH_TMP: $LOG_PATH_TMP" | tee -a "$LOG_PATH_TMP"
            echo "Test run $i_run of $N_RUNS" | tee -a "$LOG_PATH_TMP"


            # Clear cache
            if [[ $DELETE_CACHE == true ]]; then clear_cache; fi

            # Synchronize test code with source
            if [[ $SYNC_TESTS_WITH_SOURCE == true ]]; then sync_tests_with_source; fi

            # Main
            run_tests

            # Update the latest log symlink
            cat "$LOG_PATH_TMP" > "$LOG_PATH"
            sleep 1

        done

    else
        echo "Exiting to avoid multiple instances."
        exit 1
    fi

}

# Execute main function with all arguments
main "$@"

# EOF