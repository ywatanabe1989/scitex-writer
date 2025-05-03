#!/bin/bash

echo -e "$0 ...\n"

source ./scripts/sh/modules/config.sh

init() {
    rm -f $WORDCOUNT_DIR/*.txt
    mkdir -p $WORDCOUNT_DIR
}

_count_elements() {
    local dir="$1"
    local pattern="$2"
    local output_file="$3"

    if [[ -n $(find "$dir" -name "$pattern" 2>/dev/null) ]]; then
        count=$(ls "$dir"/$pattern | wc -l)
        echo $count > "$output_file"
    else
        echo "0" > "$output_file"
    fi
}

_count_words() {
    local input_file="$1"
    local output_file="$2"

    texcount "$input_file" -inc -1 -sum > "$output_file"
}

count_tables() {
    _count_elements "$TABLE_COMPILED_DIR" "Table_ID_*.tex" "$WORDCOUNT_DIR/table_count.txt"
}

count_figures() {
    _count_elements "$FIGURE_COMPILED_DIR" "Figure_ID_*.tex" "$WORDCOUNT_DIR/figure_count.txt"
}

count_IMRaD() {
    for section in abstract introduction methods results discussion; do
        local section_tex="./src/$section.tex"
        if [ -e "$section_tex" ]; then
            _count_words "$section_tex" "$WORDCOUNT_DIR/${section}_count.txt"
            # echo $section_tex
            # cat "$WORDCOUNT_DIR/${section}_count.txt"
        else
            echo 0 > "$WORDCOUNT_DIR/${section}_count.txt"
        fi
    done
    cat $WORDCOUNT_DIR/{introduction,methods,results,discussion}_count.txt | awk '{s+=$1} END {print s}' > $WORDCOUNT_DIR/imrd_count.txt
}

# echo_results() {
#     for f in $WORDCOUNT_DIR/*.txt; do
#         echo $f && cat $f
#     done
#     }

main() {
    init
    count_tables
    count_figures
    count_IMRaD
    # echo_results
}

main

# EOF



# ## EOF

# #!/bin/bash

# echo -e "$0 ..."

# source ./scripts/sh/modules/config.sh

# init(){
# # Prepares a directory
# mkdir -p $WORDCOUNT_DIR
# }

# # # Count tables
# # # table_count=`ls ./src/tables/*.tex | wc -l`
# # table_count=`ls "$TABLE_COMPILED_DIR"/Table_ID_*.tex | wc -l`
# # echo $table_count > $WORDCOUNT_DIR/table_count.txt

# # # Count figures
# # figure_count=`ls "$FIGURE_COMPILED_DIR"/Figure_ID_*.tex | wc -l`
# # echo $figure_count > $WORDCOUNT_DIR/figure_count.txt
# # Count tables
# if [[ -n $(find "$TABLE_COMPILED_DIR" -name "Table_ID_*.tex" 2>/dev/null) ]]; then
#     table_count=$(ls "$TABLE_COMPILED_DIR"/Table_ID_*.tex | wc -l)
#     echo $table_count > $WORDCOUNT_DIR/table_count.txt
# else
#     echo "0" > $WORDCOUNT_DIR/table_count.txt
# fi

# # Count figures
# if [[ -n $(find "$FIGURE_COMPILED_DIR" -name "Figure_ID_*.tex" 2>/dev/null) ]]; then
#     figure_count=$(ls "$FIGURE_COMPILED_DIR"/Figure_ID_*.tex | wc -l)
#     echo $figure_count > $WORDCOUNT_DIR/figure_count.txt
# else
#     echo "0" > $WORDCOUNT_DIR/figure_count.txt
# fi


# # Calculate word counts for each section and save to files
# texcount ./src/abstract.tex -inc -1 -sum > $WORDCOUNT_DIR/abstract_count.txt
# texcount ./src/introduction.tex -inc -1 -sum > $WORDCOUNT_DIR/introduction_count.txt
# texcount ./src/methods.tex -inc -1 -sum > $WORDCOUNT_DIR/methods_count.txt
# texcount ./src/results.tex -inc -1 -sum > $WORDCOUNT_DIR/results_count.txt
# texcount ./src/discussion.tex -inc -1 -sum > $WORDCOUNT_DIR/discussion_count.txt

# # Calculate word count for IMRaD excluding abstract
# cat $WORDCOUNT_DIR/{introduction,methods,results,discussion}_count.txt | awk '{s+=$1} END {print s}' > $WORDCOUNT_DIR/imrd_count.txt

# ## EOF
