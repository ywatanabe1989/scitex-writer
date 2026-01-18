#!/bin/bash
# -*- coding: utf-8 -*-
# File: scripts/maintenance/show_usage.sh
# Description: Display project usage guide

echo ""
echo "╭────────────────────────────────────────────────────────────────╮"
echo "│  SciTeX Writer - Project Usage Guide                           │"
echo "╰────────────────────────────────────────────────────────────────╯"
echo ""
echo "Project Structure:"
echo "  00_shared/           Shared: title, authors, keywords, journal_name, bib_files/"
echo "  01_manuscript/       Main manuscript (abstract, intro, methods, results, discussion)"
echo "  02_supplementary/    Supplementary materials (methods, results, figures, tables)"
echo "  03_revision/         Revision responses (editor/, reviewer1/, reviewer2/)"
echo ""
echo "Compilation Scripts:"
echo "  ./compile.sh manuscript       Compile main manuscript"
echo "  ./compile.sh supplementary    Compile supplementary materials"
echo "  ./compile.sh revision         Compile revision responses"
echo ""
echo "Script Options:"
echo "  --no-figs        Skip figure processing (faster compilation)"
echo "  --no-tables      Skip table processing"
echo "  --no-diff        Skip diff generation (saves ~10s)"
echo "  --draft          Single-pass compilation (saves ~5s)"
echo "  --quiet          Suppress verbose output"
echo "  --verbose        Show detailed logs"
echo "  --dark-mode      Black background, white text"
echo ""
echo "Quick Examples:"
echo "  ./compile.sh manuscript                    # Full compilation"
echo "  ./compile.sh manuscript --draft --no-diff  # Fast draft mode"
echo "  make manuscript                            # Via Makefile"
echo ""
echo "For more details: make help"
echo ""

# EOF
