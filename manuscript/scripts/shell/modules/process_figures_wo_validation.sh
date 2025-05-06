#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-06 23:39:00 (ywatanabe)"
# File: ./manuscript/scripts/shell/modules/process_figures.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
touch "$LOG_PATH" >/dev/null 2>&1


source ./config.src
echo_info "$0 ..."

init_figures() {
    local timestamp=$(date +"%Y%m%d_%H%M%S")

    mkdir -p \
          "$FIGURE_CAPTION_MEDIA_DIR" \
	      "$FIGURE_COMPILED_DIR" \
	      "$FIGURE_JPG_DIR"

    rm -f \
       "$FIGURE_COMPILED_DIR"/Figure_ID_*.tex

    echo > $FIGURE_COMPILED_FILE
}

ensure_caption() {
    for img_file in "$FIGURE_CAPTION_MEDIA_DIR"/Figure_ID_*.{tif,jpg,png,svg}; do
        [ -e "$img_file" ] || continue
        local ext="${img_file##*.}"
        local filename=$(basename "$img_file")
        local caption_tex_file="$FIGURE_CAPTION_MEDIA_DIR/${filename%.$ext}.tex"

        if [ ! -f "$caption_tex_file" ] && [ ! -L "$caption_tex_file" ]; then
            if [ -f "$FIGURE_CAPTION_MEDIA_DIR/templates/_Figure_ID_XX.tex" ]; then
                cp "$FIGURE_CAPTION_MEDIA_DIR/templates/_Figure_ID_XX.tex" "$caption_tex_file"
            elif [ -f "$FIGURE_CAPTION_MEDIA_DIR/_Figure_ID_XX.tex" ]; then
                cp "$FIGURE_CAPTION_MEDIA_DIR/_Figure_ID_XX.tex" "$caption_tex_file"
            else
                cat <<EOF > "$caption_tex_file"
%% -*- coding: utf-8 -*-
%% Timestamp: "$(date +"%Y-%m-%d %H:%M:%S") (ywatanabe)"
%% File: "$caption_tex_file"
\caption{\textbf{
FIGURE TITLE HERE
}
\smallskip
\\
FIGURE LEGEND HERE.
}
% width=0.95\textwidth
%%%% EOF
EOF
            fi
        fi

        if [ "$ext" = "jpg" ]; then
            if [ ! -f "$FIGURE_JPG_DIR/$filename" ]; then
                cp "$img_file" "$FIGURE_JPG_DIR/"
            fi
        elif [ "$ext" = "png" ]; then
            local jpg_filename="${filename%.png}.jpg"
            if [ ! -f "$FIGURE_JPG_DIR/$jpg_filename" ]; then
                convert "$img_file" -density 300 -quality 90 "$FIGURE_JPG_DIR/$jpg_filename"
            fi
        elif [ "$ext" = "svg" ]; then
            local jpg_filename="${filename%.svg}.jpg"
            if [ ! -f "$FIGURE_JPG_DIR/$jpg_filename" ]; then
                if command -v inkscape >/dev/null 2>&1; then
                    inkscape -z -e "$FIGURE_JPG_DIR/$jpg_filename" -w 1200 -h 1200 "$img_file"
                else
                    convert "$img_file" -density 300 -quality 90 "$FIGURE_JPG_DIR/$jpg_filename"
                fi
            fi
        fi
    done
}

ensure_lower_letter_id() {
    local ORIG_DIR="$(pwd)"
    cd "$FIGURE_CAPTION_MEDIA_DIR"
    for file in Figure_ID_*; do
        if [[ -f "$file" || -L "$file" ]]; then
            new_name=$(echo "$file" | sed -E 's/(Figure_ID_)(.*)/\1\L\2/')
            if [[ "$file" != "$new_name" ]]; then
                mv "$file" "$new_name"
            fi
        fi
    done
    cd $ORIG_DIR
}

pptx2tif() {
    local p2t="$1"
    if [[ "$p2t" == true ]]; then
        ./scripts/shell/modules/pptx2tif_all.sh
    fi
}

crop_tif() {
    local no_figs="$1"
    if [[ "$no_figs" == false ]]; then
        echo "Skipping crop_tif step for demonstration"
    fi
}

