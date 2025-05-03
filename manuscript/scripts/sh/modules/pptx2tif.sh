#!/bin/bash
# (pptx2tif.sh)
# Author: ywatanabe (ywatanabe@alumni.u-tokyo.ac.jp)
# Date: 2023-06-09-12-00

LOG_FILE="${0%.sh}.log"

usage() {
    echo "Usage: $0 [-i|--input INPUT_FILE] [-o|--output OUTPUT_FILE] [-h|--help]"
    echo
    echo "Options:"
    echo " -i, --input    Input PPTX file path (required)"
    echo " -o, --output   Output TIF file path (optional)"
    echo " -h, --help     Display this help message"
    echo
    echo "Example:"
    echo " $0 -i /path/to/input.pptx"
    echo " $0 -i /path/to/input.pptx -o /path/to/output.tif"
    exit 1
}

convert_pptx_to_tif() {
    local input_file="$1"
    local output_file="$2"

    local input_file_win=$(wslpath -w "$input_file")
    local output_file_win=$(wslpath -w "$output_file")
    local script_dir="$(dirname "$(realpath "$0")")"
    local ps_script="./scripts/ps1/pptx2tiff.ps1"    
    local powershell=/home/ywatanabe/.win-bin/powershell.exe
    
    echo -e "\nConverting ${input_file}...\n"

    if [ ! -f "$powershell" ]; then
        echo "Error: PowerShell executable not found at $powershell"
        exit 1
    fi

    if [ ! -f "$ps_script" ]; then
        echo "Error: PowerShell script not found at $ps_script"
        exit 1
    fi
        
    if [ ! -f "$input_file" ]; then
        echo "Error: Input file does not exist."
        exit 1
    fi

    "$powershell" -ExecutionPolicy Bypass -File "$ps_script" -inputFilePath "$input_file_win" -outputFilePath "$output_file_win" 2>&1

    # "$powershell" -ExecutionPolicy Bypass -File "$(wslpath -w ./scripts/ps1/pptx2tiff.ps1)" -inputFilePath "$input_file_win" -outputFilePath "$output_file_win" 2>&1
    ps_exit_code=$?

    if [ $ps_exit_code -ne 0 ]; then
        echo -e "\nError: PowerShell script failed with exit code $ps_exit_code"
        return 1
    fi

    if [ -f "$output_file" ]; then
        echo -e "\nConverted: ${input_file} -> ${output_file}"
    else
        echo -e "\nError: Conversion failed. Output file not created."
        return 1
    fi
}

main() {
    local input_file
    local output_file

    while [[ $# -gt 0 ]]; do
        case $1 in
            -i|--input)
                input_file="$2"
                shift 2
                ;;
            -o|--output)
                output_file="$2"
                shift 2
                ;;
            -h|--help)
                usage
                ;;
            *)
                echo "Unknown option: $1"
                usage
                ;;
        esac
    done

    if [ -z "$input_file" ]; then
        echo "Error: Input file is required."
        usage
    fi

    if [ -z "$output_file" ]; then
        output_file="${input_file%.pptx}.tif"
    fi

    convert_pptx_to_tif "$input_file" "$output_file"
}

{ main "$@" ; } 2>&1 | tee "$LOG_FILE"

# ./scripts/sh/modules/pptx2tif.sh -i /home/ywatanabe/proj/ripple-wm/paper/manuscript/src/figures/src/Figure_ID_10_vswr_jump.pptx

# EOF
