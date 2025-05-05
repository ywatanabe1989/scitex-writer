#!/bin/bash
# Complete workflow example for SciTex

# Exit on error
set -e

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Check if the environment variable is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Error: OPENAI_API_KEY environment variable is not set."
    echo "Please set it with: export OPENAI_API_KEY=\"your_api_key\""
    exit 1
fi

# Create temporary directory
TMP_DIR=$(mktemp -d)
echo "Created temporary directory: $TMP_DIR"

# Copy sample files to temporary directory
echo "Copying sample files..."
cp -r "$ROOT_DIR/manuscript/scripts/py/tests/fixtures/sample_tex.tex" "$TMP_DIR/document.tex"
cp -r "$ROOT_DIR/manuscript/scripts/py/tests/fixtures/sample_bib.bib" "$TMP_DIR/references.bib"

# Change to the root directory
cd "$ROOT_DIR"

# Step 1: Check terminology
echo -e "\n=== Step 1: Checking Terminology ==="
python "$SCRIPT_DIR/check_terms.py" --input "$TMP_DIR/document.tex" --verbose

# Step 2: Revise the document
echo -e "\n=== Step 2: Revising Document ==="
python "$SCRIPT_DIR/basic_revision.py" --input "$TMP_DIR/document.tex" --verbose

# Step 3: Insert citations
echo -e "\n=== Step 3: Inserting Citations ==="
python "$SCRIPT_DIR/insert_citations.py" --input "$TMP_DIR/document.tex" --bib "$TMP_DIR/references.bib" --verbose

# Step 4: Compile the document (simulated)
echo -e "\n=== Step 4: Compiling Document ==="
echo "Simulating LaTeX compilation..."
echo "pdflatex $TMP_DIR/document.tex"
echo "bibtex $TMP_DIR/document"
echo "pdflatex $TMP_DIR/document.tex"
echo "pdflatex $TMP_DIR/document.tex"

# Show the final document
echo -e "\n=== Final Document ==="
cat "$TMP_DIR/document.tex"

# Clean up
echo -e "\n=== Cleaning Up ==="
echo "Temporary files are in: $TMP_DIR"
echo "You can delete them with: rm -rf $TMP_DIR"

echo -e "\n=== Workflow Complete ==="