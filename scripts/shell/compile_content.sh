#!/bin/bash
# -*- coding: utf-8 -*-
# ROLE: engine-vendored — DO NOT edit here. `scitex-writer update-project`
# overwrites this file on every re-vendor; fix it upstream in the
# scitex-writer package instead (local edits are lost, and update-project
# may set it read-only in the consumer workspace after vendoring).
# Timestamp: 2026-02-08
# File: scripts/shell/compile_content.sh

################################################################################
# Content/preview LaTeX compilation
# Compiles a .tex file to PDF using latexmk (no bibliography processing)
################################################################################

set -e
set -o pipefail

# Defaults
TEX_FILE=""
OUTPUT_DIR=""
JOB_NAME="content"
COLOR_MODE="light"
PREVIEW_DIR=""
TIMEOUT=60
KEEP_AUX=false
QUIET=false

# Colors
GRAY='\033[0;90m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { [ "$QUIET" = true ] || echo -e "${GRAY}INFO: $1${NC}"; }
log_success() { echo -e "${GREEN}SUCC: $1${NC}"; }
log_error() { echo -e "${RED}ERRO: $1${NC}" >&2; }

show_usage() {
    cat <<EOF
Usage: compile_content.sh --tex-file PATH --output-dir PATH [OPTIONS]

Compile a LaTeX .tex file to PDF (content/preview mode, no bibliography).

REQUIRED:
    --tex-file PATH       Input .tex file to compile
    --output-dir PATH     Directory for output PDF

OPTIONS:
    --job-name NAME       latexmk job name (default: content)
    --color-mode MODE     light|dark (default: light)
    --preview-dir PATH    Copy PDF to this directory after compilation
    --timeout SECS        Compilation timeout (default: 60)
    --keep-aux            Keep auxiliary files (.aux, .log, etc.)
    -q, --quiet           Suppress output
    -h, --help            Show this help

EXAMPLES:
    compile_content.sh --tex-file /tmp/preview.tex --output-dir /tmp/out
    compile_content.sh --tex-file /tmp/preview.tex --output-dir /tmp/out --color-mode dark
    compile_content.sh --tex-file /tmp/preview.tex --output-dir /tmp/out --preview-dir ./project/.preview
EOF
}

# Parse arguments
while [ $# -gt 0 ]; do
    case $1 in
    --tex-file | --tex_file)
        TEX_FILE="$2"
        shift 2
        ;;
    --tex-file=* | --tex_file=*)
        TEX_FILE="${1#*=}"
        shift
        ;;
    --output-dir | --output_dir)
        OUTPUT_DIR="$2"
        shift 2
        ;;
    --output-dir=* | --output_dir=*)
        OUTPUT_DIR="${1#*=}"
        shift
        ;;
    --job-name | --job_name)
        JOB_NAME="$2"
        shift 2
        ;;
    --job-name=* | --job_name=*)
        JOB_NAME="${1#*=}"
        shift
        ;;
    --color-mode | --color_mode)
        COLOR_MODE="$2"
        shift 2
        ;;
    --color-mode=* | --color_mode=*)
        COLOR_MODE="${1#*=}"
        shift
        ;;
    --preview-dir | --preview_dir)
        PREVIEW_DIR="$2"
        shift 2
        ;;
    --preview-dir=* | --preview_dir=*)
        PREVIEW_DIR="${1#*=}"
        shift
        ;;
    --timeout)
        TIMEOUT="$2"
        shift 2
        ;;
    --timeout=*)
        TIMEOUT="${1#*=}"
        shift
        ;;
    --keep-aux | --keep_aux)
        KEEP_AUX=true
        shift
        ;;
    -q | --quiet)
        QUIET=true
        shift
        ;;
    -h | --help)
        show_usage
        exit 0
        ;;
    *)
        log_error "Unknown argument: $1"
        show_usage
        exit 1
        ;;
    esac
done

# Validate required arguments
if [ -z "$TEX_FILE" ]; then
    log_error "Missing required argument: --tex-file"
    exit 1
fi

if [ -z "$OUTPUT_DIR" ]; then
    log_error "Missing required argument: --output-dir"
    exit 1
fi

if [ ! -f "$TEX_FILE" ]; then
    log_error "TeX file not found: $TEX_FILE"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Per-(project, section, color_mode) serialization via flock(2).
