# Bibliography Files

This directory contains your bibliography files for the manuscript.

## Single File (Default)

**Current setup:**
```
00_shared/bib_files/
└── bibliography.bib    # All references here
```

Edit `bibliography.bib` directly.

## Multiple Files

**Organize references by topic:**
```
00_shared/bib_files/
├── bibliography.bib        # Auto-generated merged file
├── my_papers.bib          # Your publications
├── methods_refs.bib       # Methods and techniques
├── field_background.bib   # Field overview papers
└── tools_software.bib     # Software and tools
```

**To merge:**
```bash
python scripts/python/merge_bibliographies.py
```

**Deduplication:**
- By DOI (most reliable)
- By title + year
- Merges metadata from duplicates

**Auto-merge during compilation:**
The merge happens automatically during all compilation steps (manuscript, supplementary, revision).

**Hash-based caching:**
- Tracks file changes using MD5 hashes
- Skips merge if no files changed
- Cache stored in `.bibliography_cache.json`
- Use `--force` flag to rebuild: `python scripts/python/merge_bibliographies.py --force`

## Usage

**Add new reference:**
1. Add to appropriate topic file (e.g., `methods_refs.bib`)
2. Compile manuscript (auto-merges)
3. Or manually: `python scripts/python/merge_bibliographies.py`

**Single file workflow:**
- Just edit `bibliography.bib` directly
- No merging needed

## Demo Files

Three demo .bib files are included:
- `methods_refs.bib` - Methods and techniques (4 entries)
- `field_background.bib` - Field overview papers (5 entries)
- `my_papers.bib` - Your own publications (4 entries, including duplicate)

**To use demo files:**
1. Run: `./scripts/shell/compile_manuscript.sh`
2. Result: Merges 13 entries → 12 unique (1 duplicate removed)

**To use your own references:**
1. Replace demo files with your own .bib files
2. Or delete demo files and use single `bibliography.bib`
3. Organize by topic as needed

<!-- EOF -->
