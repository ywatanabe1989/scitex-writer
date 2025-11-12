# SciTeX Writer Logging System

## Clean, Readable Output

The logging system has been reorganized to provide clean, easy-to-read, meaningful logs.

## Key Improvements

### 1. Clean Header/Footer
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SciTeX Writer Compilation
  Type: manuscript
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

... compilation stages ...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Compilation Complete
  Total time: 16s
  Output: ./01_manuscript/manuscript.pdf
  Log: ./01_manuscript/logs/global.log
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 2. Clean Stage Markers
**Before:**
```
INFO: [11:26:10] Starting: Dependency Check
... output ...
SUCC: [11:26:11] Completed: Dependency Check (1s elapsed, 3s total)
```

**After:**
```
▸ Dependency Check
... output ...
✓ Dependency Check (1s)
```

### 3. Quieter Git Operations
**Before:**
```
[develop 10336c6] chore: Auto-archive manuscript v125
 5 files changed, 11803 insertions(+), 1 deletion(-)
 create mode 100644 01_manuscript/archive/manuscript_v125.pdf
 create mode 100644 01_manuscript/archive/manuscript_v125.tex
 ...
SUCC:     Git commit created: manuscript v125
SUCC:     Git tag created: manuscript-v125
```

**After:**
```
✓ Git commit: manuscript v126
✓ Git tag: manuscript-v126
```
(Detailed git output moved to log files)

### 4. Consistent Symbol Usage
- `▸` Stage start
- `✓` Success
- `⚠` Warning
- `✗` Error
- `→` Process (verbose mode)
- `•` Task (debug mode)

## Log Levels

Control verbosity with `SCITEX_LOG_LEVEL`:

```bash
# Quiet (errors and warnings only)
export SCITEX_LOG_LEVEL=0
./compile.sh manuscript

# Normal (default - shows stages and results)
export SCITEX_LOG_LEVEL=1
./compile.sh manuscript

# Verbose (shows all process details)
export SCITEX_LOG_LEVEL=2
./compile.sh manuscript

# Debug (shows everything including file operations)
export SCITEX_LOG_LEVEL=3
./compile.sh manuscript
```

## Configuration

Edit `/home/ywatanabe/proj/scitex-writer/config/logging.conf`:

```bash
# Verbosity level (0=quiet, 1=normal, 2=verbose, 3=debug)
SCITEX_LOG_LEVEL=1

# Show script paths in "Running..." messages
SCITEX_LOG_SHOW_PATHS=false

# Show individual file operations
SCITEX_LOG_SHOW_FILES=false

# Show git command output
SCITEX_LOG_SHOW_GIT=false
```

## Migration Status

### ✅ Completed
- Main compilation interface (compile.sh)
- Manuscript compilation script
- Git auto-commit module
- Stage start/end format
- Final summary format

### 🔄 In Progress (Optional)
- Submodule logging (process_figures.sh, process_tables.sh, etc.)
- Config loading messages
- Parallel processing output format

### Gradual Migration Strategy

The system uses **compatibility aliases** to allow gradual migration:

```bash
# Old style (still works)
echo_info "Running script..."
echo_success "Done!"

# New style (preferred)
log_process "Running script..."
log_success "Done!"
```

All old functions still work, so scripts can be migrated incrementally.

## Example Output

### Normal Mode (SCITEX_LOG_LEVEL=1)
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SciTeX Writer Compilation
  Type: manuscript
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

▸ Dependency Check
  ✓ All native LaTeX commands available
✓ Dependency Check (1s)

▸ Bibliography Merge
✓ Bibliography Merge (0s)

▸ Citation Style
  ✓ Citation style already set: unsrtnat
✓ Citation Style (0s)

▸ TeX Compilation (Structure)
==============================================================================
Thank you for citing SciTeX Writer! 🙏

Your support helps maintain this open-source project.
Citation found: \cite{scitex}
==============================================================================

  ✓ ./01_manuscript/manuscript.tex compiled
✓ TeX Compilation (Structure) (1s)

▸ PDF Generation
  ✓ ./01_manuscript/manuscript.pdf ready (348K)
✓ PDF Generation (4s)

▸ Diff Generation
  ✓ ./01_manuscript/manuscript_diff.pdf ready (380K)
✓ Diff Generation (7s)

▸ Archive/Versioning
  ✓ Git commit: manuscript v126
  ✓ Git tag: manuscript-v126
  ✓ Deleted 1 old versions: v105
✓ Archive/Versioning (0s)

▸ Cleanup
✓ Cleanup (0s)

▸ Directory Tree
  ✓ ./01_manuscript/docs/tree.txt created
✓ Directory Tree (1s)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Compilation Complete
  Total time: 16s
  Output: ./01_manuscript/manuscript.pdf
  Log: ./01_manuscript/logs/global.log
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Verbose Mode (SCITEX_LOG_LEVEL=2)
Shows all process-level messages:
```
▸ PDF Generation
  → Converting ./01_manuscript/manuscript.tex to PDF...
  → Selected engine: latexmk
  → Using latexmk engine
  → Set BIBINPUTS=/home/ywatanabe/proj/scitex-writer:
  → Running: latexmk [7 options] manuscript.tex
  ⚠ Compilation completed with warnings (check citations/references)
  ✓ latexmk compilation: 3s
  → Moved PDF: ./01_manuscript/logs/manuscript.pdf -> ./01_manuscript/manuscript.pdf
  ✓ ./01_manuscript/manuscript.pdf ready (348K)
✓ PDF Generation (4s)
```

## Benefits

1. **Cleaner output** - Easier to scan and understand
2. **Consistent formatting** - All stages use same format
3. **Better visual hierarchy** - Stages, processes, and tasks clearly distinguished
4. **Flexible verbosity** - Control detail level as needed
5. **Quiet git operations** - Details in logs, summaries on screen
6. **Professional appearance** - Unicode symbols and colors

<!-- EOF -->
