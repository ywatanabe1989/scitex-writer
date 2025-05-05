#!/bin/bash
# Simple compilation script for the example manuscript template

# Ensure we're in the right directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Create needed directories
mkdir -p main
mkdir -p src/figures/.tex
mkdir -p src/tables/.tex
mkdir -p src/figures/src/jpg

echo "Compiling example manuscript template..."

# Process figures
echo "Processing figures..."
for tex_file in src/figures/src/Figure_ID_*.tex; do
    if [ -f "$tex_file" ]; then
        # Get the basename
        base_name=$(basename "$tex_file" .tex)
        
        # Create a simple compiled version
        compiled_file="src/figures/compiled/$base_name.tex"
        
        # Extract width
        width=$(grep -oP '(?<=width=)[0-9.]+\\textwidth' "$tex_file" || echo "0.8\\textwidth")
        
        # Create compiled file
        cat > "$compiled_file" << EOF
\\begin{figure}[ht]
    \\centering
    \\fbox{[$base_name]}
    \\input{src/figures/src/$base_name}
    \\label{fig:$(echo $base_name | grep -oP 'Figure_ID_\K[0-9]+')}
\\end{figure}
EOF
    fi
done

# Gather figures
echo "" > src/figures/.tex/.All_Figures.tex
for compiled_file in src/figures/compiled/Figure_ID_*.tex; do
    if [ -f "$compiled_file" ]; then
        echo "\\input{$compiled_file}" >> src/figures/.tex/.All_Figures.tex
    fi
done

# Process tables
echo "Processing tables..."
for tex_file in src/tables/src/Table_ID_*.tex; do
    if [ -f "$tex_file" ] && [ "$(basename "$tex_file")" != "_Table_ID_XX.tex" ]; then
        # Get the basename
        base_name=$(basename "$tex_file" .tex)
        
        # Create a simple compiled version
        compiled_file="src/tables/src/compiled_$base_name.tex"
        
        # Extract width
        width=$(grep -oP '(?<=width=)[0-9.]+\\textwidth' "$tex_file" || echo "0.8\\textwidth")
        
        # Create compiled file
        cat > "$compiled_file" << EOF
\\begin{table}[ht]
    \\centering
    \\fbox{[$base_name]}
    \\input{$tex_file}
    \\label{tab:$(echo $base_name | grep -oP 'Table_ID_\K[0-9]+')}
\\end{table}
EOF
    fi
done

# Gather tables
echo "" > src/tables/.tex/.All_Tables.tex
for compiled_file in src/tables/src/compiled_Table_ID_*.tex; do
    if [ -f "$compiled_file" ]; then
        echo "\\input{$compiled_file}" >> src/tables/.tex/.All_Tables.tex
    fi
done

# Run PDFLaTeX
echo "Running PDFLaTeX..."
pdflatex -interaction=nonstopmode main.tex && \
bibtex main && \
pdflatex -interaction=nonstopmode main.tex && \
pdflatex -interaction=nonstopmode main.tex

# Move output files
if [ -f main.pdf ]; then
    mv main.pdf main/manuscript.pdf
    echo "Success! Output file is at main/manuscript.pdf"
else
    echo "Error: Compilation failed. Check the log file."
fi

# Clean up
echo "Cleaning up temporary files..."
rm -f main.aux main.log main.out main.bbl main.blg