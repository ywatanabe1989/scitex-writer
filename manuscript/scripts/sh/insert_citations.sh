#!/bin/bash

function insert_citations() {
  echo -e "The following TeX files will have citations inserted:\n"  
  echo -e "${files_to_insert_citations// /\\n}"
  echo
  read -p "Is it okay to proceed? (y/n) " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo $files_to_insert_citations | xargs -n 1 -P 5 ./.env/bin/python ./scripts/py/insert_citations.py -lb "./bibliography.bib" -lt
  fi
}

source ./scripts/sh/modules/load_files_list.sh

config_file_path="./config/files_to_insert_citations.txt"
files_to_insert_citations=$(load_files_list "$config_file_path")

# Main
insert_citations $files_to_insert_citations

# ./scripts/sh/insert_citations.sh ./src/introduction.tex ./bibliography.bib


