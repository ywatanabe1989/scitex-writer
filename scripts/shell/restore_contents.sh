#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: 2026-02-09
# File: scripts/shell/restore_contents.sh
# Purpose: Restore content files from a snapshot created by initialize_contents.sh
# Usage: restore_contents.sh [snapshot-id]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

cd "$PROJECT_ROOT"

# Content paths to restore
CONTENT_PATHS=(
    "00_shared/title.tex"
    "00_shared/authors.tex"
    "00_shared/keywords.tex"
    "00_shared/journal_name.tex"
    "00_shared/bib_files/"
    "01_manuscript/contents/"
    "02_supplementary/contents/"
    "03_revision/contents/"
)

# --------------------------------------------------------------------------
# No argument: list available snapshots
# --------------------------------------------------------------------------
if [ $# -eq 0 ]; then
    echo -e "${YELLOW}=== Available Snapshots ===${NC}"
    echo ""

    snapshots=$(git tag -l "snapshot/pre-init-*" --sort=-version:refname 2>/dev/null)
    if [ -z "$snapshots" ]; then
        echo "No snapshots found."
        echo "Snapshots are created automatically by 'make init'."
        exit 0
    fi

    while IFS= read -r tag; do
        commit=$(git rev-list -1 "$tag" 2>/dev/null)
        date=$(git log -1 --format="%ci" "$commit" 2>/dev/null | cut -d' ' -f1,2)
        short=$(git log -1 --format="%s" "$commit" 2>/dev/null)
        echo -e "  ${GREEN}${tag}${NC}  (${date})  ${short}"
    done <<<"$snapshots"

    echo ""
    echo "Usage: make restore ID=<snapshot-tag>"
    exit 0
fi

# --------------------------------------------------------------------------
# With argument: restore from snapshot
# --------------------------------------------------------------------------
SNAPSHOT_ID="$1"

if ! git rev-parse "$SNAPSHOT_ID" &>/dev/null; then
    echo -e "${RED}Error: Snapshot '${SNAPSHOT_ID}' not found.${NC}"
    echo "Run 'make restore' (without ID) to list available snapshots."
    exit 1
fi

echo -e "${YELLOW}=== Restore Contents from Snapshot ===${NC}"
echo ""
echo "Snapshot: ${SNAPSHOT_ID}"
echo "Restoring:"
for p in "${CONTENT_PATHS[@]}"; do
    echo "  - ${p}"
done
echo ""

read -rp "Proceed with restore? (y/N): " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "Aborted."
    exit 0
fi

echo ""
for p in "${CONTENT_PATHS[@]}"; do
    if git ls-tree -r "$SNAPSHOT_ID" -- "$p" &>/dev/null; then
        git checkout "$SNAPSHOT_ID" -- "$p" 2>/dev/null || true
        echo -e "  ${GREEN}Restored:${NC} ${p}"
    else
        echo -e "  ${YELLOW}Skipped:${NC} ${p} (not in snapshot)"
    fi
done

echo ""
echo -e "${GREEN}Contents restored from ${SNAPSHOT_ID}.${NC}"
echo "Review changes with: git diff"

###% EOF
