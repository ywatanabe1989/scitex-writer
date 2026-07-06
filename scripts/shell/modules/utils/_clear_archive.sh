#!/bin/bash
# ROLE: engine-vendored — DO NOT edit here. `scitex-writer update-project`
# overwrites this file on every re-vendor; fix it upstream in the
# scitex-writer package instead (local edits are lost, and update-project
# may set it read-only in the consumer workspace after vendoring).

echo -e "$0 ..."

rm compiled_v* diff_v* -f
mv old .old/old-$(date +%s)

## EOF
