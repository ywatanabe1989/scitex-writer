#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-29 18:45:47 (ywatanabe)"
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

#
# Figure Processing Pipeline
# ==========================
# Figure conversion cascade:
#   1. Supported formats: pptx, tif/tiff, mmd, png, jpeg/jpg
#   2. When pptx located, try to convert to tif
#   3. When tif/tiff located, try to convert to png
#   4. When mmd located, try to convert to png
#   5. When png located, try to convert to jpg
#
# Cropping white background:
# When cropping option is enabled, try to crop image in the earliest entry point (tiff, png, or jpg)
#
# Paneling:
# All panel files (e.g., .01a_*, .01b_*) are processed
# and then automatically tiled together into the main figure.

# Configurations
source ./config/load_config.sh $STXW_DOC_TYPE
source ./scripts/shell/modules/validate_tex.src

# Source the shared command module
source "$(dirname ${BASH_SOURCE[0]})/command_switching.src"

# Override echo_xxx functions
source ./config/load_config.sh $STXW_DOC_TYPE

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

create_placeholder_jpg() {
    local figure_id="$1"  # e.g., ".01_missing"
    local jpg_path="$STXW_FIGURE_JPG_DIR/$figure_id.jpg"

    # Primary: Use template TIF file from shared directory
    local template_tif="./shared/templates/figures/.00_TEMPLATE.tif"

    if [ -f "$template_tif" ]; then
        # Copy and convert template TIF to JPG
        local convert_cmd=$(get_cmd_convert "$ORIG_DIR")
        if [ -n "$convert_cmd" ]; then
            eval "$convert_cmd \"$template_tif\" -density 300 -quality 90 \"$jpg_path\""
            echo_success "    Created placeholder from template: $figure_id.jpg"
            return 0
        fi
    fi

    # Fallback: Create a generated text placeholder with guidance
    local convert_cmd=$(get_cmd_convert "$ORIG_DIR")
    if [ -n "$convert_cmd" ]; then
        # Create guidance text with specific path information
        local source_path="$STXW_FIGURE_CAPTION_MEDIA_DIR/$figure_id"
        local rel_source_path=$(realpath --relative-to="$(pwd)" "$source_path")

        # Extract figure number and description for citation reference
        local fig_ref=$(echo "$figure_id" | sed -E 's/.([0-9]+)_?(.*)/\1_\2/' | sed 's/_$//')

        # Create a 800x600 placeholder with helpful guidance text
        eval "$convert_cmd -size 800x600 xc:'#f0f0f0' -fill black -font Arial-Bold \
            -pointsize 32 -draw 'text 50,100 \"FIGURE PLACEHOLDER\"' \
            -pointsize 24 -draw 'text 50,160 \"Figure ID: $figure_id\"' \
            -pointsize 18 -fill '#666666' \
            -draw 'text 50,220 \"Place your image file at:\"' \
            -pointsize 16 -fill '#0066cc' \
            -draw 'text 50,260 \"$rel_source_path.[png|tif|jpg|svg|mmd|pptx]\"' \
            -pointsize 14 -fill '#666666' \
            -draw 'text 50,300 \"Supported formats: PNG, TIF/TIFF, JPG/JPEG, SVG, MMD, PPTX\"' \
            -draw 'text 50,330 \"Then run: ./compile_manuscript\"' \
            -pointsize 16 -fill '#cc6600' \
            -draw 'text 50,380 \"Reference in LaTeX as:\"' \
            -pointsize 18 -fill '#cc3300' \
            -draw 'text 50,410 \"Figure~\\\\ref{fig:$fig_ref}\"' \
            -pointsize 12 -fill '#999999' \
            -draw 'text 50,500 \"This placeholder will be automatically replaced\"' \
            -draw 'text 50,520 \"when you add the actual image file.\"' \
            \"$jpg_path\""
        echo_warning "    Created guided placeholder: $figure_id.jpg"
    else
        echo_error "    Cannot create placeholder: No ImageMagick available"
        return 1
    fi
}

