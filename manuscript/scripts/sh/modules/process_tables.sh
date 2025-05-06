#!/bin/bash
# ./paper/manuscript/scripts/sh/modules/process_tables.sh

echo -e "$0 ...\n"

source ./scripts/sh/modules/config.sh

init() {
    # Cleanup and prepare directories
    rm -f "$TABLE_COMPILED_DIR"/*.tex "$TABLE_HIDDEN_DIR"/*.tex
    mkdir -p "$TABLE_SRC_DIR" "$TABLE_COMPILED_DIR" "$TABLE_HIDDEN_DIR"
    rm -f "$TABLE_HIDDEN_DIR/.All_Tables.tex"
    touch "$TABLE_HIDDEN_DIR/.All_Tables.tex"
}

ensure_caption() {
    # Usage: ensure_caption
    for csv_file in "$TABLE_SRC_DIR"/Table_ID_*.csv; do
        [ -e "$csv_file" ] || continue
        local filename=$(basename "$csv_file")
        local caption_tex_file="$TABLE_SRC_DIR/${filename%.csv}.tex"
        if [ ! -f "$caption_tex_file" ] && [ ! -L "$caption_tex_file" ]; then
            cp "$TABLE_SRC_DIR/_Table_ID_XX.tex" "$caption_tex_file"
        fi
    done
}

ensure_lower_letters() {
    local ORIG_DIR="$(pwd)"
    cd "$TABLE_SRC_DIR"

    for file in Table_ID_*; do
        if [[ -f "$file" || -L "$file" ]]; then
            new_name=$(echo "$file" | sed -E 's/(Table_ID_)(.*)/\1\L\2/')
            if [[ "$file" != "$new_name" ]]; then
                mv "$file" "$new_name"
            fi
        fi
    done

    cd $ORIG_DIR
    }

# Function to log messages to both stdout and a log file
log_message() {
    local level="$1"
    local message="$2"
    local log_file="$TABLE_COMPILED_DIR/debug/process_tables.log"
    
    # Create log directory if it doesn't exist
    mkdir -p "$(dirname "$log_file")"
    
    # Format the log message with timestamp
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    local formatted_message="[$timestamp] [$level] $message"
    
    # Log to console with appropriate color
    case "$level" in
        "ERROR")
            echo -e "\e[31m$formatted_message\e[0m" >&2  # Red for errors
            ;;
        "WARNING")
            echo -e "\e[33m$formatted_message\e[0m" >&2  # Yellow for warnings
            ;;
        "INFO")
            echo -e "\e[32m$formatted_message\e[0m"      # Green for info
            ;;
        *)
            echo "$formatted_message"
            ;;
    esac
    
    # Log to file
    echo "$formatted_message" >> "$log_file"
}

# Detect table format and get customization parameters
detect_table_format() {
    local csv_file="$1"
    local caption_file="$2"
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local debug_dir="$TABLE_COMPILED_DIR/debug"
    local options_log="${debug_dir}/table_options_${timestamp}.log"

    # Create debug directory if it doesn't exist
    mkdir -p "$debug_dir"
    
    # Default values
    local fontsize="small"
    local tabcolsep="4pt"
    local alignment="r"  # Default right-aligned columns
    local landscape="false"
    local use_colortbl="true"
    local use_math="true"
    local table_style="booktabs"  # booktabs (default), basic, fancy
    local caption_pos="top"      # top (default) or bottom
    local float_pos="htbp"       # LaTeX float position specifier
    local scale_to_width="false" # Scale table to textwidth
    local header_style="bold"    # bold (default), plain, colored
    local auto_width="false"     # Automatic column width calculation
    local first_col_bold="false" # Make first column bold
    local max_width=""           # Maximum table width
    local custom_col_spec=""     # Custom column specifiers
    local wrap_text="false"      # Wrap text in cells
    local multirow="false"       # Allow multirow cells
    
    # Initialize log file
    echo "===== TABLE FORMAT OPTIONS =====" > "$options_log"
    echo "CSV File: $csv_file" >> "$options_log"
    echo "Caption File: $caption_file" >> "$options_log"
    echo "Timestamp: $(date)" >> "$options_log"
    echo "===========================" >> "$options_log"
    
    # Check if caption file exists
    if [ -f "$caption_file" ]; then
        # Extract formatting parameters from caption file comments
        echo "Reading options from caption file..." >> "$options_log"
        
        # Font size
        if grep -q "% fontsize=" "$caption_file"; then
            fontsize=$(grep -oP '(?<=% fontsize=)[^\s]+' "$caption_file")
            echo "Found fontsize=$fontsize" >> "$options_log"
        fi
        
        # Column separation
        if grep -q "% tabcolsep=" "$caption_file"; then
            tabcolsep=$(grep -oP '(?<=% tabcolsep=)[^\s]+' "$caption_file")
            echo "Found tabcolsep=$tabcolsep" >> "$options_log"
        fi
        
        # Column alignment
        if grep -q "% alignment=" "$caption_file"; then
            alignment=$(grep -oP '(?<=% alignment=)[^\s]+' "$caption_file")
            echo "Found alignment=$alignment" >> "$options_log"
        fi
        
        # Landscape orientation
        if grep -q "% orientation=landscape" "$caption_file"; then
            landscape="true"
            echo "Found orientation=landscape" >> "$options_log"
        fi
        
        # Color usage
        if grep -q "% no-color" "$caption_file"; then
            use_colortbl="false"
            echo "Found no-color" >> "$options_log"
        fi
        
        # Math formatting
        if grep -q "% no-math" "$caption_file"; then
            use_math="false"
            echo "Found no-math" >> "$options_log"
        fi
        
        # Table style (NEW)
        if grep -q "% style=" "$caption_file"; then
            table_style=$(grep -oP '(?<=% style=)[^\s]+' "$caption_file")
            echo "Found style=$table_style" >> "$options_log"
        fi
        
        # Caption position (NEW)
        if grep -q "% caption-pos=" "$caption_file"; then
            caption_pos=$(grep -oP '(?<=% caption-pos=)[^\s]+' "$caption_file")
            echo "Found caption-pos=$caption_pos" >> "$options_log"
        fi
        
        # Float position (NEW)
        if grep -q "% float-pos=" "$caption_file"; then
            float_pos=$(grep -oP '(?<=% float-pos=)[^\s]+' "$caption_file")
            echo "Found float-pos=$float_pos" >> "$options_log"
        fi
        
        # Scale to width (NEW)
        if grep -q "% scale-to-width" "$caption_file"; then
            scale_to_width="true"
            echo "Found scale-to-width" >> "$options_log"
        fi
        
        # Header style (NEW)
        if grep -q "% header-style=" "$caption_file"; then
            header_style=$(grep -oP '(?<=% header-style=)[^\s]+' "$caption_file")
            echo "Found header-style=$header_style" >> "$options_log"
        fi
        
        # Auto width (NEW)
        if grep -q "% auto-width" "$caption_file"; then
            auto_width="true"
            echo "Found auto-width" >> "$options_log"
        fi
        
        # First column bold (NEW)
        if grep -q "% first-col-bold" "$caption_file"; then
            first_col_bold="true"
            echo "Found first-col-bold" >> "$options_log"
        fi
        
        # Maximum width (NEW)
        if grep -q "% max-width=" "$caption_file"; then
            max_width=$(grep -oP '(?<=% max-width=)[^\s]+' "$caption_file")
            echo "Found max-width=$max_width" >> "$options_log"
        fi
        
        # Custom column specifiers (NEW)
        if grep -q "% column-spec=" "$caption_file"; then
            custom_col_spec=$(grep -oP '(?<=% column-spec=)[^\s]+' "$caption_file")
            echo "Found custom-col-spec=$custom_col_spec" >> "$options_log"
        fi
        
        # Wrap text (NEW)
        if grep -q "% wrap-text" "$caption_file"; then
            wrap_text="true"
            echo "Found wrap-text" >> "$options_log"
        fi
        
        # Multirow cells (NEW)
        if grep -q "% multirow" "$caption_file"; then
            multirow="true"
            echo "Found multirow" >> "$options_log"
        fi
    else
        echo "Caption file not found. Using default options." >> "$options_log"
    fi
    
    # Return the detected options as a JSON-like string
    echo "{\"fontsize\":\"$fontsize\",\"tabcolsep\":\"$tabcolsep\",\"alignment\":\"$alignment\",\"landscape\":\"$landscape\",\"use_colortbl\":\"$use_colortbl\",\"use_math\":\"$use_math\",\"table_style\":\"$table_style\",\"caption_pos\":\"$caption_pos\",\"float_pos\":\"$float_pos\",\"scale_to_width\":\"$scale_to_width\",\"header_style\":\"$header_style\",\"auto_width\":\"$auto_width\",\"first_col_bold\":\"$first_col_bold\",\"max_width\":\"$max_width\",\"custom_col_spec\":\"$custom_col_spec\",\"wrap_text\":\"$wrap_text\",\"multirow\":\"$multirow\"}"
}

csv2tex() {
    # Compile CSV tables with their corresponding caption files
    log_message "INFO" "Processing tables from CSV files"
    
    # Create debug directory if it doesn't exist
    mkdir -p "$TABLE_COMPILED_DIR/debug"
    
    # Find all CSV files
    local csv_files=$(find "$TABLE_SRC_DIR" -name "Table_ID_*.csv")
    
    if [ -z "$csv_files" ]; then
        log_message "INFO" "No CSV table files found"
        return 0
    fi
    
    log_message "INFO" "Found $(echo "$csv_files" | wc -l) CSV files to process"
    
    # Process each CSV file
    for csv_file in $csv_files; do
        [ -e "$csv_file" ] || continue
        
        base_name=$(basename "$csv_file" .csv)
        log_message "INFO" "Processing table: $base_name"
        
        # Extract table ID from filename
        local table_id=""
        if [[ "$base_name" =~ Table_ID_([^\.]+) ]]; then
            table_id="${BASH_REMATCH[1]}" 
        else
            log_message "WARNING" "Invalid table filename format: $base_name"
            continue
        fi
        
        # Path to the caption file
        caption_file="${TABLE_SRC_DIR}/${base_name}.tex"
        
        # Compiled output file
        compiled_file="$TABLE_COMPILED_DIR/${base_name}.tex"
        
        # Create a debug copy of the CSV file
        cp "$csv_file" "$TABLE_COMPILED_DIR/debug/${base_name}.csv.original"
        
        # Determine the number of columns in the CSV file
        num_columns=$(head -n 1 "$csv_file" | awk -F, '{print NF}')
        
        # Detect table formatting options from caption file
        format_options=$(detect_table_format "$csv_file" "$caption_file")
        
        # Extract formatting options
        fontsize=$(echo "$format_options" | grep -oP '(?<="fontsize":")\w+')
        tabcolsep=$(echo "$format_options" | grep -oP '(?<="tabcolsep":")\w+')
        alignment=$(echo "$format_options" | grep -oP '(?<="alignment":")\w+')
        landscape=$(echo "$format_options" | grep -oP '(?<="landscape":")\w+')
        use_colortbl=$(echo "$format_options" | grep -oP '(?<="use_colortbl":")\w+')
        use_math=$(echo "$format_options" | grep -oP '(?<="use_math":")\w+')
        
        # Extract new formatting options
        table_style=$(echo "$format_options" | grep -oP '(?<="table_style":")\w+')
        caption_pos=$(echo "$format_options" | grep -oP '(?<="caption_pos":")\w+')
        float_pos=$(echo "$format_options" | grep -oP '(?<="float_pos":")\w+')
        scale_to_width=$(echo "$format_options" | grep -oP '(?<="scale_to_width":")\w+')
        header_style=$(echo "$format_options" | grep -oP '(?<="header_style":")\w+')
        auto_width=$(echo "$format_options" | grep -oP '(?<="auto_width":")\w+')
        first_col_bold=$(echo "$format_options" | grep -oP '(?<="first_col_bold":")\w+')
        max_width=$(echo "$format_options" | grep -oP '(?<="max_width":")[^"]*')
        custom_col_spec=$(echo "$format_options" | grep -oP '(?<="custom_col_spec":")[^"]*')
        wrap_text=$(echo "$format_options" | grep -oP '(?<="wrap_text":")\w+')
        multirow=$(echo "$format_options" | grep -oP '(?<="multirow":")\w+')
        
        # Extract table width from caption file
        width=$(grep -oP '(?<=width=)[0-9.]+\\textwidth' "$caption_file" || echo "1\\textwidth")
        
        # Create column specifiers based on options
        col_spec=""
        
        # If custom column spec is provided, use it
        if [ -n "$custom_col_spec" ]; then
            col_spec="{$custom_col_spec}"
            log_message "INFO" "Using custom column spec: $custom_col_spec"
        else
            # Generate column spec based on alignment setting
            case "$alignment" in
                "l") col_spec="{*{$num_columns}{l}}" ;;
                "c") col_spec="{*{$num_columns}{c}}" ;;
                "r") col_spec="{*{$num_columns}{r}}" ;;
                "auto") 
                    # First column left, header columns centered, data columns right
                    col_spec="{l"
                    for ((i=2; i<=$num_columns; i++)); do
                        col_spec="${col_spec}c"
                    done
                    col_spec="${col_spec}}"
                    ;;
                "mixed")
                    # First column left, others right
                    col_spec="{l"
                    for ((i=2; i<=$num_columns; i++)); do
                        col_spec="${col_spec}r"
                    done
                    col_spec="${col_spec}}"
                    ;;
                "smart")
                    # Smart alignment: text columns left, numeric columns right
                    # This requires analysis of data - we'll implement a simple heuristic
                    col_spec="{"
                    for ((i=1; i<=$num_columns; i++)); do
                        # Check first data row to determine if column is numeric
                        col_data=$(awk -F, "NR==2 {print \$$i}" "$csv_file")
                        if [[ "$col_data" =~ ^[0-9.+-]+$ ]]; then
                            # Numeric data, right align
                            col_spec="${col_spec}r"
                        else
                            # Text data, left align
                            col_spec="${col_spec}l"
                        fi
                    done
                    col_spec="${col_spec}}"
                    ;;
                *) col_spec="{*{$num_columns}{r}}" ;;  # Default to right-aligned
            esac
            
            # Add text wrapping if enabled
            if [ "$wrap_text" = "true" ]; then
                # Replace column specs with p{width} for text wrapping
                col_spec=$(echo "$col_spec" | sed -E 's/([lcr])/p{0.15\\textwidth}/g')
                log_message "INFO" "Enabling text wrapping for all columns"
            fi
            
            # Handle first column bold if enabled
            if [ "$first_col_bold" = "true" ]; then
                log_message "INFO" "Making first column bold"
            fi
        fi
        
        # Log all formatting options for debugging
        log_message "INFO" "Table formatting: fontsize=$fontsize, alignment=$alignment, landscape=$landscape, style=$table_style, wrap=$wrap_text"
        
        # Start with a clean output file
        echo "" > "$compiled_file"
        
        # Create the LaTeX table
        {
            # Add landscape environment if requested
            if [ "$landscape" = "true" ]; then
                echo "\\begin{landscape}"
            fi
            
            # Add bookmark for PDF navigation
            echo "\\pdfbookmark[2]{ID ${table_id}}{id_${table_id}}"
            
            # Start table environment
            echo "\\begin{table}[htbp]"
            echo "\\centering"
            
            # Set font size
            case "$fontsize" in
                "tiny") echo "\\tiny" ;;
                "scriptsize") echo "\\scriptsize" ;;
                "footnotesize") echo "\\footnotesize" ;;
                "small") echo "\\small" ;;
                "normalsize") echo "\\normalsize" ;;
                *) echo "\\small" ;;  # Default
            esac
            
            # Set column spacing
            echo "\\setlength{\\tabcolsep}{$tabcolsep}"
            
            # Start tabular environment
            echo "\\begin{tabular}$col_spec"
            echo "\\toprule"
            
            # Process header row
            head -n 1 "$csv_file" | {
                IFS=',' read -ra headers
                local i=1
                local total=${#headers[@]}
                for header in "${headers[@]}"; do
                    # Escape special LaTeX characters
                    header=$(echo "$header" | sed -e 's/±/\\pm/g' -e 's/%/\\%/g' -e 's/_/\\_/g' -e 's/&/\\&/g' -e 's/#/\\#/g' -e 's/\$/\\$/g')
                    
                    # Apply math formatting if enabled
                    if [ "$use_math" = "true" ]; then
                        if [ "$i" -lt "$total" ]; then
                            echo -n "\\textbf{\\thead{\$\\mathrm{$header}\$}} & "
                        else
                            echo -n "\\textbf{\\thead{\$\\mathrm{$header}\$}}"
                        fi
                    else
                        if [ "$i" -lt "$total" ]; then
                            echo -n "\\textbf{\\thead{$header}} & "
                        else
                            echo -n "\\textbf{\\thead{$header}}"
                        fi
                    fi
                    i=$((i+1))
                done
                echo "\\\\"
            }
            
            echo "\\midrule"
            
            # Replace Windows-style newlines first
            tr -d '\r' < "$csv_file" > "${csv_file}.unix"
            
            # Process data rows with AWK
            if [ "$use_colortbl" = "true" ]; then
                # Use alternating row colors
                awk_script="BEGIN {FPAT = \"([^,]*)|(\\\"[^\\\"]+\\\")\"; OFS=\" & \"; row_count=0}
                NR>1 {
                    if (row_count % 2 == 1) {print \"\\\\rowcolor{lightgray}\"}
                    for (i=1; i<=NF; i++) {
                        if (\$i != \"\") {
                            gsub(/^\"|\"\$/, \"\", \$i)  # Remove surrounding quotes
                            gsub(/±/, \"\\\\pm\", \$i)
                            gsub(/%/, \"\\\\%\", \$i)
                            gsub(/_/, \"\\\\_\", \$i)
                            gsub(/&/, \"\\\\&\", \$i)
                            gsub(/#/, \"\\\\#\", \$i)
                            gsub(/\\\$/, \"\\\\\$\", \$i)
                            gsub(/\r/, \"\", \$i)  # Remove carriage return"
                
                if [ "$use_math" = "true" ]; then
                    awk_script="$awk_script
                            \$i = \"\$\\\\mathrm{\" \$i \"}\$\"  # Apply math formatting"
                fi
                
                awk_script="$awk_script
                        } else {
                            \$i = \"\"  # Empty cells
                        }
                    }
                    \$1=\$1  # Force field recomputation
                    print \$0\"\\\\\\\\\"
                    row_count++
                }"
            else
                # No row coloring
                awk_script="BEGIN {FPAT = \"([^,]*)|(\\\"[^\\\"]+\\\")\"; OFS=\" & \"}
                NR>1 {
                    for (i=1; i<=NF; i++) {
                        if (\$i != \"\") {
                            gsub(/^\"|\"\$/, \"\", \$i)  # Remove surrounding quotes
                            gsub(/±/, \"\\\\pm\", \$i)
                            gsub(/%/, \"\\\\%\", \$i)
                            gsub(/_/, \"\\\\_\", \$i)
                            gsub(/&/, \"\\\\&\", \$i)
                            gsub(/#/, \"\\\\#\", \$i)
                            gsub(/\\\$/, \"\\\\\$\", \$i)
                            gsub(/\r/, \"\", \$i)  # Remove carriage return"
                
                if [ "$use_math" = "true" ]; then
                    awk_script="$awk_script
                            \$i = \"\$\\\\mathrm{\" \$i \"}\$\"  # Apply math formatting"
                fi
                
                awk_script="$awk_script
                        } else {
                            \$i = \"\"  # Empty cells
                        }
                    }
                    \$1=\$1  # Force field recomputation
                    print \$0\"\\\\\\\\\"
                }"
            fi
            
            # Execute the AWK script
            awk "$awk_script" "${csv_file}.unix"
            
            # Clean up temporary file
            rm "${csv_file}.unix"
            
            # Finish table
            echo "\\bottomrule"
            echo "\\end{tabular}"
            
            # Set caption width
            echo "\\captionsetup{width=$width}"
            
            # Include the caption
            echo "\\input{${caption_file}}"
            echo "\\label{tab:${table_id}}"
            echo "\\end{table}"
            
            # Close landscape environment if used
            if [ "$landscape" = "true" ]; then
                echo "\\end{landscape}"
            fi
            
            echo ""
            
        } > "$compiled_file"
        
        # Save processed file for debugging
        cp "$compiled_file" "$TABLE_COMPILED_DIR/debug/${base_name}.tex.processed"
        
        log_message "INFO" "Table $base_name processed successfully"
    done
    
    log_message "INFO" "All tables processed"
}

gather_tex_files() {
    # Gather ./src/tables/.tex/Table_*.tex files into ./src/tables/.tex/.All_Tables.tex
    echo "" > "$TABLE_HIDDEN_DIR"/.All_Tables.tex
    for table_tex in "$TABLE_COMPILED_DIR"/Table_ID_*.tex; do
        if [ -f "$table_tex" ] || [ -L "$table_tex" ]; then
            fname="${table_tex%.tex}"
            echo "\input{${fname}}" >> "$TABLE_HIDDEN_DIR"/.All_Tables.tex
        fi
    done
}


main() {
    init
    ensure_lower_letters
    ensure_caption
    csv2tex
    gather_tex_files
    }

main "$@"

## EOF

# To fit tables in LaTeX and control their layout:

# 1. Use `table*` for wide tables spanning two columns.
# 2. Adjust font size: `\small`, `\footnotesize`, or `\tiny`.
# 3. Reduce column spacing: `\setlength{\tabcolsep}{4pt}`.
# 4. Use `\resizebox{\textwidth}{!}{...}` to scale the table.
# 5. For landscape orientation:
#    ```latex
#    \usepackage{pdflscape}
#    \begin{landscape}
#      % Your table here
#    \end{landscape}
#    ```
# 6. Consider splitting large tables across multiple pages using `longtable` or `supertabular` packages.