#
# Background (G3, follow-up to G2 atomic publish, 2026-06-10):
# G2 made the .preview publish atomic so concurrent compiles never
# observe a half-written PDF. But the underlying latexmk run still
# races: two simultaneous compiles for the same (project, section,
# color_mode) triple share $OUTPUT_DIR (or worse, a single project's
# tmp dir resolved per-invocation), step on each other's .aux / .log /
# .fdb_latexmk intermediates, and produce non-deterministic exit codes.
# The UI's Compile-on-Change loop fires the same triple repeatedly,
# so this is the live failure mode.
#
# Strategy: take an exclusive flock on a lockfile derived from the
# triple — keyed off $PREVIEW_DIR (which is the project's `.preview/`
# directory, unique per project) + $JOB_NAME (which encodes section +
# color, since content.py composes the basename as `<section>_<color>`
# or similar). Same triple → same lockfile → strict serialization.
# Different triple → different lockfile → no contention.
#
# fd 200 holds the lock for the entire script lifetime; the kernel
# auto-releases on script exit (close-on-exec semantics on fd close).
# `-w $TIMEOUT` bounds the wait so a wedged previous compile cannot
# starve a new request indefinitely — if the lock cannot be acquired
# within $TIMEOUT seconds, exit with a clear error rather than blocking
# the daphne worker forever.
#
# Only fires when --preview-dir is given (i.e., when there is a shared
# destination that could race). CLI single-shot use cases (no preview
# dir → no shared destination) skip the lock and stay non-blocking.
if [ -n "$PREVIEW_DIR" ]; then
    mkdir -p "$PREVIEW_DIR"
    LOCK_FILE="$PREVIEW_DIR/.lock.$JOB_NAME"
    exec 200>"$LOCK_FILE"
    if ! flock -x -w "$TIMEOUT" 200; then
        log_error "Could not acquire compile lock $LOCK_FILE within ${TIMEOUT}s — concurrent compile of $JOB_NAME holding it longer than expected"
        exit 1
    fi
    log_info "Acquired compile lock: $LOCK_FILE"
fi

log_info "Compiling content: $JOB_NAME (color_mode=$COLOR_MODE)"

# Run latexmk (no bibliography processing for content/preview)
timeout "$TIMEOUT" latexmk \
    -pdf \
    -synctex=1 \
    -interaction=nonstopmode \
    -halt-on-error \
    -bibtex- \
    -jobname="$JOB_NAME" \
    -output-directory="$OUTPUT_DIR" \
    "$TEX_FILE"

COMPILE_EXIT=$?

if [ $COMPILE_EXIT -ne 0 ]; then
    log_error "latexmk failed with exit code $COMPILE_EXIT"
    exit $COMPILE_EXIT
fi

PDF_FILE="$OUTPUT_DIR/$JOB_NAME.pdf"

if [ ! -f "$PDF_FILE" ]; then
    log_error "PDF not generated: $PDF_FILE"
    exit 1
fi

log_success "PDF generated: $PDF_FILE"

# Copy to preview directory if specified — atomic (tmp + mv -f).
#
# Background (2026-06-10, proj-scitex-hub diagnosis confirmed in prod by
# lead): the UI's Compile-on-Change auto-firing for the same
# (project, section, color_mode) triple causes daphne's asyncio +
# sync_to_async threadpool to invoke compile_content() concurrently
# against the same .preview/<job_name>.pdf destination. The previous
# `cp $PDF_FILE $PREVIEW_DIR/` is a raw write under `set -e` and races
# (mid-write open + read, partial flushes, cp itself short-circuiting
# with a non-zero exit) — surfacing as `Compilation failed with exit
# code N` at content.py:186 even though the compile itself succeeded.
#
# Atomic write: stage to a uniquely-named temp file (PID-suffixed so
# parallel processes do not collide on the tmp slot itself) inside the
# SAME directory as the publish target, then `mv -f` it into place.
# `mv` within one filesystem is rename(2), which is atomic — concurrent
# readers either see the OLD pdf or the NEW pdf, never a half-written
# fd. The `.` prefix on the tmp name keeps it out of normal directory
# listings if any reader walks $PREVIEW_DIR.
#
# Failure modes are explicit (non-zero exit + cleanup) rather than
# inheriting `set -e`'s opaque propagation, so content.py sees a
# coherent error code instead of the indeterminate exit 12 race.
if [ -n "$PREVIEW_DIR" ]; then
    mkdir -p "$PREVIEW_DIR"
    PREVIEW_TMP="$PREVIEW_DIR/.$JOB_NAME.pdf.tmp.$$"
    if ! cp "$PDF_FILE" "$PREVIEW_TMP"; then
        log_error "Failed to stage PDF to $PREVIEW_TMP"
        rm -f "$PREVIEW_TMP"
        exit 1
    fi
    if ! mv -f "$PREVIEW_TMP" "$PREVIEW_DIR/$JOB_NAME.pdf"; then
        log_error "Failed to publish PDF to $PREVIEW_DIR/$JOB_NAME.pdf"
        rm -f "$PREVIEW_TMP"
        exit 1
    fi
    log_info "Copied to preview: $PREVIEW_DIR/$JOB_NAME.pdf (atomic)"
fi

# Cleanup auxiliary files
if [ "$KEEP_AUX" = false ]; then
    for ext in aux log fls fdb_latexmk out bbl blg toc lof lot; do
        rm -f "$OUTPUT_DIR/$JOB_NAME.$ext"
    done
    log_info "Cleaned auxiliary files"
fi

exit 0

# EOF
