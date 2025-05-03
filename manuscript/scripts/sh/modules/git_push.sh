#!/bin/bash

echo -e "$0 ...\n"

latest_version=$(readlink ./old/.manuscript.pdf | grep -oP '(?<=compiled_v)\d+')
git add .
git commit -m "v$latest_version"
git push

## shell
