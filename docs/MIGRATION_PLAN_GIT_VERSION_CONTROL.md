# Migration Plan: Git-Based Version Control with Archive Cleanup

**Version:** 1.0
**Date:** 2025-11-12
**Status:** PROPOSAL

---

## Executive Summary

This plan outlines the migration from a pure archive-based versioning system to a hybrid approach:
- **Primary**: Git auto-commit with semantic versioning tags
- **Secondary**: Archive system retaining only last N versions (configurable, default: 20)
- **Fallback**: Archive system continues if git operations fail

### Key Benefits
- ✅ Full version history in git (no disk space growth)
- ✅ Automatic commits with meaningful metadata (who, when, why)
- ✅ Quick access to recent N versions as PDFs in archive/
- ✅ Reduced disk usage (e.g., 500MB → ~50MB for archives)
- ✅ Backward compatible (existing workflows unchanged)
- ✅ Git tags enable semantic versioning (v2.1.0, v2.1.1, etc.)

---

## Current State Analysis

### Archive System (From Exploration)
```
Current: 79 total versions, ~550 MB
├─ manuscript/archive/      72 versions (~500 MB)
├─ supplementary/archive/    6 versions (~50 MB)
└─ revision/archive/         1 version (~2 MB)

Growth: ~7 MB per manuscript version
Capacity: ~10 GB total before cleanup needed
```

### Version Scheme
- **Project version**: v2.0.0-rc2 (in `/VERSION`)
- **Document versions**: v000-v112 (3-digit sequential)
- **No git integration**: Archives tracked but not auto-committed

### Compilation Workflow
```
Stage 1-8:  Compilation & Diff Generation
Stage 9:    Archive Creation ← ENHANCEMENT POINT
Stage 10-11: Cleanup & Reporting
```

---

## Proposed Architecture

### Two-Tier System

```
┌─────────────────────────────────────────────────────────┐
│  TIER 1: Git Version Control (Primary, Long-term)      │
├─────────────────────────────────────────────────────────┤
│  • Auto-commit after each successful compilation        │
│  • Tagged with version (e.g., manuscript-v113)          │
│  • Commit message includes metadata                     │
│  • All files tracked: .tex, .pdf, .bib, etc.           │
│  • Full history: unlimited, searchable, branching       │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│  TIER 2: Archive System (Secondary, Recent Cache)      │
├─────────────────────────────────────────────────────────┤
│  • Keep only last N versions (default: 20)              │
│  • Auto-cleanup: delete older versions                  │
│  • Quick PDF access without git checkout               │
│  • Symlinks to latest: .manuscript.pdf, etc.           │
│  • Fallback if git fails                                │
└─────────────────────────────────────────────────────────┘
```

### Configuration

New file: `config/version_control.conf`

```bash
# Git Auto-Commit Settings
GIT_AUTO_COMMIT_ENABLED=true
GIT_COMMIT_MESSAGE_TEMPLATE="chore: Auto-archive %DOC_TYPE% %VERSION%"
GIT_TAG_ENABLED=true
GIT_TAG_PREFIX="%DOC_TYPE%-"  # e.g., manuscript-v113
GIT_PUSH_ENABLED=false  # Safety: manual push by default

# Archive Cleanup Settings
ARCHIVE_KEEP_LAST_N=20
ARCHIVE_CLEANUP_ENABLED=true
ARCHIVE_MIN_KEEP=5  # Safety: never delete if < 5 versions

# Fallback Settings
FAIL_ON_GIT_ERROR=false  # Continue if git fails
LOG_GIT_OPERATIONS=true
```

---

## Implementation Plan

### Phase 1: Git Auto-Commit Module (Week 1)

**New File:** `scripts/shell/modules/git_auto_commit.sh`

