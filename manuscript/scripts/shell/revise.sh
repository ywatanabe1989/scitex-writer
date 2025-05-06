#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-06 12:51:18 (ywatanabe)"
# File: ./manuscript/scripts/shell/revise.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
touch "$LOG_PATH" >/dev/null 2>&1


source ./scripts/shell/modules/load_files_list.sh

function revise() {
  echo -e "The following texfiles are being revised:\n"
  echo -e "${files_to_revise// /\\n}"
  echo
  read -p "Is it okay to proceed? (y/n) " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo $files_to_revise | xargs -n 1 -P 5 ./.env/bin/python ./scripts/python/revise_by_GPT.py -l
  fi
}



# Load from the config file
config_file_path="./config/files_to_revise.txt"
files_to_revise=$(load_files_list "$config_file_path")

# Main
revise $files_to_revise

# ./scripts/shell/revise.sh

# EOF