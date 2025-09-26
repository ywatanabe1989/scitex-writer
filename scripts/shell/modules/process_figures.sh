#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-26 11:00:33 (ywatanabe)"
# File: ./paper/scripts/shell/modules/process_figures.sh

ORIG_DIR="$(pwd)"
THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
echo > "$LOG_PATH"

BLACK='\033[0;30m'
LIGHT_GRAY='\033[0;37m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo_info() { echo -e "${LIGHT_GRAY}$1${NC}"; }
echo_success() { echo -e "${GREEN}$1${NC}"; }
echo_warning() { echo -e "${YELLOW}$1${NC}"; }
echo_error() { echo -e "${RED}$1${NC}"; }
# ---------------------------------------

# Configurations
source ./config/load_config.sh $STXW_MANUSCRIPT_TYPE
source ./scripts/shell/modules/validate_tex.src

# Logging
touch "$LOG_PATH" >/dev/null 2>&1
echo
echo_info "Running $0 ..."

# In process_figures.sh, add the validate_image_file function:
validate_image_file() {
    local image_path="$1"
    if [ ! -f "$image_path" ]; then
        return 1
    fi
    local mime_type=$(file --mime-type -b "$image_path")
    if [[ "$mime_type" == "image/"* ]]; then
        return 0
    fi
    return 1
}

init_figures() {
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    mkdir -p \
          "$STXW_FIGURE_CAPTION_MEDIA_DIR" \
	      "$STXW_FIGURE_COMPILED_DIR" \
	      "$STXW_FIGURE_JPG_DIR"
    rm -f \
       "$STXW_FIGURE_COMPILED_DIR"/Figure_ID_*.tex
    echo > $STXW_FIGURE_COMPILED_FILE
}

ensure_caption() {
    for img_file in "$STXW_FIGURE_CAPTION_MEDIA_DIR"/Figure_ID_*.{tif,jpg,png,svg,mmd}; do
        [ -e "$img_file" ] || continue
        local ext="${img_file##*.}"
        local filename=$(basename "$img_file")
        local caption_tex_file="$STXW_FIGURE_CAPTION_MEDIA_DIR/${filename%.$ext}.tex"
        local template_tex_file="$STXW_FIGURE_CAPTION_MEDIA_DIR/templates/Figure_ID_00_template.tex"
        # local template_tex_file="$STXW_FIGURE_CAPTION_MEDIA_DIR/templates/_Figure_ID_XX.tex"
        if [ ! -f "$caption_tex_file" ] && [ ! -L "$caption_tex_file" ]; then
            if [ -f "$template_tex_file" ]; then
                cp "$template_tex_file" "$caption_tex_file"
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
            if [ ! -f "$STXW_FIGURE_JPG_DIR/$filename" ]; then
                cp "$img_file" "$STXW_FIGURE_JPG_DIR/"
            fi
        elif [ "$ext" = "png" ]; then
            local jpg_filename="${filename%.png}.jpg"
            if [ ! -f "$STXW_FIGURE_JPG_DIR/$jpg_filename" ]; then
                convert "$img_file" -density 300 -quality 90 "$STXW_FIGURE_JPG_DIR/$jpg_filename"
            fi
        elif [ "$ext" = "svg" ]; then
            local jpg_filename="${filename%.svg}.jpg"
            if [ ! -f "$STXW_FIGURE_JPG_DIR/$jpg_filename" ]; then
                if command -v inkscape >/dev/null 2>&1; then
                    inkscape -z -e "$STXW_FIGURE_JPG_DIR/$jpg_filename" -w 1200 -h 1200 "$img_file"
                else
                    convert "$img_file" -density 300 -quality 90 "$STXW_FIGURE_JPG_DIR/$jpg_filename"
                fi
            fi
        elif [ "$ext" = "mmd" ]; then
            # Just create the caption file for mmd, processing is done separately
            :
        fi
    done
}

