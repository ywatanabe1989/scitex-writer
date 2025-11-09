# Bibliography Files

This directory contains your bibliography files for the manuscript.

## Single File (Default)

**Current setup:**
```
00_shared/bib_files/
└── bibliography.bib    # All references here
```

Edit `bibliography.bib` directly.

## Multiple Files (Optional - Organized by Topic)

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
# Creates bibliography.bib with smart deduplication
```

**Smart deduplication:**
- By DOI (most reliable)
- By title + year
- Merges metadata from duplicates

**Auto-merge during compilation:**
The merge happens automatically if multiple .bib files exist.

## Usage

**Add new reference:**
1. Add to appropriate topic file (e.g., `methods_refs.bib`)
2. Compile manuscript (auto-merges)
3. Or manually: `python scripts/python/merge_bibliographies.py`

**Single file workflow:**
- Just edit `bibliography.bib` directly
- No merging needed

<!-- EOF -->
