<!-- ---
!-- Timestamp: 2025-05-06 07:06:12
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/SciTex/docs/FROM_OPENAI.md
!-- --- -->

Root Cause and Solution: Figures Not Rendering in PDF After ./compile -m -- -f
1. Root Cause: Figure Rendering/Caption Extraction Logic
Findings
Your figure images and captions exist and are processed.
The compilation log and script output show:
Figures are processed, .jpg and .tex files are generated in the correct places.
The correct number of Figure_ID_*.tex files appears in contents/figures/compiled/.
The figure processing scripts run many times (possibly from repeated calls).
The gather_tex_files() function in process_figures.sh is responsible for concatenating the compiled figures into .All_Figures.tex.
Compilation succeeds, but the produced PDF is missing captions/legends or has broken formatting.
Key Problem:

Figure captions are not being rendered correctly alongside the images—LaTeX compiles but with missing or broken captions and sometimes missing graphics.
Over-iteration or repeated processing is polluting the debug/compiled directory and may result in unpredictable merge order or missed updates.
Shell scripts for extracting TeX between \caption{...} and } can go wrong with multi-line captions, nested braces, or non-standard formatting.
The final .All_Figures.tex is generated, but the code that reads/extracts the caption/title and produces the LaTeX figure* block is inconsistent/fragile.
2. Immediate Solution Steps
(A) Improve Caption Extraction:
Instead of relying on regex/sed/awk for extracting the caption, use a more robust multiline parser for \caption{...\n...} blocks. Bash tools often fail on nested braces or multi-line content.
Example Bash Function for Robust Extraction:
extract_caption_contents() {
    local infile="$1"
    awk '
    /\\caption{/ {flag=1; sub(/.*\\caption{\s*/, ""); caption=""; next}
    flag && /}/ {
        sub(/}\s*$/, "");
        caption = caption $0;
        print caption;
        exit
    }
    flag {caption = caption $0 "\n"}
    ' "$infile"
}
Then inside the figure compiling loop:

caption_content=$(extract_caption_contents "$caption_file" | sed '/^%/d')
(B) Always Use the Correct Figure Path and Width
Confirm that for each figure, you use:
\includegraphics[width=xxx]{.../Figure_ID_XX_example.jpg}
...and that the width is parsed correctly from any % width=... line.
(C) Do NOT wrap the figure in extra {} or emit malformed LaTeX
Each compiled figure file (in compiled/) should look like this:
\clearpage
\begin{figure*}[p]
    \pdfbookmark[2]{ID 01}{figure_id_01}
    \centering
    \includegraphics[width=0.95\textwidth]{./contents/figures/contents/jpg/Figure_ID_01_example.jpg}
    \caption{\textbf{
    Example figure showing the SciTex system workflow
    }
    \smallskip
    \\
    The figure illustrates the key components...
    }
    \label{fig:01}
\end{figure*}
NO JSON blocks, curly braces without context, or missing required fields!
(D) Do Not Repeatedly Regenerate Fig/Caption Files Over and Over
The logs show that all the steps run dozens of times per compile; this can produce racing or messy output. Limit main loop to a single pass per figure.
3. Patch for process_figures.sh—Key Block
Update the compile_legends function to ensure:

Robust capture of the caption (prefer awk, or at worst, a multi-line sed trick).
One figure per page using \clearpage and [p] as the float specifier.
NO JSON at the top or inline—keep it purely LaTeX!
Sample fixed snippet:

compile_legends() {
    # Create figures in the correct format
    local ii=0
    for caption_file in "$FIGURE_SRC_DIR"/Figure_ID_*.tex; do
        [ -f "$caption_file" ] || continue
        local fname=$(basename "$caption_file")
        local tgt_file="$STXW_FIGURE_COMPILED_DIR/$fname"
        local basename_noext="${fname%.tex}"
        local jpg_file="$STXW_FIGURE_JPG_DIR/$basename_noext.jpg"
        # Extract figure number
        local fig_number=$(echo "$fname" | sed -n 's/^Figure_ID_\([0-9][0-9]\).*\.tex$/\1/p')
        [ -n "$fig_number" ] || fig_number="$basename_noext"

        # Extract width from caption file (fallback to 1\textwidth)
        local width="1\\textwidth"
        local width_line=$(grep -oP '(?<=width=)[0-9.]+\\textwidth' "$caption_file" | head -1)
        [ -n "$width_line" ] && width=$width_line

        # Robust caption content extraction
        local caption_content
        caption_content=$(awk '/\\caption\{/ {flag=1; next} flag; /}/ {flag=0}' "$caption_file" | sed 's/^}//' | sed '/^$/d')

        # Compose compiled figure file
        cat > "$tgt_file" <<EOF
\clearpage
\begin{figure*}[p]
    \pdfbookmark[2]{ID $fig_number}{figure_id_$fig_number}
    \centering
    \includegraphics[width=$width]{$jpg_file}
    \caption{\textbf{
$caption_content
    }
    }
    \label{fig:$fig_number}
\end{figure*}
EOF
    done
}
4. Best Practices and Sanity Checks
After you compile, spot-check the generated files:
contents/figures/compiled/Figure_ID_0X_example.tex — does it consist of exactly the correct LaTeX block above?
contents/figures/.tex/.All_Figures.tex should \input{} each compiled figure file, one per line.
The main.tex (or the main/manuscript.tex) should \input{contents/figures/.tex/.All_Figures.tex} in its "Figures" section.
After running, check a few figure captions in the PDF to confirm it's working as desired.
Test with multi-line captions, special characters, etc.
If you have TikZ or vector figures, handle them in separate branches.
5. Summary: What Needs Fixing
Fix extraction of caption content in your shell scripts (process_figures.sh → compile_legends).
Be robust to multi-line and nested braces.
Ensure every compiled figure file is a standalone valid LaTeX block (as above).
Only allow a single, non-JSON LaTeX fragment per file for inclusion.
Limit figure processing to one pass.
6. Optional Future: Switch to Python for Figure Processing
If shell regex logic keeps getting gnarly, write a Python script that:

Loads each Figure_ID_*.tex caption,
Robustly extracts all {} block contents using a stack parser,
Assembles the LaTeX file with correct \includegraphics and formatting,
Writes out compiled/Figure_ID_*.tex.
If you make these changes, you will see all figures and captions rendered correctly in the final PDF produced by ./compile -m -- -f.
If you want a PR or working code sample for your repo, just ask!

<!-- EOF -->