tif2jpg() {
    local no_figs="$1"

    if [[ "$no_figs" == false ]]; then
        echo "Processing images (tif2jpg)..."

        if [ -f "./scripts/python/optimize_figure.py" ] && command -v python3 >/dev/null 2>&1; then
            find "$FIGURE_CAPTION_MEDIA_DIR" -name "Figure_ID_*.tif" | parallel -j+0 --eta '
                python3 ./scripts/python/optimize_figure.py --input {} --output "'"$FIGURE_JPG_DIR"'/$(basename {} .tif).jpg" --dpi 300 --quality 95
            '

            find "$FIGURE_CAPTION_MEDIA_DIR" -name "Figure_ID_*.png" | parallel -j+0 --eta '
                python3 ./scripts/python/optimize_figure.py --input {} --output "'"$FIGURE_JPG_DIR"'/$(basename {} .png).jpg" --dpi 300 --quality 95
            '

            if command -v inkscape >/dev/null 2>&1; then
                find "$FIGURE_CAPTION_MEDIA_DIR" -name "Figure_ID_*.svg" | parallel -j+0 --eta '
                    inkscape -z -e "'"$FIGURE_JPG_DIR"'/$(basename {} .svg)_temp.png" -w 1200 -h 1200 {}
                    python3 ./scripts/python/optimize_figure.py --input "'"$FIGURE_JPG_DIR"'/$(basename {} .svg)_temp.png" --output "'"$FIGURE_JPG_DIR"'/$(basename {} .svg).jpg" --dpi 300 --quality 95
                    rm -f "'"$FIGURE_JPG_DIR"'/$(basename {} .svg)_temp.png"
                '
            else
                find "$FIGURE_CAPTION_MEDIA_DIR" -name "Figure_ID_*.svg" | parallel -j+0 --eta '
                    convert {} -density 300 -quality 95 "'"$FIGURE_JPG_DIR"'/$(basename {} .svg).jpg"
                '
            fi

            find "$FIGURE_CAPTION_MEDIA_DIR" -name "Figure_ID_*.jpg" | parallel -j+0 --eta '
                if [ ! -f "'"$FIGURE_JPG_DIR"'/$(basename {})" ]; then
                    python3 ./scripts/python/optimize_figure.py --input {} --output "'"$FIGURE_JPG_DIR"'/$(basename {})" --dpi 300 --quality 95
                fi
            '
        else
            find "$FIGURE_CAPTION_MEDIA_DIR" -name "Figure_ID_*.tif" | parallel -j+0 --eta '
                convert {} -density 300 -quality 95 "'"$FIGURE_JPG_DIR"'/$(basename {} .tif).jpg"
            '

            find "$FIGURE_CAPTION_MEDIA_DIR" -name "Figure_ID_*.png" | parallel -j+0 --eta '
                convert {} -density 300 -quality 95 "'"$FIGURE_JPG_DIR"'/$(basename {} .png).jpg"
            '

            find "$FIGURE_CAPTION_MEDIA_DIR" -name "Figure_ID_*.svg" | parallel -j+0 --eta '
                convert {} -density 300 -quality 95 "'"$FIGURE_JPG_DIR"'/$(basename {} .svg).jpg"
            '

            find "$FIGURE_CAPTION_MEDIA_DIR" -name "Figure_ID_*.jpg" | parallel -j+0 --eta '
                if [ ! -f "'"$FIGURE_JPG_DIR"'/$(basename {})" ]; then
                    cp {} "'"$FIGURE_JPG_DIR"'/$(basename {})"
                fi
            '
        fi
    fi
}

