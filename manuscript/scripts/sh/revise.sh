#!/bin/bash

function revise() {
  echo -e "The following texfiles are being revised:\n"
  echo -e "${files_to_revise// /\\n}"
  echo
  read -p "Is it okay to proceed? (y/n) " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo $files_to_revise | xargs -n 1 -P 5 ./.env/bin/python ./scripts/py/revise_by_GPT.py -l
  fi
}

source ./scripts/sh/modules/load_files_list.sh

# Load from the config file
config_file_path="./config/files_to_revise.txt"
files_to_revise=$(load_files_list "$config_file_path")

# Main
revise $files_to_revise

# ./scripts/sh/revise.sh