```bash
#!/bin/bash
# Git Auto-Commit Module for SciTeX Writer

git_auto_commit() {
    local doc_type="$1"      # manuscript, supplementary, revision
    local version="$2"       # e.g., v113
    local pdf_path="$3"
    local tex_path="$4"

    # Check if enabled
    [[ "$GIT_AUTO_COMMIT_ENABLED" != "true" ]] && return 0

    # Verify git repo
    if ! git rev-parse --git-dir &>/dev/null; then
        log_warning "Not a git repository, skipping auto-commit"
        return 1
    fi

    # Stage files
    git add "$pdf_path" "$tex_path" "${pdf_path/_diff/}" "${tex_path/_diff/}"
    git add "$VERSION" "${doc_type}/archive/.version_counter.txt"

    # Create commit message
    local msg="${GIT_COMMIT_MESSAGE_TEMPLATE//%DOC_TYPE%/$doc_type}"
    msg="${msg//%VERSION%/$version}"
    msg="$msg

Auto-generated during compilation.

Changes:
- Updated ${doc_type} to ${version}
- Compiled: $(date '+%Y-%m-%d %H:%M:%S')
- User: $(git config user.name)
"

    # Commit
    if git commit -m "$msg" &>>"$LOG_FILE"; then
        log_success "Git auto-commit: ${doc_type} ${version}"

        # Create tag if enabled
        if [[ "$GIT_TAG_ENABLED" == "true" ]]; then
            local tag="${GIT_TAG_PREFIX//%DOC_TYPE%/$doc_type}${version}"
            git tag -a "$tag" -m "Auto-tag: ${doc_type} ${version}" &>>"$LOG_FILE"
            log_success "Git tag created: $tag"
        fi

        return 0
    else
        log_error "Git commit failed"
        return 1
    fi
}

export -f git_auto_commit
```

**Integration Point:** `scripts/shell/modules/archive_management.sh:archive_version()`

```bash
# After successful archiving (line ~150)
archive_version() {
    # ... existing code ...

    # Archive succeeded, now commit to git
    if [[ "$GIT_AUTO_COMMIT_ENABLED" == "true" ]]; then
        source "${MODULES_DIR}/git_auto_commit.sh"
        git_auto_commit "$DOC_TYPE" "$ARCHIVE_VERSION" \
            "$ARCHIVE_PDF_PATH" "$ARCHIVE_TEX_PATH" \
            || log_warning "Git auto-commit failed, but archive succeeded"
    fi
}
```

**Estimated Effort:** 8 hours (coding + testing)

---

### Phase 2: Archive Cleanup Module (Week 2)

**New File:** `scripts/shell/modules/archive_cleanup.sh`

```bash
#!/bin/bash
# Archive Cleanup Module: Keep only last N versions

cleanup_old_archives() {
    local doc_type="$1"
    local keep_last_n="${ARCHIVE_KEEP_LAST_N:-20}"
    local min_keep="${ARCHIVE_MIN_KEEP:-5}"

    # Safety check
    [[ "$ARCHIVE_CLEANUP_ENABLED" != "true" ]] && return 0

    local archive_dir="${PROJECT_ROOT}/${doc_type}/archive"
    [[ ! -d "$archive_dir" ]] && return 0

    # Count versions
    local total_versions=$(find "$archive_dir" -name "${doc_type}_v*.pdf" \
        | wc -l)

    # Safety: never delete if too few versions
    if [[ $total_versions -le $min_keep ]]; then
        log_info "Only $total_versions versions, skipping cleanup"
        return 0
    fi

    # Calculate how many to delete
    local to_delete=$((total_versions - keep_last_n))
    [[ $to_delete -le 0 ]] && return 0

    log_info "Cleaning up $to_delete old versions (keeping last $keep_last_n)"

    # Get sorted list of versions to delete (oldest first)
    local versions_to_delete=$(find "$archive_dir" \
        -name "${doc_type}_v*.pdf" -printf '%T@ %p\n' \
        | sort -n \
        | head -n "$to_delete" \
        | cut -d' ' -f2- \
        | sed 's/_diff.pdf$//' \
        | sed 's/.pdf$//' \
        | sort -u)

    # Delete old versions
    local deleted_count=0
    while IFS= read -r version_base; do
        rm -f "${version_base}.pdf" \
              "${version_base}.tex" \
              "${version_base}_diff.pdf" \
              "${version_base}_diff.tex" 2>/dev/null

        [[ $? -eq 0 ]] && ((deleted_count++))
    done <<< "$versions_to_delete"

    log_success "Deleted $deleted_count old archive versions"

    # Update counter file
    local new_min_version=$((total_versions - keep_last_n + 1))
    echo "# Archive cleanup: versions before v$(printf '%03d' $new_min_version) deleted" \
        >> "${archive_dir}/.version_counter.txt"
}

export -f cleanup_old_archives
```