compile_legends() {
    mkdir -p "$FIGURE_COMPILED_DIR"
    rm -f "$FIGURE_COMPILED_DIR"/Figure_ID_*.tex

    local figures_header_file="$FIGURE_COMPILED_DIR/00_Figures_Header.tex"
    cat > "$figures_header_file" << "EOF"
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% FIGURES
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% \clearpage
\section*{Figures}
\label{figures}
\pdfbookmark[1]{Figures}{figures}
EOF

    for caption_file in "$FIGURE_CAPTION_MEDIA_DIR"/Figure_ID_*.tex; do
        [ -f "$caption_file" ] || continue

        local fname=$(basename "$caption_file")
        local figure_id=""

        if [[ "$fname" =~ Figure_ID_([^\.]+) ]]; then
            figure_id="${BASH_REMATCH[1]}"
        else
            continue
        fi

        local figure_id_clean=$(echo "$figure_id" | sed 's/\.jpg$//')
        local figure_number=""

        if [[ "$figure_id_clean" =~ ^([0-9]+)_ ]]; then
            figure_number="${BASH_REMATCH[1]}"
        else
            figure_number="$figure_id_clean"
        fi

        local tgt_file="$FIGURE_COMPILED_DIR/$fname"
        local is_tikz=false

        if grep -q "\\\\begin{tikzpicture}" "$caption_file"; then
            is_tikz=true
        fi

        local jpg_file=""
        if [[ "$fname" == *".jpg.tex" ]]; then
            jpg_file="${fname%.tex}"
        else
            jpg_file="${fname%.tex}.jpg"
        fi

        local width="1\\textwidth"
        local width_spec=$(grep -o "width=.*\\\\textwidth" "$caption_file" | head -1)

        if [ -n "$width_spec" ]; then
            width=$(echo "$width_spec" | sed 's/width=//')
        fi

        local caption_content=""

        if grep -q "\\\\caption{" "$caption_file"; then
            caption_raw=$(sed -n '/\\caption{/,/^}\s*$/p' "$caption_file" | sed '1s/^\\caption{//' | sed '$s/}\s*$//')
            caption_content=$(echo "$caption_raw" | grep -v "\\\\label{" | sed '/^$/d' | sed 's/^[ \t]*//' | sed 's/[ \t]*$//')
        else
            caption_content=$(cat "$caption_file" | grep -v "^%" | grep -v "^$" | sed 's/^[ \t]*//' | sed 's/[ \t]*$//')
        fi

        if [ -z "$caption_content" ]; then
            caption_content="\\textbf{Figure $figure_number.} No caption available."
        fi

        if [ "$is_tikz" = true ]; then
            local tikz_begin_line=$(grep -n "\\\\begin{tikzpicture}" "$caption_file" | cut -d: -f1)
            local tikz_end_line=$(grep -n "\\\\end{tikzpicture}" "$caption_file" | cut -d: -f1)

            if [ -n "$tikz_begin_line" ] && [ -n "$tikz_end_line" ]; then
                local tikz_code=$(sed -n "${tikz_begin_line},${tikz_end_line}p" "$caption_file")

                cat > "$tgt_file" << EOF
% FIGURE METADATA - Figure ID ${figure_id_clean}, Number ${figure_number}
% FIGURE TYPE: TikZ
% This is not a standalone LaTeX environment - it will be included by compile_figure_tex_files
{
    "id": "${figure_id_clean}",
    "number": "${figure_number}",
    "type": "tikz",
    "width": "$width",
    "tikz_code": "$tikz_code"
}
$caption_content
EOF
            else
                cat > "$tgt_file" << EOF
% FIGURE METADATA - Figure ID ${figure_id_clean}, Number ${figure_number}
% FIGURE TYPE: Image
% This is not a standalone LaTeX environment - it will be included by compile_figure_tex_files
{
    "id": "${figure_id_clean}",
    "number": "${figure_number}",
    "type": "image",
    "width": "$width",
    "path": "$FIGURE_JPG_DIR/$jpg_file"
}
$caption_content
EOF
            fi
        else
            cat > "$tgt_file" << EOF
% FIGURE METADATA - Figure ID ${figure_id_clean}, Number ${figure_number}
% FIGURE TYPE: Image
% This is not a standalone LaTeX environment - it will be included by compile_figure_tex_files
{
    "id": "${figure_id_clean}",
    "number": "${figure_number}",
    "type": "image",
    "width": "$width",
    "path": "$FIGURE_JPG_DIR/$jpg_file"
}
$caption_content
EOF
        fi
    done
}