ensure_lower_letter_id() {
    local ORIG_DIR="$(pwd)"
    cd "$STXW_FIGURE_CAPTION_MEDIA_DIR"
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
    local do_crop_tif="$2"
    local verbose="$3"

    if [[ "$no_figs" == false && "$do_crop_tif" == true ]]; then
        echo_info "    Processing images (crop_tif)..."
        if [ -f "./scripts/python/crop_tif.py" ] && command -v python3 >/dev/null 2>&1; then
            # Check for required Python dependencies
            if ! python3 -c "import cv2, numpy" >/dev/null 2>&1; then
                echo_warn "    Required Python packages (opencv, numpy) not found. Skipping crop_tif."
                return 1
            fi

            # Process all TIF files in the caption_and_media directory
            local tif_files=$(find "$STXW_FIGURE_CAPTION_MEDIA_DIR" -name "Figure_ID_*.tif")
            local count=$(echo "$tif_files" | wc -l)

            if [ -z "$tif_files" ]; then
                echo_info "    No TIF files found to crop."
                return 0
            fi

            echo_info "    Found $count TIF files to crop"

            # Create a temporary directory for processed files if needed
            local temp_dir="${STXW_FIGURE_CAPTION_MEDIA_DIR}/processed"
            mkdir -p "$temp_dir"

            # Process each TIF file
            echo "$tif_files" | while read -r tif_file; do
                if [ -z "$tif_file" ]; then continue; fi

                local filename=$(basename "$tif_file")
                local output_path="${temp_dir}/${filename}"

                if [ "$verbose" = true ]; then
                    echo_info "    Cropping: $filename"
                fi

                # Run the Python script with appropriate parameters
                if [ "$verbose" = true ]; then
                    python3 ./scripts/python/crop_tif.py file \
                        --input "$tif_file" \
                        --output "$output_path" \
                        --margin 30 \
                        --verbose
                else
                    python3 ./scripts/python/crop_tif.py file \
                        --input "$tif_file" \
                        --output "$output_path" \
                        --margin 30
                fi

                # If successful, replace the original file
                if [ -f "$output_path" ]; then
                    mv "$output_path" "$tif_file"
                fi
            done

            # Clean up temporary directory
            rmdir "$temp_dir" 2>/dev/null

            echo_success "    Cropped $count TIF files"
        else
            echo_warn "    crop_tif.py script or Python 3 not found. Skipping crop_tif."
        fi
    fi
}

