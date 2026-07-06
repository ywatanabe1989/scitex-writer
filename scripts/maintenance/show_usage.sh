#!/bin/bash
# -*- coding: utf-8 -*-
# ROLE: engine-vendored — DO NOT edit here. `scitex-writer update-project`
# overwrites this file on every re-vendor; fix it upstream in the
# scitex-writer package instead (local edits are lost, and update-project
# may set it read-only in the consumer workspace after vendoring).
# File: scripts/maintenance/show_usage.sh
# Description: Display project usage guide (delegates to compile.sh --help-recursive)

# Resolve project root
THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$THIS_DIR/../.." && pwd)"

# Colors
BOLD_CYAN='\033[1;36m'
GRAY='\033[0;90m'
GREEN='\033[0;32m'
NC='\033[0m'

echo ""
echo -e "${BOLD_CYAN}╭────────────────────────────────────────────────────────────────╮${NC}"
echo -e "${BOLD_CYAN}│  SciTeX Writer - Project Usage Guide                           │${NC}"
echo -e "${BOLD_CYAN}╰────────────────────────────────────────────────────────────────╯${NC}"
echo ""
echo -e "${GRAY}Project Root:${NC} $PROJECT_ROOT"
echo ""
echo -e "${BOLD_CYAN}━━━ Project Structure ━━━${NC}"
echo -e "  ${GREEN}00_shared/${NC}           Shared: title, authors, keywords, journal_name, bib_files/"
echo -e "  ${GREEN}01_manuscript/${NC}       Main manuscript (abstract, intro, methods, results, discussion)"
echo -e "  ${GREEN}02_supplementary/${NC}    Supplementary materials (methods, results, figures, tables)"
echo -e "  ${GREEN}03_revision/${NC}         Revision responses (editor/, reviewer1/, reviewer2/)"
echo ""

# Delegate to compile.sh --help-recursive for detailed documentation
"$PROJECT_ROOT/compile.sh" --help-recursive

# EOF