**Integration Point:** `scripts/shell/modules/archive_management.sh:archive_version()`

```bash
# After git auto-commit (line ~160)
archive_version() {
    # ... existing code ...
    # ... git auto-commit ...

    # Cleanup old archives
    if [[ "$ARCHIVE_CLEANUP_ENABLED" == "true" ]]; then
        source "${MODULES_DIR}/archive_cleanup.sh"
        cleanup_old_archives "$DOC_TYPE"
    fi
}
```

**Estimated Effort:** 6 hours (coding + testing)

---

### Phase 3: Configuration & Migration (Week 3)

**Tasks:**

1. **Create config file** (`config/version_control.conf`)
   - Default settings for git and archive
   - Documentation comments
   - Environment-specific overrides

2. **Update main compilation scripts**
   - Source new config file
   - Load git and cleanup modules
   - Add command-line flags: `--no-git-commit`, `--keep-all-archives`

3. **Migration script** (`scripts/shell/migrate_to_git_version_control.sh`)
   ```bash
   #!/bin/bash
   # One-time migration script

   # 1. Commit all existing archives to git
   # 2. Create historical tags for major versions
   # 3. Clean up old archives (keep last 20)
   # 4. Update VERSION file
   # 5. Enable git auto-commit in config
   ```

4. **Documentation updates**
   - Update `docs/01_GUIDE_AGENTS.md`
   - Create `docs/GIT_VERSION_CONTROL.md`
   - Update README.md

**Estimated Effort:** 10 hours

---

### Phase 4: Testing & Rollout (Week 4)

**Test Cases:**

```bash
# Test 1: Normal compilation with git auto-commit
./scripts/shell/compile_manuscript.sh
# Expected: Archive created, git commit, tag created, old archives deleted

# Test 2: Git disabled
GIT_AUTO_COMMIT_ENABLED=false ./scripts/shell/compile_manuscript.sh
# Expected: Archive created, no git operations

# Test 3: Archive cleanup disabled
ARCHIVE_CLEANUP_ENABLED=false ./scripts/shell/compile_manuscript.sh
# Expected: All archives kept

# Test 4: Not a git repo
cd /tmp && cp -r project . && cd project
./scripts/shell/compile_manuscript.sh
# Expected: Graceful fallback, archive still created

# Test 5: Git failure (no user.name)
git config --unset user.name
./scripts/shell/compile_manuscript.sh
# Expected: Warning logged, archive still created

# Test 6: Multiple document types
./scripts/shell/compile_manuscript.sh
./scripts/shell/compile_supplementary.sh
./scripts/shell/compile_revision.sh
# Expected: Separate commits, tags, and cleanup for each
```

**Rollout:**
1. Deploy to development branch
2. Test with 10 compilations
3. Verify git history and tags
4. Verify archive cleanup
5. Merge to main
6. Update user documentation

**Estimated Effort:** 8 hours

---

## Disk Space Savings

### Before Migration
```
manuscript/archive/: 72 versions × 7 MB = ~500 MB
Total: ~550 MB
```

