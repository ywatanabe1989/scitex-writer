#!/bin/bash
# Time-stamp: "2024-11-06 08:55:33 (ywatanabe)"
# File: ./torchPAC/paper/manuscript/scripts/sh/modules/process_figures.sh


echo -e "$0 ...\n"

source ./scripts/sh/modules/config.sh

init() {
    # Cleanup and prepare directories
    rm -f "$FIGURE_COMPILED_DIR"/Figure_ID_*.tex "$FIGURE_HIDDEN_DIR"/*.tex "$FIGURE_JPG_DIR"/Figure_ID_*.jpg
    mkdir -p "$FIGURE_SRC_DIR" "$FIGURE_COMPILED_DIR" "$FIGURE_JPG_DIR" "$FIGURE_HIDDEN_DIR"
    rm -f "$FIGURE_HIDDEN_DIR/.All_Figures.tex"
    touch "$FIGURE_HIDDEN_DIR/.All_Figures.tex"
}

ensure_caption() {
    # Usage: ensure_caption
    for tif_file in "$FIGURE_SRC_DIR"/Figure_ID_*.tif; do
        [ -e "$tif_file" ] || continue
        local filename=$(basename "$tif_file")
        local caption_tex_file="$FIGURE_SRC_DIR/${filename%.tif}.tex"
        if [ ! -f "$caption_tex_file" ] && [ ! -L "$caption_tex_file" ]; then
            echo $file_name $caption_tex_file
            # ln -sf "_Figure_ID_XX.tex" "$caption_tex_file"
            cp "$FIGURE_SRC_DIR/_Figure_ID_XX.tex" "$caption_tex_file"
        fi
    done
}

ensure_lower_letters() {
    local ORIG_DIR="$(pwd)"
    cd "$FIGURE_SRC_DIR"

    for file in Figure_ID_*; do
        if [[ -f "$file" || -L "$file" ]]; then
            new_name=$(echo "$file" | sed -E 's/(Figure_ID_)(.*)/\1\L\2/')
            if [[ "$file" != "$new_name" ]]; then
                # ln -s "$file" "$new_name"
                mv "$file" "$new_name"
            fi
        fi
    done

    cd $ORIG_DIR
    }

pptx2tif() {
    local p2t="$1"

    if [[ "$p2t" == true ]]; then
        ./scripts/sh/modules/pptx2tif_all.sh
    fi
}

crop_tif() {
    local no_figs="$1"
    if [[ "$no_figs" == false ]]; then
        # ./scripts/sh/modules/crop_figures.sh

        # find "$FIGURE_SRC_DIR"/Figure_ID*.tif | \
        ls "$FIGURE_SRC_DIR"/Figure_ID*.tif | \
            parallel -j+0 --eta './.env/bin/python ./scripts/py/crop_tif.py -l {}'
    fi
}


tif2jpg () {
    local no_figs="$1"
    if [[ "$no_figs" == false ]]; then
        echo "tif2jpg"
        find "$FIGURE_SRC_DIR" -name "Figure_ID_*.tif" | parallel -j+0 --eta '
            echo -e "\nConverting {} to '"$FIGURE_JPG_DIR"'/$(basename {} .tif).jpg"
            convert {} -density 100 -quality 90 "'"$FIGURE_JPG_DIR"'/$(basename {} .tif).jpg"
        '
    fi
}

# compile_legends () {
#     # Generates ./src/figures/tex/Figure_ID_*.tex files from ./src/figures/Figure_ID_*.tex files
#     local ii=0
#     for caption_file in "$FIGURE_SRC_DIR"/Figure_ID_*.tex; do
#         echo $caption_file
#         # [ -e "$caption_file" ] || continue
#         local fname=$(basename "$caption_file")
#         local tgt_file="$FIGURE_COMPILED_DIR/$fname"
#         local figure_content=$(cat "$caption_file")
#         local figure_id=$(echo "$fname" | grep -oP '(?<=Figure_ID_)[^\.]+' | tr '[:upper:]' '[:lower:]')
#         local width=$(grep -oP '(?<=width=)[0-9.]+\\textwidth' "$caption_file")

#         [[ $ii -gt 0 ]] && echo "\\clearpage" > "$tgt_file"

#         rm "$tgt_file" -f # > /dev/null 2>&1
#         touch "$tgt_file"

#         cat <<EOF > "$tgt_file"
#         \clearpage
#         \begin{figure*}[ht]
#             \pdfbookmark[2]{ID $figure_id}{figure_id_$figure_id}
#         	\centering
#             \includegraphics[width=$width]{$FIGURE_JPG_DIR/${fname%.tex}.jpg}
#         	$figure_content
#         	\label{fig:$figure_id}
#         \end{figure*}
# EOF
#         ((ii++))
#     done

# }

compile_legends () {
    # Generates ./src/figures/compiled/Figure_ID_*.tex files from ./src/figures/src/Figure_ID_*.tex files
    local ii=0
    for caption_file in "$FIGURE_SRC_DIR"/Figure_ID_*.tex; do
        if [ ! -f "$caption_file" ]; then
            echo "Error: File not found: $caption_file" >&2
            return 1
        fi
        local fname=$(basename "$caption_file")
        local tgt_file="$FIGURE_COMPILED_DIR/$fname"
        local figure_content=$(cat "$caption_file") || { echo "Error reading $caption_file" >&2; return 1; }
        # local figure_id=$(echo "$fname" | grep -oP '(?<=Figure_ID_)[^\.]+')
        local figure_id=$(echo "$fname" | grep -oP '(?<=Figure_ID_)[^\.]+' | tr '[:upper:]' '[:lower:]')
        local width=$(grep -oP '(?<=width=)[0-9.]+\\textwidth' "$caption_file")

        if [ ! -d "$FIGURE_COMPILED_DIR" ]; then
            mkdir -p "$FIGURE_COMPILED_DIR" || \
                { echo "Error creating directory $FIGURE_COMPILED_DIR" >&2; return 1; }
        fi

        [[ $ii -gt 0 ]] && echo "\\clearpage" > "$tgt_file"

        if ! rm "$tgt_file" -f > /dev/null 2>&1 || ! touch "$tgt_file"; then
            echo "Error creating $tgt_file" >&2
            return 1
        fi

        cat <<EOF > "$tgt_file"
        \clearpage
        \begin{figure}[ht]
            \pdfbookmark[2]{ID $figure_id}{figure_id_$figure_id}
        	\centering
            \includegraphics[width=$width]{$FIGURE_JPG_DIR/${fname%.tex}.jpg}
        	$figure_content
        	\label{fig:$figure_id}
        \end{figure}
EOF
        ((ii++))
    done

}

# _toggle_figures() {
#     local action=$1
#     local sed_cmd
#     [[ $action == "disable" ]] && sed_cmd='s/^\(\s*\)\\includegraphics/%\1\\includegraphics/g' || sed_cmd='s/^%\(\s*\\includegraphics\)/\1/g'
#     sed -i "$sed_cmd" "$FIGURE_COMPILED_DIR"/Figure_ID_*.tex
# }

# _toggle_figures() {
#     local action=$1
#     local sed_cmd
#     [[ $action == "disable" ]] && sed_cmd='s/^\(\s*\)\\includegraphics/%\1\\includegraphics/g' || sed_cmd='s/^%\(\s*\\includegraphics\)/\1/g'
#     if [[ -d "$FIGURE_COMPILED_DIR" ]]; then
#         find "$FIGURE_COMPILED_DIR" -name "Figure_ID_*.tex" -print0 | xargs -0 sed -i "$sed_cmd"
#     else
#         echo "Error: Directory $FIGURE_COMPILED_DIR not found"
#         return 1
#     fi
# }


_toggle_figures() {
    local action=$1
    local sed_cmd
    [[ $action == "disable" ]] && sed_cmd='s/^\(\s*\)\\includegraphics/%\1\\includegraphics/g' || sed_cmd='s/^%\(\s*\\includegraphics\)/\1/g'

    # Check if files exist
    if [[ ! -n $(find "$FIGURE_COMPILED_DIR" -name "Figure_ID_*.tex" 2>/dev/null) ]]; then
        echo "No matching files found. Skipping figure toggle."
        return 0
    fi

    sed -i "$sed_cmd" "$FIGURE_COMPILED_DIR"/Figure_ID_*.tex
}

handle_figure_visibility() {
    local no_figs="$1"

    if [[ "$no_figs" == true ]]; then
        _toggle_figures disable
    else
        tif2jpg
        [[ -n $(find "$FIGURE_JPG_DIR" -name "*.jpg") ]] && _toggle_figures enable || _toggle_figures disable
    fi
}

gather_tex_files () {
    local output_file="$FIGURE_HIDDEN_DIR/.All_Figures.tex"
    echo "" > "$output_file"
	for fig_tex in "$FIGURE_COMPILED_DIR"/Figure_ID_*.tex; do
        [ -e "$fig_tex" ] || continue
	    fname="${fig_tex%.tex}"
        echo "\input{${fname}}" >> "$output_file"
    done
}

main () {
    local no_figs="${1:-true}"
    local p2t="${2:-false}"

    init || { echo "Error in init ($0)"; return 1; }
    pptx2tif "$p2t" || { echo "Error in pptx2tif ($0)"; return 1; }
    ensure_lower_letters || { echo "Error in ensure_lower_letters ($0)"; return 1; }
    ensure_caption || { echo "Error in ensure_caption ($0)"; return 1; }
    crop_tif "$no_figs" || { echo "Error in crop_tif ($0)"; return 1; }
    tif2jpg "$no_figs" || { echo "Error in crop_tif ($0)"; return 1; }
    compile_legends
    handle_figure_visibility "$no_figs" || { echo "Error in handle_figure_visibility ($0)"; return 1; }
    gather_tex_files || { echo "Error in gather_tex_files ($0)"; return 1; }
}

main "$@"

# EOF

# /home/ywatanabe/proj/ripple-wm/paper/manuscript/scripts/sh/modules/process_figures.sh true true


# EOF
