# Implementation Summary

Technical overview of SciTeX system architecture and implementation details.

## System Architecture

### Core Components

**Compilation System**
- Main entry point: `./compile_manuscript`
- Handles figures, tables, bibliography
- Generates PDF with change tracking
- Processes metadata from 00_shared directory

**Figure Processing**
- Automatic PNG format conversion
- Image cropping and resolution optimization
- LaTeX caption integration
- Mermaid diagram rendering

**Table Processing**
- CSV to LaTeX conversion
- Automatic formatting and styling
- Column alignment and width adjustment
- Data type detection and formatting

**Bibliography Management**
- BibTeX source: `00_shared/bibliography.bib`
- Shared across manuscript, supplementary, revision
- Automatic citation resolution
- Maintains single source of truth

### Directory Organization

```
project/
├── 01_manuscript/          # Primary manuscript
│   ├── manuscript.tex      # Main entry
│   ├── contents/           # Editable content
│   │   ├── abstract.tex
│   │   ├── introduction.tex
│   │   ├── methods.tex
│   │   ├── results.tex
│   │   ├── discussion.tex
│   │   ├── figures/
│   │   │   ├── caption_and_media/  # Source files
│   │   │   │   ├── .XX_name.png
│   │   │   │   └── .XX_name.tex
│   │   │   └── compiled/           # Generated
│   │   └── tables/
│   │       ├── caption_and_media/  # Source files
│   │       │   ├── .XX_name.csv
│   │       │   └── .XX_name.tex
│   │       └── compiled/           # Generated
│   └── scripts/            # Compilation scripts
│
├── 02_supplementary/       # Supplementary materials
│   ├── supplementary.tex
│   └── contents/
│       ├── figures/
│       ├── tables/
│       └── (same structure as main)
│
├── 03_revision/            # Revision responses
│   ├── revision.tex
│   ├── conclusion.tex
│   └── contents/
│       ├── editor/
│       │   ├── E_01_comments.tex
│       │   └── E_01_response.tex
│       ├── reviewer1/
│       │   ├── R1_01_comments.tex
│       │   ├── R1_01_response.tex
│       │   └── R1_01_revision.tex
│       └── (similar for other reviewers)
│
├── 00_shared/                 # Shared metadata
│   ├── authors.tex
│   ├── title.tex
│   ├── keywords.tex
│   ├── bibliography.bib
│   └── styling.tex
│
└── docs/                   # Documentation
    ├── 01_GUIDE_QUICK_START.md
    ├── 01_GUIDE_CONTENT_CREATION.md
    ├── G_AGENTS.md
    ├── 03_RESEARCH_TERMINOLOGY.md
    ├── 02_ARCHITECTURE.md
    ├── 04_EXTERNAL_RESOURCES.md
    └── to_claude/          # Claude Code guidelines
```

## Key Features

### Single Source of Truth

- Bibliography: All documents reference same `.bib` file
- Metadata: Authors, title, keywords centralized in `00_shared/`
- Figures/Tables: Use symlinks to maintain synchronization

### Automatic Processing

**Figures**:
1. Detect PNG, JPG, TIF, Mermaid files
2. Convert to consistent PNG format
3. Crop excess white space
4. Integrate captions from TEX files
5. Generate LaTeX environment with labels

**Tables**:
1. Parse CSV files
2. Apply formatting rules from caption comments
3. Generate LaTeX table environment
4. Integrate captions
5. Handle special formatting (landscape, font sizes, alignment)

### Change Tracking

- Compares current compilation to previous
- Generates `diff.pdf` highlighting changes
- Useful for revision processes
- Maintains version history in git

## Technical Implementation

### LaTeX Foundation

Built on standard LaTeX:
- Document class: `article` or custom variant
- Packages: graphicx, booktabs, hyperref, etc.
- TikZ for diagrams and vector graphics

### Processing Scripts

Located in `scripts/`:
- `process_figures.sh`: Figure handling
- `process_tables.sh`: Table handling
- `compile_manuscript`: Main orchestration

Written in Bash for:
- Cross-platform compatibility
- Minimal dependencies
- Easy customization
- Transparent processing steps

### File Naming Strategy

