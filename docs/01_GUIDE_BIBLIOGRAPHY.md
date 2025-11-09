# Bibliography Management Guide

Reference management with multi-file bibliography system, deduplication, and hash-based caching.

---

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Single File Workflow](#single-file-workflow)
- [Multi-File Workflow](#multi-file-workflow)
- [Deduplication](#deduplication)
- [Hash-Based Caching](#hash-based-caching)
- [Manual Merging](#manual-merging)
- [Demo Files](#demo-files)
- [Citation Styles](#citation-styles)
- [Troubleshooting](#troubleshooting)

---

## Overview

Bibliography management system supporting:

- Single-file workflow: Single `.bib` file
- Multi-file workflow: References organized by topic
- Deduplication: Duplicate detection by DOI or title+year
- Hash-based caching: Skips merge when files unchanged
- Automatic merge: Runs during compilation
- Citation style configuration: Via YAML config files

Location: `00_shared/bib_files/`

---

## Quick Start

### Option 1: Use Demo Files

```bash
# Compile manuscript (auto-merges 3 demo files)
./scripts/shell/compile_manuscript.sh

# Expected output:
# [00:00:00] Starting: Bibliography Merge
# Merging 3 bibliography files...
#   - field_background.bib
#   - methods_refs.bib
#   - my_papers.bib
# ✓ Merged bibliography saved: 00_shared/bib_files/bibliography.bib
#   Input entries: 13
#   Unique entries: 12
#   Duplicates removed: 1
```

### Option 2: Single File

```bash
# Delete demo files
rm 00_shared/bib_files/{methods_refs,field_background,my_papers}.bib

# Edit single file
vim 00_shared/bib_files/bibliography.bib

# Compile normally
./scripts/shell/compile_manuscript.sh
```

### Option 3: Custom Multi-File Organization

```bash
cd 00_shared/bib_files/

# Create topic-based files
vim deep_learning.bib
vim neuroimaging.bib
vim my_publications.bib

# Compile (auto-merges)
cd ../..
./scripts/shell/compile_manuscript.sh
```

---

## Single File Workflow

**When to use:**
- Small projects (<50 references)
- Simple organization needs
- Quick papers or letters

**Setup:**

```bash
# Delete any multi-file organization
rm 00_shared/bib_files/*.bib
# Keep only bibliography.bib

# Edit directly
vim 00_shared/bib_files/bibliography.bib
```

**Structure:**

```
00_shared/bib_files/
└── bibliography.bib    # All references here
```

**No merging needed** - compilation uses `bibliography.bib` directly.

---

## Multi-File Workflow

**When to use:**
- Large projects (50+ references)
- Collaborative writing
- Topic-based organization
- Reusing reference sets across projects

**Recommended Organization:**

```
00_shared/bib_files/
├── bibliography.bib              # Auto-generated (DO NOT EDIT)
├── .bibliography_cache.json      # Cache (auto-managed)
├── methods_refs.bib              # Methods and techniques
├── field_background.bib          # Field overview papers
├── my_papers.bib                 # Your publications
├── deep_learning.bib             # Deep learning references
└── neuroimaging.bib              # Neuroimaging studies
```

**Workflow:**

1. **Add references** to appropriate topic file:
   ```bash
   vim 00_shared/bib_files/methods_refs.bib
   ```

2. **Compile** (automatic merge):
   ```bash
   ./scripts/shell/compile_manuscript.sh
   ```

3. **Check merged output**:
   ```bash
   cat 00_shared/bib_files/bibliography.bib
   ```

**Important:**
- **DO NOT** manually edit `bibliography.bib` (it's auto-generated)
- Edit only the source `.bib` files
- `bibliography.bib` is regenerated on each compilation

---

## Deduplication

Merge system removes duplicate entries using two-tier strategy:

### Deduplication Strategy

**1. By DOI** (most reliable):
```bibtex
@article{Smith2020_A,
  doi = {10.1038/s41598-020-12345-6},
  author = {Smith, J. and Doe, J.},
  title = {Neural Processing},
  year = {2020}
}

@article{Smith2020_B,
  doi = {10.1038/s41598-020-12345-6},  # Same DOI
  author = {Smith, John and Doe, Jane},
  title = {Neural Processing Methods},  # Different title
  year = {2020}
}
# → Merged into single entry with combined metadata
```

**2. By Title + Year** (fallback):
```bibtex
@article{Chen2021_A,
  author = {Chen, W.},
  title = {Machine Learning for Neural Data},
  year = {2021}
}

@article{Chen2021_B,
  author = {Chen, Wei and Zhang, L.},
  title = {Machine Learning for Neural Data},  # Same normalized title
  year = {2021}                                # Same year
}
# → Merged (no DOI available, using title+year)
```

### Metadata Merging

When duplicates are found, metadata is merged:

```bibtex
# Entry 1 (less complete)
@article{Smith2020,
  author = {Smith, J.},
  title = {Neural Processing},
  year = {2020}
}

# Entry 2 (more complete)
@article{Smith2020_dup,
  author = {Smith, John and Doe, Jane},
  title = {Neural Processing},
  journal = {Nature},
  year = {2020},
  doi = {10.1038/nature12345},
  abstract = {Full abstract here...}
}

# Merged result (best of both)
@article{Smith2020,
  author = {Smith, John and Doe, Jane},  # Longer version preferred
  title = {Neural Processing},
  journal = {Nature},
  year = {2020},
  doi = {10.1038/nature12345},
  abstract = {Full abstract here...}
}
```

**Rules:**
- Prefers entries with more fields
- Prefers longer/more detailed field values
- Keeps all unique information
- First entry's citation key is used

---

## Hash-Based Caching

The system uses MD5 hashing to detect changes and skip unnecessary merges.

### How It Works

1. **First compilation**:
   ```bash
   ./scripts/shell/compile_manuscript.sh
   # Merges files, creates cache
   ```

2. **Subsequent compilations** (no changes):
   ```bash
   ./scripts/shell/compile_manuscript.sh
   # ✓ Bibliography cache valid (no changes detected)
   # Merge skipped
   ```

3. **After editing** a `.bib` file:
   ```bash
   vim 00_shared/bib_files/methods_refs.bib
   ./scripts/shell/compile_manuscript.sh
   # Cache invalid, rebuilding...
   # Merging 3 bibliography files...
   ```

### Cache File

**Location**: `00_shared/bib_files/.bibliography_cache.json`

**Contents:**
```json
{
  "input_hash": "6f91cc7eab63a633f61ec01f9a2f7477",
  "input_files": [
    "field_background.bib",
    "methods_refs.bib",
    "my_papers.bib"
  ],
  "output_file": "bibliography.bib",
  "stats": {
    "total_input": 13,
    "unique_output": 12,
    "duplicates_found": 1,
    "duplicates_merged": 1
  }
}
```

**Notes:**
- Automatically managed (don't edit)
- Git-ignored by default
- Safe to delete (will rebuild on next compile)

### Performance

**Without caching:**
```
Bibliography Merge: ~2-5s (depends on file size)
```

**With valid cache:**
```
Bibliography Merge: <0.1s
```

**Speedup**: 20-50x faster when files unchanged

---

## Manual Merging

### Basic Usage

```bash
# From project root
python3 scripts/python/merge_bibliographies.py

# Output:
# Merging 3 bibliography files...
#   - field_background.bib
#   - methods_refs.bib
#   - my_papers.bib
# ✓ Merged bibliography saved: 00_shared/bib_files/bibliography.bib
#   Input entries: 13
#   Unique entries: 12
#   Duplicates removed: 1
```

### Command-Line Options

```bash
# Force rebuild (ignore cache)
python3 scripts/python/merge_bibliographies.py --force

# Quiet mode (no output)
python3 scripts/python/merge_bibliographies.py --quiet

# Custom directory
python3 scripts/python/merge_bibliographies.py /path/to/bib_files/

# Custom output filename
python3 scripts/python/merge_bibliographies.py -o merged.bib

# Help
python3 scripts/python/merge_bibliographies.py --help
```

### When to Use Manual Merge

- Testing deduplication
- Checking merge results before compilation
- Rebuilding after major reorganization
- Debugging bibliography issues

---

## Demo Files

Three demo files are included to demonstrate the system:

### `methods_refs.bib` (4 entries)
Methods and techniques references:
- Neural signal processing
- Spectral analysis
- Machine learning
- Deep learning

### `field_background.bib` (5 entries)
Field overview papers:
- Computational neuroscience review
- Brain networks
- Cognitive neuroscience
- Systems neuroscience
- Neuroscience textbook

### `my_papers.bib` (4 entries)
Your own publications (with intentional duplicate):
- Novel method (2023) - appears twice with different details
- Previous work (2022)
- Conference paper (2021)

### Testing with Demos

```bash
# See deduplication in action
python3 scripts/python/merge_bibliographies.py

# Expected:
# Input entries: 13
# Unique entries: 12
# Duplicates removed: 1
# (The duplicate in my_papers.bib is detected and merged)
```

### Replacing Demo Files

**Option 1: Delete and start fresh**
```bash
cd 00_shared/bib_files/
rm methods_refs.bib field_background.bib my_papers.bib bibliography.bib
# Create your own organization
```

**Option 2: Modify demo files**
```bash
# Replace demo entries with your references
vim 00_shared/bib_files/methods_refs.bib
vim 00_shared/bib_files/field_background.bib
vim 00_shared/bib_files/my_papers.bib
```

---

## Citation Styles

Citation style is configured in `config/manuscript.yaml` (or supplementary/revision configs).

### Changing Style

**Edit config:**
```yaml
# config/manuscript.yaml
citation_style: "unsrtnat"  # Order of appearance (default)
# citation_style: "plainnat"   # Alphabetical
# citation_style: "abbrvnat"   # Abbreviated
# citation_style: "apalike"    # APA-like
```

**Compile:**
```bash
./scripts/shell/compile_manuscript.sh
```

The citation style is automatically applied to `00_shared/latex_styles/bibliography.tex`.

### Available Styles

**Numbered (Order of Appearance):**
- `unsrtnat` - [1], [2], [3]... (default)
- `ieeetr` - IEEE style

**Numbered (Alphabetical):**
- `plainnat` - [1], [2], [3]... sorted by author
- `abbrvnat` - Abbreviated names

**Author-Year:**
- `plainnat` - (Smith, 2020)
- `apalike` - APA-like style
- `chicago` - Chicago style

**Journal-Specific:**
- `elsarticle-num` - Elsevier numbered
- `naturemag` - Nature style
- `IEEEtran` - IEEE Transactions

See `00_shared/latex_styles/bibliography.tex` for full list and details.

---

## Troubleshooting

### Problem: Merge Not Running

**Symptom:**
```
No .bib files found in 00_shared/bib_files
```

**Solution:**
```bash
# Check files exist
ls 00_shared/bib_files/*.bib

# Ensure not all named bibliography.bib
ls 00_shared/bib_files/ | grep -v bibliography.bib
```

---

### Problem: Duplicates Not Removed

**Symptom:**
Duplicate entries appear in final PDF bibliography.

**Diagnosis:**
```bash
# Run merge manually to see details
python3 scripts/python/merge_bibliographies.py

# Check if duplicates have same DOI
grep "doi = " 00_shared/bib_files/*.bib | grep "YOUR_DOI"

# Or same title+year
grep "title = " 00_shared/bib_files/*.bib | grep "YOUR_TITLE"
```

**Solution:**
Ensure duplicates have either:
- Same DOI (most reliable)
- Same title (case-insensitive, normalized) AND same year

---

### Problem: Cache Not Invalidating

**Symptom:**
Changes to `.bib` files not reflected after compilation.

**Solution:**
```bash
# Delete cache manually
rm 00_shared/bib_files/.bibliography_cache.json

# Or force rebuild
python3 scripts/python/merge_bibliographies.py --force

# Then compile
./scripts/shell/compile_manuscript.sh
```

---

### Problem: Merge Script Not Found

**Symptom:**
```
ERROR: scripts/python/merge_bibliographies.py not found
```

**Solution:**
```bash
# Check script exists
ls -la scripts/python/merge_bibliographies.py

# Check permissions
chmod +x scripts/python/merge_bibliographies.py

# Check Python is available
which python3
```

---

### Problem: bibtexparser Not Installed

**Symptom:**
```
ERROR: bibtexparser not installed
```

**Solution:**
```bash
# Install package
pip install bibtexparser

# Or with Python 3
python3 -m pip install bibtexparser
```

---

### Problem: Citations Appear as [?]

**Symptom:**
PDF shows [?] instead of citation numbers.

**Causes:**
- Bibliography file missing entries
- BibTeX compilation failed
- Citation keys don't match

**Solution:**
```bash
# Check merged bibliography contains your keys
grep "@article{YOUR_KEY" 00_shared/bib_files/bibliography.bib

# Run full compilation (3 passes)
./scripts/shell/compile_manuscript.sh

# Check BibTeX log
cat 01_manuscript/archive/manuscript.blg
```

---

### Problem: Metadata Lost During Merge

**Symptom:**
Merged entry missing some fields.

**Explanation:**
Merge prefers longer/more complete fields. Short fields are replaced by longer ones.

**Solution:**
Ensure the most complete entry has the longest field values:

```bibtex
# BAD: Complete entry has short fields
@article{key1,
  author = {Smith, J.},           # Short
  title = {Title},                # Short
  doi = {10.1038/nature12345}
}

# GOOD: Complete entry has long fields
@article{key1,
  author = {Smith, John and Doe, Jane},  # Long - will be kept
  title = {Full Title of Paper},         # Long - will be kept
  journal = {Nature},
  year = {2020},
  doi = {10.1038/nature12345}
}
```

---

## Best Practices

### File Organization

✅ **Good:**
```
00_shared/bib_files/
├── methods_signal_processing.bib
├── methods_machine_learning.bib
├── field_neuroscience.bib
├── field_deep_learning.bib
└── our_publications.bib
```

❌ **Avoid:**
```
00_shared/bib_files/
├── refs1.bib
├── refs2.bib
└── misc.bib
```

### Citation Keys

✅ **Good (descriptive, unique):**
```bibtex
@article{Smith2020_NeuralProcessing,
@article{Chen2021_MachineLearning,
@article{YourName2023_NovelMethod,
```

❌ **Avoid (generic):**
```bibtex
@article{paper1,
@article{ref2,
@article{article3,
```

### Adding References

✅ **Workflow:**
1. Determine topic (methods, background, etc.)
2. Add to appropriate file
3. Compile (auto-merges)
4. Cite in manuscript: `\cite{Smith2020_NeuralProcessing}`

❌ **Don't:**
- Edit `bibliography.bib` directly (it's auto-generated)
- Add duplicates without checking
- Use inconsistent citation key formats

### Version Control

**Git ignore:**
```bash
# .gitignore should include
00_shared/bib_files/.bibliography_cache.json
```

**Commit:**
```bash
# Commit source files
git add 00_shared/bib_files/*.bib
git commit -m "Add new references for deep learning section"

# Do NOT commit
git add 00_shared/bib_files/bibliography.bib  # Auto-generated
```

---

## Summary

| Feature | Description | Benefit |
|---------|-------------|---------|
| Multi-file | Organize by topic | Better organization |
| Deduplication | By DOI or title+year | No duplicate citations |
| Auto-merge | During compilation | No manual steps |
| Caching | Hash-based change detection | 20-50x performance |
| Manual merge | `merge_bibliographies.py` | Testing & debugging |

**Key Files:**
- `00_shared/bib_files/*.bib` - Source files (edit these)
- `00_shared/bib_files/bibliography.bib` - Merged output (auto-generated)
- `00_shared/bib_files/.bibliography_cache.json` - Cache (auto-managed)
- `scripts/python/merge_bibliographies.py` - Merge script

**Key Commands:**
```bash
# Compile (auto-merge)
./scripts/shell/compile_manuscript.sh

# Manual merge
python3 scripts/python/merge_bibliographies.py

# Force rebuild
python3 scripts/python/merge_bibliographies.py --force
```

---

For more information, see:
- `00_shared/bib_files/README.md` - Quick reference
- `00_shared/latex_styles/bibliography.tex` - Citation style details
- `scripts/python/merge_bibliographies.py` - Implementation

<!-- EOF -->
