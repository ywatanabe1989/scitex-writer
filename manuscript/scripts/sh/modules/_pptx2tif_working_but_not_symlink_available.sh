#!/bin/bash

echo -e "$0 ...\n"

inputFilePath=$1 # must be fullpath

echo -e "\nConverting ${inputFilePath}..."

inputFilePathWin=$(wslpath -w "$inputFilePath")

if [ "$#" -eq 2 ]; then
    outputFilePath=$2
    outputFilePathWin=$(wslpath -w "$outputFilePath")
else
    outputFilePathWin=${inputFilePathWin%.pptx}.tif
fi

# Run the PowerShell script
powershell.exe -ExecutionPolicy Bypass -File "$(wslpath -w ./scripts/ps1/pptx2tiff.ps1)" -inputFilePath "$inputFilePathWin" -outputFilePath "$outputFilePathWin"


if [ -n "$inputFilePath" ]; then
   echo -e "\nConverted: ${inputFilePath} -> ${inputFilePath%.pptx}.tif"
fi

# ./scripts/sh/modules/pptx2tif.sh /home/ywatanabe/proj/ripple-wm/paper/manuscript/src/figures/src/Figure_10_vSWR_jump.pptx 

## EOF
