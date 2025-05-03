#!/bin/bash

echo -e "$0 ...\n"

rm compiled_v* diff_v* -f
mv old .old/old-$(date +%s)

## EOF
