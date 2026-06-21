#!/bin/bash
# -*- coding: utf-8 -*-
# Test: figure JPG placement in jpg_for_compilation is symlink-first
#       with cp + WARN fallback (operator decision 1b, 2026-06-12).
#
# Drives copy_composed_figures_to_jpg_for_compilation against a temp
# fixture so we don't need a real manuscript repo.

# NOTE: no `set -e` because the function under test uses `((var++))` which
# returns exit 1 on the FIRST increment from 0. That's harmless in the
# production caller (no -e there) and we don't want to penalise the function
# with a `|| true` just to satisfy the test fixture's strictness.
set -u

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$THIS_DIR/../../../.." && pwd)"
MODULES_DIR="$REPO_ROOT/scripts/shell/modules/process_figures_modules"

PASS=0
FAIL=0
TOTAL=0

pass() { echo "  PASS: $1"; PASS=$((PASS+1)); TOTAL=$((TOTAL+1)); }
fail() { echo "  FAIL: $1"; FAIL=$((FAIL+1)); TOTAL=$((TOTAL+1)); }

# shellcheck disable=SC1091
source "$MODULES_DIR/00_common.src"
# shellcheck disable=SC1091
source "$MODULES_DIR/02_format_conversion.src"

WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT

export SCITEX_WRITER_FIGURE_CAPTION_MEDIA_DIR="$WORKDIR/captions"
export SCITEX_WRITER_FIGURE_JPG_DIR="$WORKDIR/jpgs"
mkdir -p "$SCITEX_WRITER_FIGURE_CAPTION_MEDIA_DIR"
mkdir -p "$SCITEX_WRITER_FIGURE_JPG_DIR"

# Three figures: 01.jpg (main), 02.jpg (main), 01a_panel.jpg (panel — must be skipped)
echo "main-1" > "$SCITEX_WRITER_FIGURE_CAPTION_MEDIA_DIR/01.jpg"
echo "main-2" > "$SCITEX_WRITER_FIGURE_CAPTION_MEDIA_DIR/02.jpg"
echo "panel"  > "$SCITEX_WRITER_FIGURE_CAPTION_MEDIA_DIR/01a_panel.jpg"

# Capture stdout/stderr to keep test output quiet.
copy_composed_jpg_files > "$WORKDIR/run.log" 2>&1

# Assertions ----------------------------------------------------------------

# 1. Main figures land in the destination.
if [ -e "$SCITEX_WRITER_FIGURE_JPG_DIR/01.jpg" ]; then
  pass "01.jpg placed in jpg_for_compilation"
else
  fail "01.jpg missing from jpg_for_compilation"
fi
if [ -e "$SCITEX_WRITER_FIGURE_JPG_DIR/02.jpg" ]; then
  pass "02.jpg placed in jpg_for_compilation"
else
  fail "02.jpg missing from jpg_for_compilation"
fi

# 2. Panel file was skipped.
if [ ! -e "$SCITEX_WRITER_FIGURE_JPG_DIR/01a_panel.jpg" ]; then
  pass "panel file (01a_panel.jpg) was skipped"
else
  fail "panel file (01a_panel.jpg) leaked into jpg_for_compilation"
fi

# 3. On a tmpfs-style FS that supports symlinks, the placement IS a symlink
#    (the new behaviour). On a hostile FS it falls back to a regular file —
#    accept either, but at least one of (symlink, regular file) must hold,
#    and the symlink path must point at the original abs source when used.
if [ -L "$SCITEX_WRITER_FIGURE_JPG_DIR/01.jpg" ]; then
  link_target="$(readlink "$SCITEX_WRITER_FIGURE_JPG_DIR/01.jpg")"
  expected_target="$(readlink -f "$SCITEX_WRITER_FIGURE_CAPTION_MEDIA_DIR/01.jpg")"
  if [ "$link_target" = "$expected_target" ]; then
    pass "01.jpg is a symlink pointing at absolute source"
  else
    fail "01.jpg symlink points at '$link_target' (expected '$expected_target')"
  fi
elif [ -f "$SCITEX_WRITER_FIGURE_JPG_DIR/01.jpg" ]; then
  # fallback path — acceptable, must have warned.
  if grep -q "Symlink unsupported" "$WORKDIR/run.log"; then
    pass "fallback to cp emitted WARN as designed"
  else
    fail "fallback to cp did not WARN"
  fi
else
  fail "01.jpg is neither symlink nor file"
fi

# 4. Reading through the symlinked dest returns the source bytes — this is
#    the property pdflatex / latexdiff rely on (POSIX symlink follow). If
#    this passes, downstream LaTeX tools will see the figure unchanged.
expected="$(cat "$SCITEX_WRITER_FIGURE_CAPTION_MEDIA_DIR/01.jpg")"
actual="$(cat "$SCITEX_WRITER_FIGURE_JPG_DIR/01.jpg")"
if [ "$expected" = "$actual" ]; then
  pass "read-through-symlink returns source bytes (pdflatex/latexdiff will follow)"
else
  fail "read-through-symlink returned '$actual' but source is '$expected'"
fi

# 5. Edits to the upstream source propagate without re-running placement —
#    the whole point of switching to symlinks.
echo "edited-source" > "$SCITEX_WRITER_FIGURE_CAPTION_MEDIA_DIR/01.jpg"
if [ "$(cat "$SCITEX_WRITER_FIGURE_JPG_DIR/01.jpg")" = "edited-source" ]; then
  pass "upstream edits propagate to jpg_for_compilation without re-link"
else
  fail "upstream edits did NOT propagate (defeats the purpose of switching to symlink)"
fi

# 6. Re-running over-writes (ln -sf semantics) without error.
copy_composed_jpg_files > "$WORKDIR/run2.log" 2>&1
if [ -e "$SCITEX_WRITER_FIGURE_JPG_DIR/01.jpg" ]; then
  pass "second run is idempotent (01.jpg still present)"
else
  fail "second run lost 01.jpg"
fi

echo "----"
echo "Results: $PASS/$TOTAL passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