_toggle_figures() {
    local action=$1

    if [ ! -d "$FIGURE_COMPILED_DIR" ]; then
        mkdir -p "$FIGURE_COMPILED_DIR"
        return 0
    fi

    if [[ ! -n $(find "$FIGURE_COMPILED_DIR" -name "Figure_ID_*.tex" 2>/dev/null) ]]; then
        return 0
    fi

    if [[ $action == "disable" ]]; then
        sed -i 's/^\(\s*\)\\includegraphics/%\1\\includegraphics/g' "$FIGURE_COMPILED_DIR"/Figure_ID_*.tex
    else
        mkdir -p "$FIGURE_JPG_DIR"

        find "$FIGURE_CAPTION_MEDIA_DIR" -name "*.jpg" | while read src_jpg; do
            base_jpg=$(basename "$src_jpg")
            if [ ! -f "$FIGURE_JPG_DIR/$base_jpg" ]; then
                cp "$src_jpg" "$FIGURE_JPG_DIR/"
            fi
        done

        for fig_tex in "$FIGURE_COMPILED_DIR"/Figure_ID_*.tex; do
            [ -e "$fig_tex" ] || continue

            local fname=$(basename "$fig_tex")
            local jpg_file=""

            if [[ "$fname" == *".jpg.tex" ]]; then
                jpg_file="${fname%.tex}"
            else
                jpg_file="${fname%.tex}.jpg"
            fi

            if [ -f "$FIGURE_JPG_DIR/$jpg_file" ]; then
                local width_spec=$(grep -o "width=.*\\\\textwidth" "$fig_tex" | head -1 | sed 's/width=//')

                if [[ -z "$width_spec" ]]; then
                    width_spec="1\\\\textwidth"
                fi

                if [[ ! "$width_spec" == *"\\textwidth"* ]]; then
                    if [[ "$width_spec" =~ ^[0-9]+(\.[0-9]+)?$ ]]; then
                        width_spec="${width_spec}\\\\textwidth"
                    fi
                fi

                sed -i 's/^%\(\s*\\includegraphics\)/\1/g' "$fig_tex"
                sed -i "s|\\\\includegraphics\[width=[^]]*\]{[^}]*}|\\\\includegraphics[width=$width_spec]{$FIGURE_JPG_DIR/$jpg_file}|g" "$fig_tex"
                sed -i "s|\\\\includegraphics\[width=\]{|\\\\includegraphics[width=$width_spec]{|g" "$fig_tex"
                sed -i "s|\\\\includegraphics\[width=.*extwidth\]{|\\\\includegraphics[width=$width_spec]{|g" "$fig_tex"
                sed -i 's/\\begin{figure\*}\[[^\]]*\]/\\begin{figure\*}[ht]/g' "$fig_tex"
            fi
        done
    fi
}

handle_figure_visibility() {
    local no_figs="$1"
    if [[ "$no_figs" == true ]]; then
        _toggle_figures disable
    else
        tif2jpg "$no_figs"
        [[ -n $(find "$FIGURE_JPG_DIR" -name "*.jpg") ]] && _toggle_figures enable || _toggle_figures disable
    fi
}


