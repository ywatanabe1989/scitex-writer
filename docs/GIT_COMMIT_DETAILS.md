# Git Auto-Commit: Atomic & Staging-Safe Implementation

**Status:** ✅ IMPLEMENTED
**Date:** 2025-11-12

---

## Summary

The git auto-commit system commits **ONLY** the specific files created during compilation, using `git commit --only` to **preserve your staging area completely**.

---

## What Gets Committed

### Exactly 5-6 Files Per Compilation

For each compilation (e.g., manuscript v113), the system commits:

```
01_manuscript/archive/manuscript_v113.pdf         # Compiled PDF
01_manuscript/archive/manuscript_v113.tex         # Compiled TeX
01_manuscript/archive/manuscript_v113_diff.pdf    # Diff PDF
01_manuscript/archive/manuscript_v113_diff.tex    # Diff TeX
01_manuscript/archive/.version_counter.txt        # Version counter
01_manuscript/archive/.cleanup_history.txt        # (if cleanup ran)
```

**That's it. Nothing else.**

---

## What Does NOT Get Committed

The following are **explicitly excluded** from auto-commit:

### ❌ No Other Files

- ❌ Shell scripts (e.g., `scripts/shell/*.sh`)
- ❌ Configuration files (e.g., `config/*.conf`, `config/*.yaml`)
- ❌ Python scripts (e.g., `scripts/python/*.py`)
- ❌ Documentation (e.g., `docs/*.md`, `README.md`)
- ❌ Project VERSION file
- ❌ Bibliography files (e.g., `00_shared/bib_files/`)
- ❌ LaTeX styles (e.g., `00_shared/latex_styles/`)
- ❌ Source content (e.g., `01_manuscript/contents/`)
- ❌ Other archive versions (only the NEW version)

### ❌ No Staging Area Interference

- ❌ Does NOT stage any files
- ❌ Does NOT unstage any files
- ❌ Does NOT affect files you've already staged
- ❌ Does NOT touch the index at all

---

## How It Works: `git commit --only`

### The Critical Flag

```bash
git commit --only file1 file2 file3 -m "message"
```

This command:
1. ✅ Commits ONLY the specified files
2. ✅ Ignores the current staging area (index)
3. ✅ Preserves any files you have staged
4. ✅ Does not stage or unstage anything

### Contrast with Traditional Approach

**❌ Traditional (BAD for our use case):**
```bash
git add archive/         # Stages ALL files in archive/
git commit -m "message"  # Commits everything staged
# Problem: Affects staging area, commits too much
```

**✅ Our Approach (GOOD):**
```bash
git commit --only \
  archive/manuscript_v113.pdf \
  archive/manuscript_v113.tex \
  archive/manuscript_v113_diff.pdf \
  archive/manuscript_v113_diff.tex \
  archive/.version_counter.txt \
  -m "chore: Auto-archive manuscript v113"

# Result: Only these 5 files committed, staging area untouched
```

---

## Example Scenario

### Before Compilation

```bash
$ git status
On branch develop
Changes not staged for commit:
  modified:   scripts/shell/modules/process_figures.sh
  modified:   config/version_control.conf

$ git add config/version_control.conf

$ git status
On branch develop
Changes to be committed:
  modified:   config/version_control.conf    # ← Staged by you

Changes not staged for commit:
  modified:   scripts/shell/modules/process_figures.sh
```

### Run Compilation

```bash
$ ./scripts/shell/compile_manuscript.sh

# [compilation happens...]
# [auto-commit runs]

✅ Git commit created: manuscript v113
✅ Git tag created: manuscript-v113
```

### After Compilation

```bash
$ git status
On branch develop
Changes to be committed:
  modified:   config/version_control.conf    # ← STILL STAGED!

Changes not staged for commit:
  modified:   scripts/shell/modules/process_figures.sh

$ git log -1 --name-only
commit abc123def456 (HEAD -> develop, tag: manuscript-v113)
Author: You <you@example.com>
Date:   Wed Nov 12 11:00:00 2025

    chore: Auto-archive manuscript v113

    Auto-generated during compilation.

    Files committed (atomic):
      - 01_manuscript/archive/manuscript_v113.pdf
      - 01_manuscript/archive/manuscript_v113.tex
      - 01_manuscript/archive/manuscript_v113_diff.pdf
      - 01_manuscript/archive/manuscript_v113_diff.tex
      - 01_manuscript/archive/.version_counter.txt

01_manuscript/archive/manuscript_v113.pdf
01_manuscript/archive/manuscript_v113.tex
01_manuscript/archive/manuscript_v113_diff.pdf
01_manuscript/archive/manuscript_v113_diff.tex
01_manuscript/archive/.version_counter.txt
```

**Notice:**
- ✅ Your staged file (`config/version_control.conf`) is STILL staged
- ✅ Your unstaged file (`process_figures.sh`) is STILL unstaged
- ✅ Only the 5 archive files were committed
- ✅ Your workflow was completely unaffected