tif2jpg() {
    local no_figs="$1"
    if [[ "$no_figs" == false ]]; then
        echo "Processing images (tif2jpg)..."
        if [ -f "./scripts/python/optimize_figure.py" ] \
               && command -v python3 >/dev/null 2>&1; then

            find "$STXW_FIGURE_CAPTION_MEDIA_DIR" -name "Figure_ID_*.tif" \
                | parallel -j+0 --eta '
                python3 ./scripts/python/optimize_figure.py --input {} --output "$STXW_FIGURE_JPG_DIR"/$(basename {} .tif).jpg" --dpi 300 --quality 95
            '

            find "$STXW_FIGURE_CAPTION_MEDIA_DIR" -name "Figure_ID_*.png" \
                | parallel -j+0 --eta '
                python3
./scripts/python/optimize_figure.py
--input {}
--output
"$STXW_FIGURE_JPG_DIR"/$(basename {} .png).jpg"
--dpi 300
--quality 95
            '
            if command -v inkscape >/dev/null 2>&1; then
                find "$STXW_FIGURE_CAPTION_MEDIA_DIR" -name "Figure_ID_*.svg" | parallel -j+0 --eta '
                    inkscape -z -e "$STXW_FIGURE_JPG_DIR"/$(basename {} .svg)_temp.png" -w 1200 -h 1200 {}
                    python3 ./scripts/python/optimize_figure.py --input "$STXW_FIGURE_JPG_DIR"/$(basename {} .svg)_temp.png" --output "$STXW_FIGURE_JPG_DIR"/$(basename {} .svg).jpg" --dpi 300 --quality 95
                    rm -f "$STXW_FIGURE_JPG_DIR"/$(basename {} .svg)_temp.png"
                '
            else
                find "$STXW_FIGURE_CAPTION_MEDIA_DIR" -name "Figure_ID_*.svg" | parallel -j+0 --eta '
                    convert {} -density 300 -quality 95 "$STXW_FIGURE_JPG_DIR"/$(basename {} .svg).jpg"
                '
            fi
            find "$STXW_FIGURE_CAPTION_MEDIA_DIR" -name "Figure_ID_*.jpg" | parallel -j+0 --eta '
                if [ ! -f "$STXW_FIGURE_JPG_DIR"/$(basename {})" ]; then
                    python3 ./scripts/python/optimize_figure.py --input {} --output "$STXW_FIGURE_JPG_DIR"/$(basename {})" --dpi 300 --quality 95
                fi
            '
        else
            find "$STXW_FIGURE_CAPTION_MEDIA_DIR" -name "Figure_ID_*.tif" | parallel -j+0 --eta '
                convert {} -density 300 -quality 95 "$STXW_FIGURE_JPG_DIR"/$(basename {} .tif).jpg"
            '
            find "$STXW_FIGURE_CAPTION_MEDIA_DIR" -name "Figure_ID_*.png" | parallel -j+0 --eta '
                convert {} -density 300 -quality 95 "$STXW_FIGURE_JPG_DIR"/$(basename {} .png).jpg"
            '
            find "$STXW_FIGURE_CAPTION_MEDIA_DIR" -name "Figure_ID_*.svg" | parallel -j+0 --eta '
                convert {} -density 300 -quality 95 "$STXW_FIGURE_JPG_DIR"/$(basename {} .svg).jpg"
            '
            find "$STXW_FIGURE_CAPTION_MEDIA_DIR" -name "Figure_ID_*.jpg" | parallel -j+0 --eta '
                if [ ! -f "$STXW_FIGURE_JPG_DIR"/$(basename {})" ]; then
                    cp {} "$STXW_FIGURE_JPG_DIR"/$(basename {})"
                fi
            '
        fi
    fi
}

compile_legends() {
    mkdir -p "$STXW_FIGURE_COMPILED_DIR"
    rm -f "$STXW_FIGURE_COMPILED_DIR"/Figure_ID_*.tex
    local figures_header_file="$STXW_FIGURE_COMPILED_DIR/00_Figures_Header.tex"
    cat > "$figures_header_file" << "EOF"
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% FIGURES
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% \clearpage
\section*{Figures}
\label{figures}
\pdfbookmark[1]{Figures}{figures}
EOF
    for caption_file in "$STXW_FIGURE_CAPTION_MEDIA_DIR"/Figure_ID_*.tex; do
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
        local tgt_file="$STXW_FIGURE_COMPILED_DIR/$fname"
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
    "path": "$STXW_FIGURE_JPG_DIR/$jpg_file"
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
    "path": "$STXW_FIGURE_JPG_DIR/$jpg_file"
}
$caption_content
EOF
        fi

        # Validate the figure-related files
        if [ -f "$STXW_FIGURE_JPG_DIR/$jpg_file" ]; then
            if file "$STXW_FIGURE_JPG_DIR/$jpg_file" | grep -qv "JPEG image data"; then
                echo_warn "   File $jpg_file exists but may not be a valid JPEG image."
            fi
        else
            if [ "$is_tikz" = false ]; then
                echo_warn "    Image file not found: $STXW_FIGURE_JPG_DIR/$jpg_file"
            fi
        fi

    done
}

_toggle_figures() {
    local action=$1
    if [ ! -d "$STXW_FIGURE_COMPILED_DIR" ]; then
        mkdir -p "$STXW_FIGURE_COMPILED_DIR"
        return 0
    fi
    if [[ ! -n $(find "$STXW_FIGURE_COMPILED_DIR" -name "Figure_ID_*.tex" 2>/dev/null) ]]; then
        return 0
    fi
    if [[ $action == "disable" ]]; then
        sed -i 's/^\(\s*\)\\includegraphics/%\1\\includegraphics/g' "$STXW_FIGURE_COMPILED_DIR"/Figure_ID_*.tex
    else
        mkdir -p "$STXW_FIGURE_JPG_DIR"
        find "$STXW_FIGURE_CAPTION_MEDIA_DIR" -name "*.jpg" | while read src_jpg; do
            base_jpg=$(basename "$src_jpg")
            if [ ! -f "$STXW_FIGURE_JPG_DIR/$base_jpg" ]; then
                cp "$src_jpg" "$STXW_FIGURE_JPG_DIR/"
            fi
        done
        for fig_tex in "$STXW_FIGURE_COMPILED_DIR"/Figure_ID_*.tex; do
            [ -e "$fig_tex" ] || continue
            local fname=$(basename "$fig_tex")
            local jpg_file=""
            if [[ "$fname" == *".jpg.tex" ]]; then
                jpg_file="${fname%.tex}"
            else
                jpg_file="${fname%.tex}.jpg"
            fi
            if [ -f "$STXW_FIGURE_JPG_DIR/$jpg_file" ]; then
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
                sed -i "s|\\\\includegraphics\[width=[^]]*\]{[^}]*}|\\\\includegraphics[width=$width_spec]{$STXW_FIGURE_JPG_DIR/$jpg_file}|g" "$fig_tex"
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
        [[ -n $(find "$STXW_FIGURE_JPG_DIR" -name "*.jpg") ]] && _toggle_figures enable || _toggle_figures disable
    fi
}

compile_figure_tex_files() {
    echo "% Generated by compile_figure_tex_files() on $(date)" > "$STXW_FIGURE_COMPILED_FILE"
    echo "% This file includes all figure files in order" >> "$STXW_FIGURE_COMPILED_FILE"
    echo "" >> "$STXW_FIGURE_COMPILED_FILE"
    # Variable to track if we're on the first figure
    local first_figure=true
    for fig_tex in $(find "$STXW_FIGURE_COMPILED_DIR" -maxdepth 1 -name "Figure_ID_*.tex" | sort); do
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
        local original_caption_file="$STXW_FIGURE_CAPTION_MEDIA_DIR/${basename}"
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
        echo "% Figure $figure_number: ${figure_title}" >> "$STXW_FIGURE_COMPILED_FILE"
        # Only add \clearpage for figures after the first one
        if [ "$first_figure" = true ]; then
            first_figure=false
        else
            echo "\\clearpage" >> "$STXW_FIGURE_COMPILED_FILE"
        fi
        echo "\\begin{figure*}[p]" >> "$STXW_FIGURE_COMPILED_FILE"
        echo "    \\pdfbookmark[2]{Figure $figure_number}{figure_id_$figure_number}" >> "$STXW_FIGURE_COMPILED_FILE"
        echo "    \\centering" >> "$STXW_FIGURE_COMPILED_FILE"
        if [ "$figure_type" = "tikz" ]; then
            local tikz_code=$(grep -A100 "\\\\begin{tikzpicture}" "$fig_tex" | sed -n '/\\begin{tikzpicture}/,/\\end{tikzpicture}/p')
            if [ -n "$tikz_code" ]; then
                echo "$tikz_code" >> "$STXW_FIGURE_COMPILED_FILE"
            else
                if [ -n "$image_path" ]; then
                    echo "    \\includegraphics[width=$width]{$image_path}" >> "$STXW_FIGURE_COMPILED_FILE"
                fi
            fi
        else
            if [ -n "$image_path" ]; then
                echo "    \\includegraphics[width=$width]{$image_path}" >> "$STXW_FIGURE_COMPILED_FILE"
                # Validate image path
                if ! validate_image_file "$image_path"; then
                    echo_warn "    Image file not found: $image_path"
                fi
            fi
        fi
        echo "    \\caption{" >> "$STXW_FIGURE_COMPILED_FILE"
        echo "\\textbf{" >> "$STXW_FIGURE_COMPILED_FILE"
        echo "$figure_title" >> "$STXW_FIGURE_COMPILED_FILE"
        echo "}" >> "$STXW_FIGURE_COMPILED_FILE"
        echo "\\smallskip" >> "$STXW_FIGURE_COMPILED_FILE"
        echo "\\\\" >> "$STXW_FIGURE_COMPILED_FILE"
        echo "$caption_text" >> "$STXW_FIGURE_COMPILED_FILE"
        echo "}" >> "$STXW_FIGURE_COMPILED_FILE"
        echo "    \\label{fig:${figure_id}}" >> "$STXW_FIGURE_COMPILED_FILE"
        echo "\\end{figure*}" >> "$STXW_FIGURE_COMPILED_FILE"
        echo "" >> "$STXW_FIGURE_COMPILED_FILE"
    done
}


main() {
    local no_figs="${1:-true}"
    local p2t="${2:-false}"
    local verbose="${3:-false}"
    local do_crop_tif="${4:-false}"
    if [ "$verbose" = true ]; then
        echo -n "Figure processing: Starting with parameters: "
        echo "no_figs=$no_figs, p2t=$p2t, crop_tif=$do_crop_tif"
    fi

    # Mermaid
    local THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
    eval "$THIS_DIR/mmd2png_all.sh" >/dev/null 2>&1 || echo "mmd2png failed"
    eval "$THIS_DIR/png2tif_all.sh"

    init_figures
    pptx2tif "$p2t"

    ensure_lower_letter_id
    ensure_caption
    crop_tif "$no_figs" "$do_crop_tif" "$verbose"
    tif2jpg "$no_figs"
    compile_legends
    handle_figure_visibility "$no_figs"
    compile_figure_tex_files
    local compiled_count=$(find "$STXW_FIGURE_COMPILED_DIR" -name "Figure_ID_*.tex" | wc -l)
    if [ "$no_figs" = false ] && [ $compiled_count -gt 0 ]; then
        echo_success "    $compiled_count figures compiled"
    fi
}

main "$@"

# EOF