compile_figure_tex_files() {
    echo "% Generated by compile_figure_tex_files() on $(date)" > "$FIGURE_COMPILED_FILE"
    echo "% This file includes all figure files in order" >> "$FIGURE_COMPILED_FILE"
    echo "" >> "$FIGURE_COMPILED_FILE"

    # Variable to track if we're on the first figure
    local first_figure=true

    for fig_tex in $(find "$FIGURE_COMPILED_DIR" -maxdepth 1 -name "Figure_ID_*.tex" | sort); do
        [ -e "$fig_tex" ] || continue
        local basename=$(basename "$fig_tex")
        local figure_id=""
        local figure_number=""
        local figure_title=""
        local image_path=""
        local width="0.9\\\\textwidth"
        local figure_type="image"
        local caption_content=""
        if [[ "$basename" =~ Figure_ID_([^\.]+) ]]; then
            figure_id="${BASH_REMATCH[1]}"
            if [[ "$figure_id" =~ ^([0-9]+)_ ]]; then
                figure_number="${BASH_REMATCH[1]}"
            else
                figure_number="$figure_id"
            fi
        fi
        if grep -q "^{" "$fig_tex"; then
            if grep -q '"path":' "$fig_tex"; then
                image_path=$(grep -o '"path": *"[^"]*"' "$fig_tex" | sed 's/"path": *"\(.*\)"/\1/')
            fi
            if grep -q '"width":' "$fig_tex"; then
                width=$(grep -o '"width": *"[^"]*"' "$fig_tex" | sed 's/"width": *"\(.*\)"/\1/')
            fi
            if grep -q '"type":' "$fig_tex"; then
                figure_type=$(grep -o '"type": *"[^"]*"' "$fig_tex" | sed 's/"type": *"\(.*\)"/\1/')
            fi
            caption_content=$(sed -n '/^}/,$p' "$fig_tex" | tail -n +2 | sed 's/^[ \t]*//' | sed '/^$/d')
            if [[ "$caption_content" =~ \\textbf\{([^}]*)\} ]]; then
                figure_title="${BASH_REMATCH[1]}"
            fi
        else
            image_path=$(grep -o "\\\\includegraphics\[.*\]{[^}]*}" "$fig_tex" | grep -o "{[^}]*}" | tr -d "{}")
            width_spec=$(grep -o "width=[^,\]}]*" "$fig_tex" | sed 's/width=//' | head -1)
            if [ -n "$width_spec" ]; then
                width="$width_spec"
            fi
            figure_title=$(sed -n '/\\caption{/,/}/p' "$fig_tex" | grep -A1 "\\\\textbf{" | sed -n 's/.*\\textbf{\(.*\)}.*/\1/p' | tr -d '\n' | xargs)
            caption_content=$(sed -n '/\\caption{/,/}/p' "$fig_tex" | sed '1s/^\\caption{//' | sed '$s/}\s*$//')
        fi
        if [[ -n "$image_path" && ! "$image_path" =~ ^[./] ]]; then
            image_path="./$image_path"
        fi
        if [ -z "$figure_title" ]; then
            if [[ "$caption_content" =~ \\textbf\{([^}]*)\} ]]; then
                figure_title="${BASH_REMATCH[1]}"
            else
                figure_title="Figure $figure_number"
            fi
        fi
        local original_caption_file="$FIGURE_CAPTION_MEDIA_DIR/${basename}"
        if [ -f "$original_caption_file" ]; then
            local original_caption=$(sed -n '/\\caption{/,/^}\s*$/p' "$original_caption_file" | sed '1s/^\\caption{//' | sed '$s/}\s*$//')
            if [ -n "$original_caption" ]; then
                caption_content="$original_caption"
            fi
        fi
        local caption_text=""
        if [[ "$caption_content" =~ \\textbf\{.*\}(.*) ]]; then
            caption_text="${BASH_REMATCH[1]}"
            caption_text=$(echo "$caption_text" | grep -v "^%" | sed 's/^[ \t]*//' | sed 's/[ \t]*$//')
        fi
        if [ -z "$caption_text" ]; then
            caption_text="Description for figure $figure_number."
        fi
        echo "% Figure $figure_number: ${figure_title}" >> "$FIGURE_COMPILED_FILE"

        # Only add \clearpage for figures after the first one
        if [ "$first_figure" = true ]; then
            first_figure=false
        else
            echo "\\clearpage" >> "$FIGURE_COMPILED_FILE"
        fi

        echo "\\begin{figure*}[p]" >> "$FIGURE_COMPILED_FILE"
        echo "    \\pdfbookmark[2]{Figure $figure_number}{figure_id_$figure_number}" >> "$FIGURE_COMPILED_FILE"
        echo "    \\centering" >> "$FIGURE_COMPILED_FILE"
        if [ "$figure_type" = "tikz" ]; then
            local tikz_code=$(grep -A100 "\\\\begin{tikzpicture}" "$fig_tex" | sed -n '/\\begin{tikzpicture}/,/\\end{tikzpicture}/p')
            if [ -n "$tikz_code" ]; then
                echo "$tikz_code" >> "$FIGURE_COMPILED_FILE"
            else
                if [ -n "$image_path" ]; then
                    echo "    \\includegraphics[width=$width]{$image_path}" >> "$FIGURE_COMPILED_FILE"
                fi
            fi
        else
            if [ -n "$image_path" ]; then
                echo "    \\includegraphics[width=$width]{$image_path}" >> "$FIGURE_COMPILED_FILE"
            fi
        fi
        echo "    \\caption{" >> "$FIGURE_COMPILED_FILE"
        echo "\\textbf{" >> "$FIGURE_COMPILED_FILE"
        echo "$figure_title" >> "$FIGURE_COMPILED_FILE"
        echo "}" >> "$FIGURE_COMPILED_FILE"
        echo "\\smallskip" >> "$FIGURE_COMPILED_FILE"
        echo "\\\\" >> "$FIGURE_COMPILED_FILE"
        echo "$caption_text" >> "$FIGURE_COMPILED_FILE"
        echo "}" >> "$FIGURE_COMPILED_FILE"
        echo "    \\label{fig:${figure_id}}" >> "$FIGURE_COMPILED_FILE"
        echo "\\end{figure*}" >> "$FIGURE_COMPILED_FILE"
        echo "" >> "$FIGURE_COMPILED_FILE"
    done
}

main() {
    local no_figs="${1:-true}"
    local p2t="${2:-false}"
    local verbose="${3:-false}"

    if [ "$verbose" = true ]; then
        echo "Figure processing: Starting with parameters: no_figs=$no_figs, p2t=$p2t"
    fi

    init_figures
    pptx2tif "$p2t"
    ensure_lower_letter_id
    ensure_caption
    crop_tif "$no_figs"
    tif2jpg "$no_figs"
    compile_legends
    handle_figure_visibility "$no_figs"
    compile_figure_tex_files

    local compiled_count=$(find "$FIGURE_COMPILED_DIR" -name "Figure_ID_*.tex" | wc -l)

    if [ "$no_figs" = false ] && [ $compiled_count -gt 0 ]; then
        echo "Generated $compiled_count figure files."
    fi
}


main "$@"

# EOF