---

## Safe for Parent Repositories

This implementation is **specifically designed** for use when scitex-writer is nested inside a parent git repository:

```
parent-scitex-repo/              # Your main project repo
├── .git/                        # Parent git
├── scitex-writer/               # This project (nested)
│   ├── 01_manuscript/
│   │   └── archive/            # Auto-commits only affect these
│   ├── 02_supplementary/
│   └── scripts/                # These are NEVER auto-committed
└── other-scitex-code/          # These are NEVER touched
```

### Why This Matters

- ✅ You can develop scripts/configs in the parent repo
- ✅ Stage and commit your development work normally
- ✅ Auto-commit only affects archive files
- ✅ No conflicts, no interference

---

## Implementation Details

### File Selection Logic

From `scripts/shell/modules/git_auto_commit.sh`:

```bash
# Build exact list of files to commit (atomic)
files_to_commit=()
archive_base="${SCITEX_WRITER_VERSIONS_DIR}/${doc_type}_v${version}"

# Only add files that exist
[ -f "${archive_base}.pdf" ] && files_to_commit+=("${archive_base}.pdf")
[ -f "${archive_base}.tex" ] && files_to_commit+=("${archive_base}.tex")
[ -f "${archive_base}_diff.pdf" ] && files_to_commit+=("${archive_base}_diff.pdf")
[ -f "${archive_base}_diff.tex" ] && files_to_commit+=("${archive_base}_diff.tex")
[ -f "$version_file" ] && files_to_commit+=("$version_file")

# Only add cleanup log if recently modified (< 5 seconds)
if [ -f "$cleanup_log" ] && [ modified_recently ]; then
    files_to_commit+=("$cleanup_log")
fi
```

### Commit Execution

```bash
# Build commit command with --only flag
commit_cmd="git commit --only"
for file in "${files_to_commit[@]}"; do
    commit_cmd="$commit_cmd \"$file\""
done
commit_cmd="$commit_cmd -m \"$msg\" -m \"$commit_body\""

# Execute (does NOT touch staging area)
eval "$commit_cmd"
```

---

## Verification

### Test Scripts

Run these to verify behavior:

```bash
# Test 1: Verify atomic commit logic
./tests/scripts/test_atomic_commit.sh

# Test 2: Verify staging preservation
./tests/scripts/test_staging_preservation.sh
```

### Manual Verification

```bash
# 1. Stage a test file
git add config/version_control.conf

# 2. Check what's staged
git diff --cached --name-only
# Output: config/version_control.conf

# 3. Run compilation
./scripts/shell/compile_manuscript.sh

# 4. Check staging again
git diff --cached --name-only
# Output: config/version_control.conf  (UNCHANGED!)

# 5. Check last commit
git log -1 --name-only
# Output: Only archive files, NOT your staged files
```

---

## Configuration

### Enable/Disable

Edit `config/version_control.conf`:

```bash
# Enable git auto-commit (default: true)
GIT_AUTO_COMMIT_ENABLED=true

# Enable git tagging (default: true)
GIT_TAG_ENABLED=true
```

### Atomic Behavior (Built-in)

The atomic behavior is **always active** when auto-commit is enabled. There's no configuration needed - it's the only way the system works.

---

## Guarantees

### What We Guarantee

1. ✅ **Only 5-6 files committed** per compilation
2. ✅ **Staging area completely preserved**
3. ✅ **No interference with other files**
4. ✅ **Safe in parent repositories**
5. ✅ **Explicit file list in commit message**

### What We Don't Touch

1. ❌ Files you've staged for other commits
2. ❌ Files you've modified but not staged
3. ❌ Any files outside the archive directory
4. ❌ The git index/staging area
5. ❌ Other branches or tags

---

## Troubleshooting

### "My staged files were committed!"

This should **never** happen. If it does:

1. Check git log: `git log -1 --name-only`
2. Look for the "Files committed (atomic):" section
3. Verify it only lists archive files
4. If not, please report as a bug

### "Auto-commit didn't work"

Check:

```bash
# Is it enabled?
grep GIT_AUTO_COMMIT_ENABLED config/version_control.conf

# Are you in a git repo?
git rev-parse --git-dir

# Check logs
tail scripts/shell/modules/.git_auto_commit.sh.log
```

### "I want to disable it"

```bash
# Edit config/version_control.conf
GIT_AUTO_COMMIT_ENABLED=false

# Or for one compilation:
GIT_AUTO_COMMIT_ENABLED=false ./scripts/shell/compile_manuscript.sh
```

---

## References

- Git documentation: `git help commit` (see `--only` flag)
- Implementation: `scripts/shell/modules/git_auto_commit.sh`
- Tests: `tests/scripts/test_atomic_commit.sh`
- Configuration: `config/version_control.conf`

---

**Last Updated:** 2025-11-12
**Version:** 2.0 (Atomic + Staging-Safe)