### After Migration (Keep Last 20)
```
manuscript/archive/: 20 versions × 7 MB = ~140 MB
Total: ~150 MB

Savings: 400 MB (73% reduction)
```

### Git Repository Size
```
.git/: ~100 MB (compressed, all history)
Working tree: ~50 MB (current version)
Total git overhead: ~150 MB

Net savings: 250 MB (45% reduction)
```

---

## Rollback Plan

If issues arise:

1. **Disable git auto-commit**
   ```bash
   # In config/version_control.conf
   GIT_AUTO_COMMIT_ENABLED=false
   ```

2. **Disable archive cleanup**
   ```bash
   ARCHIVE_CLEANUP_ENABLED=false
   ```

3. **Restore deleted archives from git**
   ```bash
   git log --all --pretty=format: --name-only --diff-filter=D \
       | grep "archive/" | sort -u > deleted_files.txt

   while read file; do
       git checkout $(git rev-list -n 1 HEAD -- "$file")^ -- "$file"
   done < deleted_files.txt
   ```

4. **Remove unwanted commits**
   ```bash
   # Reset to before migration
   git reset --soft <commit-before-migration>
   ```

---

## Migration Checklist

### Pre-Migration
- [ ] Backup entire repository
- [ ] Verify git config (user.name, user.email)
- [ ] Document current archive state (version counts, sizes)
- [ ] Test compilation on clean checkout
- [ ] Review and approve this plan

### Migration
- [ ] Create `config/version_control.conf`
- [ ] Implement `git_auto_commit.sh` module
- [ ] Implement `archive_cleanup.sh` module
- [ ] Update `archive_management.sh` integration
- [ ] Update compilation scripts to source config
- [ ] Run migration script
- [ ] Verify git history and tags

### Post-Migration
- [ ] Test all compilation modes (manuscript, supplementary, revision)
- [ ] Verify archive cleanup (only last 20 kept)
- [ ] Verify git auto-commit and tagging
- [ ] Update documentation
- [ ] Train users on new workflow
- [ ] Monitor for 1 week

### Success Criteria
- ✅ Archives auto-committed to git with tags
- ✅ Only last 20 versions kept in archive/
- ✅ Disk usage reduced by >40%
- ✅ No compilation failures
- ✅ Graceful fallback if git unavailable
- ✅ Full history accessible via `git log`

---

## Timeline

| Week | Phase | Deliverables | Hours |
|------|-------|--------------|-------|
| 1 | Git Auto-Commit | `git_auto_commit.sh`, integration | 8 |
| 2 | Archive Cleanup | `archive_cleanup.sh`, integration | 6 |
| 3 | Config & Migration | Config file, migration script, docs | 10 |
| 4 | Testing & Rollout | Test suite, deployment | 8 |
| **Total** | | | **32 hours** |

---

## Future Enhancements

### Phase 5 (Optional)
1. **Semantic versioning integration**
   - Parse `VERSION` file (v2.0.0-rc2)
   - Auto-increment patch version on commit
   - Major/minor bumps via CLI flags

2. **Git push automation**
   - Optional auto-push to remote
   - Configurable branch (default: develop)
   - Safety: require clean working tree

3. **Archive restoration command**
   ```bash
   ./scripts/shell/restore_archive.sh manuscript v087
   # Checkout old version from git to archive/
   ```

4. **Web-based archive browser**
   - View all versions with thumbnails
   - Diff visualization
   - Download any version

---

## Conclusion

This migration plan provides:
- **Reliability**: Git as single source of truth
- **Efficiency**: 45% disk space savings
- **Usability**: Quick access to recent PDFs
- **Safety**: Fallback and rollback mechanisms
- **Compatibility**: Existing workflows unchanged

**Recommendation**: Proceed with implementation starting Week 1.

---

**Document Status:** READY FOR REVIEW
**Next Steps:** User approval → Phase 1 implementation

