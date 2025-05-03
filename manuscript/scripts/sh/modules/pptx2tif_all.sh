#!/bin/bash

echo -e "$0 ..."

source ./scripts/sh/modules/config.sh

# PowerPoint to TIF
total=$(ls "$FIGURE_SRC_DIR"/Figure_ID_*.pptx | wc -l)
ls "$FIGURE_SRC_DIR"/Figure_ID_*.pptx | \
parallel --eta --progress --joblog progress.log \
    './scripts/sh/modules/pptx2tif.sh -i "$(realpath {})" -o "$(realpath {.}.tif)"; \
    echo "Processed: {#}/$total"'

## EOF

# #!/bin/bash

# echo -e "$0 ..."

# source ./scripts/sh/modules/config.sh

# # PowerPoint to TIF
# ls "$FIGURE_SRC_DIR"/Figure_ID_*.pptx | \
# parallel ./scripts/sh/modules/pptx2tif.sh -i "$(realpath {})" -o "$(realpath {.}.tif)"

# ## EOF