**Rationale**:
- Dot prefix (`.01_name.png`) hides files in some systems
- Sequential numbering enables automatic ordering
- Descriptive names improve discoverability
- Separate caption files (`.tex`) allow flexible content

**Processing**:
```bash
for file in .XX_*.png; do
  # Extract XX number
  num=$(echo $file | sed 's/\.\([0-9]*\)_.*/\1/')
  # Find matching caption
  caption=".${num}_*.tex"
  # Generate LaTeX environment
  # Create figure label fig:XX
done
```

### Cross-Referencing

Documents share labels through:
- Same naming convention across all documents
- Optional reverse links between manuscript and supplements
- Prefix system for supplementary (supple-fig:01)

Setup:
```latex
% In main document
\link[supple-]{../02_supplementary/supplementary}

% In supplementary
\link[main-]{../01_manuscript/manuscript}
```

## Compilation Workflow

### Step 1: Initialization
- Create output directories
- Clear previous compilation artifacts
- Setup temporary files

### Step 2: Asset Processing
- Process all figures (convert, crop, scale)
- Process all tables (parse CSV, format)
- Generate LaTeX code for each

### Step 3: Content Compilation
- Read content files (abstract, introduction, etc.)
- Insert processed figures and tables
- Resolve citations from bibliography

### Step 4: PDF Generation
- Run LaTeX compiler (pdflatex or xelatex)
- Resolve references and cross-references
- Generate PDF output

### Step 5: Diff Generation
- Compare with previous manuscript PDF
- Generate annotated diff showing changes
- Create summary of modifications

## Customization Points

### LaTeX Preamble
Edit `styles/` to customize:
- Document class options
- Color schemes
- Font selections
- Page margins and layout

### Processing Behavior
Modify script behavior:
- Figure conversion parameters
- Table formatting defaults
- Caption positioning
- Label naming scheme

### Metadata
Centralized in `00_shared/`:
- Authors and affiliations
- Title and subtitle
- Keywords
- Running headers/footers

## Performance Considerations

### Compilation Time

Typical times:
- First pass: 30-60 seconds
- With figures: +30-90 seconds
- With change tracking: +10-20 seconds

Optimization:
- LaTeX is sequential (unavoidable)
- Figure processing is parallelizable
- Consider splitting large documents

### File Sizes

Typical outputs:
- Manuscript PDF: 2-5 MB
- With embedded figures: 5-20 MB
- Diff PDF: 1-3 MB

Best practices:
- Compress images before linking
- Use PDF or EPS for vector graphics
- Consider external supplementary for large media

## Extension and Development

### Adding New Features

To add figure format support:
1. Add format handler in `process_figures.sh`
2. Define conversion command
3. Update documentation
4. Test with example

To add table formatting option:
1. Add pattern match in `process_tables.sh`
2. Implement LaTeX generation
3. Document in `01_GUIDE_CONTENT_CREATION.md`
4. Test with examples

### Integration with External Tools

Currently supports:
- PowerPoint to PNG conversion
- Mermaid diagram rendering
- BibTeX bibliography processing
- Standard image formats

Could extend with:
- Python script outputs
- R/ggplot2 integration
- Data visualization tools
- Citation managers (Zotero, Mendeley)

## Troubleshooting Guide

### Common Issues

**PDF not generating**:
1. Check LaTeX installation
2. Review console output for errors
3. Verify all file paths are correct
4. Check for special characters in filenames

**Figures missing from output**:
1. Verify files exist with correct naming
2. Check both PNG and TEX files present
3. Review file permissions
4. Check image format and encoding

**Bibliography not working**:
1. Verify `.bib` file syntax
2. Check all `\cite{}` commands have matching entries
3. Run bibtex manually: `bibtex manuscript`
4. Recompile manuscript

**Diff PDF empty**:
1. Ensure previous PDF exists
2. Verify diff tool installation
3. Check sufficient disk space
4. Try manual diff: `pdfdiff old.pdf new.pdf`

## Version History

SciTeX maintains backward compatibility with:
- LaTeX 2e (standard)
- Modern LaTeX distributions (TeX Live 2020+, MiKTeX)
- Python 3.8+ (for optional features)

See version changelog in main repository.