check_and_create_placeholders() {
    echo_info "    Checking for missing figures..."

    # Look for .tex caption files without corresponding source images
    for tex_file in "$STXW_FIGURE_CAPTION_MEDIA_DIR"/[0-9]*.tex; do
        [ -e "$tex_file" ] || continue

        local base_name=$(basename "$tex_file" .tex)

        # Skip panel files (e.g., .01A_name, .01a_name)
        if [[ "$base_name" =~ [0-9]+[A-Za-z]_ ]]; then
            continue
        fi
        local has_source=false

        # Check if any source file exists for this figure
        for ext in tif tiff jpg jpeg png svg mmd pptx; do
            if [ -f "$STXW_FIGURE_CAPTION_MEDIA_DIR/$base_name.$ext" ]; then
                has_source=true
                break
            fi
        done

        # Check if JPG already exists in compilation directory
        local jpg_exists=false
        if [ -f "$STXW_FIGURE_JPG_DIR/$base_name.jpg" ]; then
            jpg_exists=true
        fi

        # Create placeholder if no source and no JPG exists
        if [ "$has_source" = false ] && [ "$jpg_exists" = false ]; then
            echo_warning "    Missing source for: $base_name"
            create_placeholder_jpg "$base_name"
        fi
    done
}

init_figures() {
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    mkdir -p \
          "$STXW_FIGURE_CAPTION_MEDIA_DIR" \
	      "$STXW_FIGURE_COMPILED_DIR" \
	      "$STXW_FIGURE_JPG_DIR"

    # Clean up jpg_for_compilation directory before processing
    echo_info "    Cleaning jpg_for_compilation directory..."
    rm -rf "$STXW_FIGURE_JPG_DIR"/*

    rm -f \
       "$STXW_FIGURE_COMPILED_DIR"/.*.tex
    echo > $STXW_FIGURE_COMPILED_FILE
}

ensure_caption() {
    # First, ensure caption files exist for all figure files
    for img_file in "$STXW_FIGURE_CAPTION_MEDIA_DIR"/[0-9]*.{tif,tiff,jpg,jpeg,png,svg,mmd,pptx}; do
        [ -e "$img_file" ] || continue
        local ext="${img_file##*.}"
        local filename=$(basename "$img_file")

        # Process ALL files including panel files - they need captions and conversion too

        local caption_tex_file="$STXW_FIGURE_CAPTION_MEDIA_DIR/${filename%.$ext}.tex"
        local template_tex_file="$STXW_FIGURE_CAPTION_MEDIA_DIR/templates/.00_template.tex"
        # local template_tex_file="$STXW_FIGURE_CAPTION_MEDIA_DIR/templates/_.XX.tex"
        if [ ! -f "$caption_tex_file" ] && [ ! -L "$caption_tex_file" ]; then
            # Skip creating caption files for panel files
            if [[ "$filename" =~ [0-9]+[A-Za-z]_ ]]; then
                continue
            fi
            if [ -f "$template_tex_file" ]; then
                cp "$template_tex_file" "$caption_tex_file"
            else
                cat <<EOF > "$caption_tex_file"
%% -*- coding: utf-8 -*-
%% Timestamp: "$(date +"%Y-%m-%d %H:%M:%S") (ywatanabe)"
%% File: "$caption_tex_file"
\caption{\textbf{FIGURE TITLE HERE}\\\\
\smallskip
FIGURE LEGEND HERE.
}
% width=0.95\textwidth
%%%% EOF
EOF
            fi
        fi
    done
}

# This function is deprecated - use convert_figure_formats_in_cascade instead
# Kept for backwards compatibility if needed

# ===============================================
# Figure Conversion Cascade
# ===============================================
# Conversion order:
#   1. PPTX -> TIF
#   2. Crop TIF (if enabled)
#   3. TIF/TIFF -> PNG
#   4. MMD -> PNG
#   5. PNG -> JPG
#   6. Copy JPG/JPEG files
# ===============================================

convert_figure_formats_in_cascade() {
    local p2t="$1"      # Convert PPTX to TIF
    local do_crop="$2"  # Crop images

    echo_info "    Starting figure conversion cascade..."

    # Step 1: PPTX -> TIF (when pptx located, convert to tif)
    if [ "$p2t" = true ]; then
        echo_info "    Step 1: Converting PPTX to TIF..."
        pptx2tif true
    fi

    # Step 2: Crop TIF files (when cropping option enabled)
    if [ "$do_crop" = true ]; then
        echo_info "    Step 2: Cropping TIF files..."
        for tif_file in "$STXW_FIGURE_CAPTION_MEDIA_DIR"/[0-9]*.{tif,tiff}; do
            [ -e "$tif_file" ] || continue
            crop_image "$tif_file" true false
        done
    fi

    # Step 3: TIF/TIFF -> PNG (when tif/tiff located, convert to png)
    echo_info "    Step 3: Converting TIF/TIFF to PNG..."
    for tif_file in "$STXW_FIGURE_CAPTION_MEDIA_DIR"/[0-9]*.{tif,tiff}; do
        [ -e "$tif_file" ] || continue
        local base_name="$(basename "$tif_file" | sed 's/\.tiff\?$//')"
        local png_path="$STXW_FIGURE_CAPTION_MEDIA_DIR/${base_name}.png"

        if [ ! -f "$png_path" ]; then
            tif2png "$tif_file" "$png_path"
        fi
    done

    # Step 4: MMD -> PNG (when mmd located, convert to png)
    echo_info "    Step 4: Converting MMD to PNG..."
    mmd2png

    # Step 5: PNG -> JPG (convert png to jpg directly in caption_and_media)
    echo_info "    Step 5: Converting PNG to JPG..."
    for png_file in "$STXW_FIGURE_CAPTION_MEDIA_DIR"/[0-9]*.png; do
        [ -e "$png_file" ] || continue
        local base_name="$(basename "$png_file" .png)"
        local jpg_path="$STXW_FIGURE_CAPTION_MEDIA_DIR/${base_name}.jpg"

        # Skip if JPG already exists
        if [ -f "$jpg_path" ]; then
            echo_info "    JPG already exists: ${base_name}.jpg"
            continue
        fi

        if png2jpg "$png_file" "$jpg_path"; then
            echo_success "    Converted: $(basename "$png_file") -> ${base_name}.jpg"
        else
            echo_warning "    Failed to convert: $(basename "$png_file")"
        fi
    done

    # Step 6: Process existing JPG/JPEG files (normalize extension)
    echo_info "    Step 6: Processing existing JPG/JPEG files..."
    for jpeg_file in "$STXW_FIGURE_CAPTION_MEDIA_DIR"/[0-9]*.jpeg; do
        [ -e "$jpeg_file" ] || continue
        local base_name="$(basename "$jpeg_file" .jpeg)"
        local jpg_path="$STXW_FIGURE_CAPTION_MEDIA_DIR/${base_name}.jpg"

        # Rename .jpeg to .jpg for consistency
        if [ ! -f "$jpg_path" ]; then
            mv "$jpeg_file" "$jpg_path"
            echo_success "    Renamed: $(basename "$jpeg_file") -> ${base_name}.jpg"
        fi
    done

    # Optional: SVG -> JPG directly in caption_and_media
    for svg_file in "$STXW_FIGURE_CAPTION_MEDIA_DIR"/[0-9]*.svg; do
        [ -e "$svg_file" ] || continue
        local base_name="$(basename "$svg_file" .svg)"
        local jpg_path="$STXW_FIGURE_CAPTION_MEDIA_DIR/${base_name}.jpg"

        if [ ! -f "$jpg_path" ]; then
            svg2jpg "$svg_file" "$jpg_path"
        fi
    done

    # Step 7: Tile panel figures into composed figures
    tile_panels "$STXW_FIGURE_CAPTION_MEDIA_DIR"

    # Step 8: Copy ONLY composed/main figure JPGs to jpg_for_compilation
    copy_composed_jpg_files "$STXW_FIGURE_CAPTION_MEDIA_DIR" "$STXW_FIGURE_JPG_DIR"

    echo_success "    Figure conversion cascade completed"
}

ensure_lower_letter_id() {
    local ORIG_DIR="$(pwd)"
    cd "$STXW_FIGURE_CAPTION_MEDIA_DIR"
    for file in .*; do
        if [[ -f "$file" || -L "$file" ]]; then
            new_name=$(echo "$file" | sed -E 's/(.)(.*)/\1\L\2/')
            if [[ "$file" != "$new_name" ]]; then
                mv "$file" "$new_name"
            fi
        fi
    done
    cd $ORIG_DIR
}

# ===============================================
# Conversion Functions - Each handles one format
# ===============================================

copy_composed_jpg_files() {
    local src_dir="$1"
    local dst_dir="$2"

    echo_info "    Copying composed figure JPGs to jpg_for_compilation..."
    local copied_count=0

    for jpg_file in "$src_dir"/[0-9]*.jpg; do
        [ -e "$jpg_file" ] || continue
        local basename=$(basename "$jpg_file")

        # Skip panel files (e.g., 01a_*, 01b_*)
        # Only copy main/composed figure files (e.g., 01_demographic.jpg, 02_pac.jpg)
        if [[ "$basename" =~ ^[0-9]+[a-z]_ ]]; then
            echo_info "    Skipping panel file: $basename"
            continue
        fi

        # Only copy if the file doesn't already exist in destination
        if [ ! -f "$dst_dir/$basename" ] || [ "$jpg_file" -nt "$dst_dir/$basename" ]; then
            cp "$jpg_file" "$dst_dir/"
            echo_success "    Copied composed figure: $basename"
            ((copied_count++))
        else
            echo_info "    Already up-to-date: $basename"
        fi
    done

    if [ $copied_count -gt 0 ]; then
        echo_success "    Copied $copied_count composed figures to jpg_for_compilation"
    else
        echo_info "    All figures already up-to-date in jpg_for_compilation"
    fi
}

tile_panels() {
    local working_dir="$1"

    echo_info "    Creating composed figures from panels..."

    # Track which base figures we've already processed
    local processed_bases=()

    # Find all panel files (e.g., 01a_demographic_data.jpg, 01b_demographic_data.jpg)
    for panel_file in "$working_dir"/[0-9]*[a-z]_*.jpg; do
        [ -e "$panel_file" ] || continue

        # Extract base name (e.g., "01_demographic_data" from "01a_demographic_data.jpg")
        local panel_name=$(basename "$panel_file")
        local base_name=$(echo "$panel_name" | sed 's/\([0-9]\+\)[a-z]_/\1_/')

        # Skip if we already processed this base figure
        if [[ " ${processed_bases[@]} " =~ " ${base_name} " ]]; then
            continue
        fi
        processed_bases+=("$base_name")

        # Find all panels for this base figure
        # Get the figure number from base_name
        local fig_num="${base_name%%_*}"
        local panels=("$working_dir"/${fig_num}[a-z]_*.jpg)

        # echo_info "    Looking for panels matching: ${fig_num}[a-z]_*.jpg"
        # echo_info "    Found ${#panels[@]} panel files"

        if [ ${#panels[@]} -gt 1 ]; then
            # echo_info "    Found ${#panels[@]} panels for $base_name"

            # Use tile_panels.py if available
            if command -v python3 >/dev/null 2>&1 && [ -f "./scripts/python/tile_panels.py" ]; then
                python3 ./scripts/python/tile_panels.py \
                    --figure-base "$base_name" \
                    --search-dir "$working_dir" \
                    --output "$working_dir/$base_name" \
                    --spacing 30

                if [ $? -eq 0 ]; then
                    echo_success "    Created composed figure: $base_name"
                else
                    echo_warning "    Failed to tile panels for $base_name"
                fi
            else
                echo_warning "    tile_panels.py not available - skipping panel tiling"
            fi
        elif [ ${#panels[@]} -eq 1 ] && [ -e "${panels[0]}" ]; then
            # Single panel - copy it as the main figure
            # echo_info "    Found single panel for $base_name - using as main figure"
            cp "${panels[0]}" "$working_dir/$base_name"
            # echo_success "    Copied single panel as main figure: $base_name"
        else
            # No panels found, but we should still have the main figure if it exists
            # echo_info "    No panels found for $base_name"
            :
        fi
    done
}

pptx2tif() {
    local p2t="$1"
    if [[ "$p2t" == true ]]; then
        echo_info "    Converting PPTX to TIF..."
        ./scripts/shell/modules/pptx2tif_all.sh
    fi
}

mmd2png() {
    echo_info "    Converting Mermaid diagrams to PNG..."
    local THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
    eval "$THIS_DIR/mmd2png_all.sh" || echo_warning "    mmd2png failed"
}

tif2png() {
    local tif_file="$1"
    local png_file="$2"

    if [ -f "$png_file" ]; then
        return 0  # PNG already exists
    fi

    local convert_cmd=$(get_cmd_convert "$ORIG_DIR")
    if [ -n "$convert_cmd" ]; then
        eval "$convert_cmd \"$tif_file\" \"$png_file\""
        if [ -f "$png_file" ]; then
            echo_success "    Converted TIF->PNG: $(basename "$tif_file") -> $(basename "$png_file")"
            return 0
        fi
    fi
    return 1
}

png2jpg() {
    local png_file="$1"
    local jpg_file="$2"

    if [ -f "$jpg_file" ]; then
        echo_info "    JPG already exists: $(basename "$jpg_file")"
        return 0  # JPG already exists
    fi

    # For containerized ImageMagick, we need the file to be accessible
    # If it's a symlink pointing outside the bind mount, copy it temporarily
    local work_png_file="$png_file"
    local temp_copy_needed=false

    if [ -L "$png_file" ]; then
        local target=$(readlink -f "$png_file")
        if [ ! -f "$target" ]; then
            echo_warning "    Symlink target not found: $(basename "$png_file")"
            return 1
        fi
        echo_info "    Processing symlink: $(basename "$png_file")"

        # Copy the target to a temp file in the same directory for container access
        work_png_file="${png_file}.tmp.png"
        cp -L "$png_file" "$work_png_file"
        temp_copy_needed=true
    fi

    local convert_cmd=$(get_cmd_convert "$ORIG_DIR")
    if [ -n "$convert_cmd" ]; then
        # For RGBA PNGs, we need to flatten the alpha channel to white background
        eval "$convert_cmd \"$work_png_file\" -background white -alpha remove -alpha off -density 300 -quality 90 \"$jpg_file\"" 2>/dev/null
        local result=$?

        if [ $result -ne 0 ] || [ ! -f "$jpg_file" ]; then
            # Try without alpha channel handling as fallback
            eval "$convert_cmd \"$work_png_file\" -density 300 -quality 90 \"$jpg_file\"" 2>/dev/null
            result=$?
        fi

        # Clean up temp file if we created one
        if [ "$temp_copy_needed" = true ]; then
            rm -f "$work_png_file"
        fi

        if [ $result -eq 0 ] && [ -f "$jpg_file" ]; then
            echo_success "    Converted PNG->JPG: $(basename "$png_file") -> $(basename "$jpg_file")"
            return 0
        else
            echo_warning "    Failed to convert: $(basename "$png_file")"
        fi
    else
        echo_warning "    No ImageMagick found, cannot convert $(basename "$png_file") to JPG"
    fi
    return 1
}

svg2jpg() {
    local svg_file="$1"
    local jpg_file="$2"

    if [ -f "$jpg_file" ]; then
        return 0  # JPG already exists
    fi

    # Try inkscape first for better quality
    if command -v inkscape >/dev/null 2>&1; then
        inkscape -z -e "$jpg_file" -w 1200 -h 1200 "$svg_file" 2>/dev/null
        if [ -f "$jpg_file" ]; then
            echo_success "    Converted SVG->JPG with Inkscape: $(basename "$svg_file") -> $(basename "$jpg_file")"
            return 0
        fi
    fi

    # Fallback to ImageMagick
    local convert_cmd=$(get_cmd_convert "$ORIG_DIR")
    if [ -n "$convert_cmd" ]; then
        eval "$convert_cmd \"$svg_file\" -density 300 -quality 90 \"$jpg_file\""
        if [ -f "$jpg_file" ]; then
            echo_success "    Converted SVG->JPG: $(basename "$svg_file") -> $(basename "$jpg_file")"
            return 0
        fi
    else
        echo_warning "    No converter found for SVG file: $(basename "$svg_file")"
    fi
    return 1
}

copy_jpg() {
    local src_jpg="$1"
    local dst_jpg="$2"

    if [ -f "$dst_jpg" ]; then
        return 0  # Already exists
    fi

    cp "$src_jpg" "$dst_jpg"
    echo_success "    Copied: $(basename "$src_jpg") -> $(basename "$dst_jpg")"
    return 0
}

crop_image() {
    local img_file="$1"
    local do_crop="$2"
    local verbose="$3"

    if [[ "$do_crop" != true ]]; then
        return 0
    fi

    if [ ! -f "./scripts/python/crop_tif.py" ] || ! command -v python3 >/dev/null 2>&1; then
        return 0
    fi

    # Check for required Python dependencies
    if ! python3 -c "import cv2, numpy" >/dev/null 2>&1; then
        return 0
    fi

    local filename=$(basename "$img_file")
    local temp_file="${img_file}.cropped.tmp"

    if [ "$verbose" = true ]; then
        echo_info "    Cropping: $filename"
    fi

    # Run the Python script
    if [ "$verbose" = true ]; then
        python3 ./scripts/python/crop_tif.py file \
            --input "$img_file" \
            --output "$temp_file" \
            --margin 30 \
            --verbose
    else
        python3 ./scripts/python/crop_tif.py file \
            --input "$img_file" \
            --output "$temp_file" \
            --margin 30 >/dev/null 2>&1
    fi

    # If successful, replace the original file
    if [ -f "$temp_file" ]; then
        mv "$temp_file" "$img_file"
        if [ "$verbose" = true ]; then
            echo_success "    Cropped: $filename"
        fi
        return 0
    fi
    return 1
}

crop_all_images() {
    local no_figs="$1"
    local do_crop="$2"
    local verbose="$3"

    if [[ "$no_figs" == true || "$do_crop" != true ]]; then
        return 0
    fi

    echo_info "    Applying cropping to all image files..."

    # Crop all supported image formats (TIF, PNG, JPG)
    local count=0
    for img_file in "$STXW_FIGURE_CAPTION_MEDIA_DIR"/.*.{tif,tiff,png,jpg,jpeg}; do
        [ -e "$img_file" ] || continue

        # Track which files we've cropped to avoid re-cropping
        local crop_marker="${img_file}.cropped"
        if [ -f "$crop_marker" ]; then
            continue  # Already cropped in this session
        fi

        if crop_image "$img_file" "$do_crop" "$verbose"; then
            touch "$crop_marker"  # Mark as cropped
            ((count++))
        fi
    done

    if [ $count -gt 0 ]; then
        echo_success "    Cropped $count image files"
    fi

    # Clean up crop markers after processing
    rm -f "$STXW_FIGURE_CAPTION_MEDIA_DIR"/*.cropped 2>/dev/null
}

# Legacy function kept for compatibility - now uses new conversion system
optimize_figures_with_python() {
    local no_figs="$1"
    if [[ "$no_figs" == false ]] && [ -f "./scripts/python/optimize_figure.py" ] && command -v python3 >/dev/null 2>&1; then
        echo_info "    Optimizing figures with Python script..."

        # Optimize any JPG files that were created
        find "$STXW_FIGURE_JPG_DIR" -name ".*.jpg" -newer "$STXW_FIGURE_JPG_DIR" 2>/dev/null | \
            parallel -j+0 --no-notice --silent "
                python3 ./scripts/python/optimize_figure.py --input {} --output {}.tmp --dpi 300 --quality 95 && mv {}.tmp {}
            "
    fi
}

compile_legends() {
    mkdir -p "$STXW_FIGURE_COMPILED_DIR"
    rm -f "$STXW_FIGURE_COMPILED_DIR"/[0-9]*.tex
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
    # Process all numeric-prefixed caption files
    for caption_file in "$STXW_FIGURE_CAPTION_MEDIA_DIR"/[0-9]*.tex; do
        [ -f "$caption_file" ] || continue
        local fname=$(basename "$caption_file")

        # Skip panel files (e.g., 01A_name.tex, 01a_name.tex, .01A_name.tex)
        if [[ "$fname" =~ ^[0-9]+[A-Za-z]_ ]] || [[ "$fname" =~ [0-9]+[A-Za-z]_ ]]; then
            continue
        fi

        local figure_id=""
        # Extract figure ID from filename
        if [[ "$fname" =~ ^([0-9]+.*)\.tex$ ]]; then
            # Extract figure ID: 01_demographic_data.tex
            figure_id="${BASH_REMATCH[1]}"
        else
            continue
        fi
        local clean=$(echo "$figure_id" | sed 's/\.jpg$//')
        local figure_number=""
        if [[ "$clean" =~ ^([0-9]+)_ ]]; then
            figure_number="${BASH_REMATCH[1]}"
        else
            figure_number="$clean"
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
% FIGURE METADATA - Figure ID ${clean}, Number ${figure_number}
% FIGURE TYPE: TikZ
% This is not a standalone LaTeX environment - it will be included by compile_figure_tex_files
{
    "id": "${clean}",
    "number": "${figure_number}",
    "type": "tikz",
    "width": "$width",
    "tikz_code": "$tikz_code"
}
$caption_content
EOF
            else
                cat > "$tgt_file" << EOF
% FIGURE METADATA - Figure ID ${clean}, Number ${figure_number}
% FIGURE TYPE: Image
% This is not a standalone LaTeX environment - it will be included by compile_figure_tex_files
{
    "id": "${clean}",
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
% FIGURE METADATA - Figure ID ${clean}, Number ${figure_number}
% FIGURE TYPE: Image
% This is not a standalone LaTeX environment - it will be included by compile_figure_tex_files
{
    "id": "${clean}",
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
    if [[ ! -n $(find "$STXW_FIGURE_COMPILED_DIR" -name ".*.tex" 2>/dev/null) ]]; then
        return 0
    fi
    if [[ $action == "disable" ]]; then
        sed -i 's/^\(\s*\)\\includegraphics/%\1\\includegraphics/g' "$STXW_FIGURE_COMPILED_DIR"/.*.tex
    else
        mkdir -p "$STXW_FIGURE_JPG_DIR"
        find "$STXW_FIGURE_CAPTION_MEDIA_DIR" -name "*.jpg" | while read contents_jpg; do
            base_jpg=$(basename "$contents_jpg")
            if [ ! -f "$STXW_FIGURE_JPG_DIR/$base_jpg" ]; then
                cp "$contents_jpg" "$STXW_FIGURE_JPG_DIR/"
            fi
        done
        for fig_tex in "$STXW_FIGURE_COMPILED_DIR"/.*.tex; do
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
                    if [[ "$width_spec" =~ ^[0-9]+(\[0-9]+)?$ ]]; then
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

auto_tile_panels() {
    local no_figs="$1"
    if [[ "$no_figs" == true ]]; then
        return 0
    fi

    echo_info "    Checking for panel figures to tile..."

    # Find all base figure names (only numeric-prefixed patterns)
    # Format: XXa or XXA format (e.g., 01a_demographic_data.jpg)
    local figure_bases=($(find "$STXW_FIGURE_CAPTION_MEDIA_DIR" -maxdepth 1 -name "[0-9]*[A-Za-z]_*.jpg" | \
        sed 's/\([0-9]\+\)[A-Za-z]_/\1_/' | sort -u))

    for base in "${figure_bases[@]}"; do
        local base_name=$(basename "$base")
        # Extract the ID part (e.g., "01" from "01_demographic_data")
        local figure_id=$(echo "$base_name" | sed 's/\([0-9]\+\)_.*/\1/')
        local panels=($(find "$STXW_FIGURE_CAPTION_MEDIA_DIR" -maxdepth 1 -name "${figure_id}[A-Za-z]_*.jpg" | sort))

        if [ ${#panels[@]} -gt 1 ]; then
            echo "INFO:     Found ${#panels[@]} panels for $base_name - creating tiled figure..."

            if command -v python3 >/dev/null 2>&1 && [ -f "./scripts/python/tile_panels.py" ]; then
                # Remove .jpg extension if it already exists in base_name
                local output_name="${base_name%.jpg}.jpg"
                python3 ./scripts/python/tile_panels.py \
                    --figure-base "$base_name" \
                    --search-dir "$STXW_FIGURE_CAPTION_MEDIA_DIR" \
                    --output "$STXW_FIGURE_JPG_DIR/${output_name}" \
                    --spacing 30

                if [ $? -eq 0 ]; then
                    echo_success "    Created tiled figure: ${output_name}"
                else
                    echo_warning "    Failed to create tiled figure for $base_name"
                fi
            else
                echo_warning "    Python3 or tile_panels.py not available - skipping tiling"
            fi
        fi
    done
}

handle_figure_visibility() {
    local no_figs="$1"
    if [[ "$no_figs" == true ]]; then
        _toggle_figures disable
    else
        # Optional: Run Python optimizer on generated JPGs
        optimize_figures_with_python "$no_figs"
        [[ -n $(find "$STXW_FIGURE_JPG_DIR" -name "*.jpg") ]] && _toggle_figures enable || _toggle_figures disable
    fi
}

compile_figure_tex_files() {
    echo "% Generated by compile_figure_tex_files()" > "$STXW_FIGURE_COMPILED_FILE"
    echo "% This file includes all figure files in order" >> "$STXW_FIGURE_COMPILED_FILE"
    echo "" >> "$STXW_FIGURE_COMPILED_FILE"

    # First, check if there are any real figure files (not just the header)
    local figure_files=($(find "$STXW_FIGURE_COMPILED_DIR" -maxdepth 1 \( -name "[0-9]*.tex" \) ! -name "00_Figures_Header.tex" | sort))
    local has_real_figures=false
    if [ ${#figure_files[@]} -gt 0 ]; then
        has_real_figures=true
        # Don't add anything here - base.tex handles the section header and spacing
    fi

    # Variable to track if we're on the first figure
    local first_figure=true
    # Handle ([0-9]*) naming patterns
    for fig_tex in $(find "$STXW_FIGURE_COMPILED_DIR" -maxdepth 1 \( -name ".*.tex" -o -name "[0-9]*.tex" \) | sort); do
        [ -e "$fig_tex" ] || continue
        local basename=$(basename "$fig_tex")

        # Skip the header file completely if we have real figures
        if [[ "$basename" == "00_Figures_Header.tex" ]]; then
            if [ "$has_real_figures" = true ]; then
                continue
            else
                # Only use the header template if no real figures exist
                cat "$fig_tex" >> "$STXW_FIGURE_COMPILED_FILE"
                continue
            fi
        fi
        local figure_id=""
        local figure_number=""
        local figure_title=""
        local image_path=""
        local width="0.9\\\\textwidth"
        local figure_type="image"
        local caption_content=""
        if [[ "$basename" =~ .([^\.]+) ]]; then
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
        # Simply use the original caption file as-is
        local original_caption_file="$STXW_FIGURE_CAPTION_MEDIA_DIR/${basename}"
        if [ -f "$original_caption_file" ]; then
            # Read the entire caption content from the original file
            caption_content=$(cat "$original_caption_file" | grep -v "^%" | grep -v "^$")
            # Extract title from first textbf for the figure comment
            if [[ "$caption_content" =~ \\textbf\{([^}]*)\} ]]; then
                figure_title="${BASH_REMATCH[1]}"
            fi
        fi

        # Use simple fallback if no caption found
        if [ -z "$caption_content" ]; then
            caption_content="\\caption{\\textbf{Figure $figure_number}\\\\Description for figure $figure_number.}"
        fi
        echo "% Figure $figure_number" >> "$STXW_FIGURE_COMPILED_FILE"
        # Use [htbp] for all figures to allow flexible placement
        if [ "$first_figure" = true ]; then
            first_figure=false
            # First figure right after header
            echo "\\begin{figure*}[h!]" >> "$STXW_FIGURE_COMPILED_FILE"
        else
            # Allow consecutive figures without forced page breaks
            echo "\\begin{figure*}[htbp]" >> "$STXW_FIGURE_COMPILED_FILE"
        fi
        echo "    \\pdfbookmark[2]{Figure $figure_number}{.$figure_number}" >> "$STXW_FIGURE_COMPILED_FILE"
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
        # Use the complete caption content from the original file
        echo "    $caption_content" >> "$STXW_FIGURE_COMPILED_FILE"
        echo "    \\label{fig:${figure_id}}" >> "$STXW_FIGURE_COMPILED_FILE"
        echo "\\end{figure*}" >> "$STXW_FIGURE_COMPILED_FILE"
        echo "" >> "$STXW_FIGURE_COMPILED_FILE"
    done
}


main() {
    local no_figs="${1:-false}"
    local p2t="${2:-false}"  # Convert PPTX to TIF
    local verbose="${3:-false}"
    local do_crop="${4:-false}"  # Crop images

    if [ "$verbose" = true ]; then
        echo_info "    Figure processing: Starting with parameters: "
        echo_info "    no_figs=$no_figs, p2t=$p2t, crop=$do_crop"
    fi

    # Initialize environment
    init_figures
    ensure_lower_letter_id
    ensure_caption

    if [ "$no_figs" = false ]; then
        # Run the figure conversion cascade
        convert_figure_formats_in_cascade "$p2t" "$do_crop"

        # Post-processing
        check_and_create_placeholders
        auto_tile_panels "$no_figs"
    fi

    # Final compilation steps
    compile_legends
    handle_figure_visibility "$no_figs"
    compile_figure_tex_files
    local compiled_count=$(find "$STXW_FIGURE_COMPILED_DIR" -name ".*.tex" | wc -l)
    if [ "$no_figs" = false ] && [ $compiled_count -gt 0 ]; then
        echo_success "    $compiled_count figures compiled"
    fi
}

main "$@"

# EOF