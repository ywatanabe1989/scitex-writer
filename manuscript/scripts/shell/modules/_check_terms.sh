#!/bin/bash

echo -e "$0 ..."

function check_terms() {
  echo -e "\nChecking terms in ${1}"
  ./.env/bin/python ./scripts/python/check_terms_by_GPT.py -l "${1}" | tee ./.logs/term_check_results.txt
  echo "Results logged in ./.logs/term_check_results.txt"
}

# Main
file_to_check_terms=./manuscript.tex
check_terms $file_to_check_terms

# ./scripts/shell/check_terms.sh
