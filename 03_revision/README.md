# Revision Response

This directory contains reviewer comments and author responses for manuscript revision.

## Quick Start

From the paper root directory:
```bash
# Compile revision response document
./compile_revision

# Quiet mode
./compile_revision -q

# With figures
./compile_revision -f
```

## Directory Structure

```
03_revision/
├── base.tex                  # Main revision response document
├── contents/
│   ├── editor/              # Editor comments and responses
│   │   ├── E_01_comments.tex
│   │   ├── E_01_response.tex
│   │   └── E_02_comments.tex
│   ├── reviewer1/           # Reviewer 1 comments and responses
│   │   ├── R1_01_comments.tex
│   │   ├── R1_01_response.tex
│   │   └── R1_02_comments.tex
│   ├── reviewer2/           # Reviewer 2 comments and responses
│   │   ├── R2_01_comments.tex
│   │   ├── R2_01_response.tex
│   │   └── R2_02_comments.tex
│   ├── figures/             # Revised/new figures for responses
│   ├── tables/              # Revised/new tables for responses
│   └── latex_styles/        # LaTeX formatting
├── archive/                 # Version history
├── logs/                    # Compilation logs
└── docs/                    # Documentation
```

## File Naming Convention

### Comments and Responses

Use consistent prefixes for each reviewer:
- **Editor**: `E_XX_comments.tex`, `E_XX_response.tex`
- **Reviewer 1**: `R1_XX_comments.tex`, `R1_XX_response.tex`
- **Reviewer 2**: `R2_XX_comments.tex`, `R2_XX_response.tex`

Where XX is a two-digit number (01, 02, 03, ...)

### Optional Descriptive Suffixes

For better organization, you can add descriptive suffixes:
- `E_01_comments_methodology.tex`
- `R1_02_response_statistical_analysis.tex`
- `R2_03_comments_figure_quality.tex`

The compilation script will match comments to responses based on the base ID (prefix + number).

## Adding Reviewer Comments and Responses

1. **Add reviewer comment**: Create file in appropriate directory
   ```
   contents/reviewer1/R1_03_comments.tex
   ```

2. **Add your response**: Create corresponding response file
   ```
   contents/reviewer1/R1_03_response.tex
   ```

3. **Optional revision notes**: Add revision details
   ```
   contents/reviewer1/R1_03_revision.tex
   ```

## Output Files

After successful compilation:
- `revision.pdf` - Complete revision response document
- `revision.tex` - Processed LaTeX source
- `revision_diff.pdf` - Shows changes from original manuscript

## Compilation Features

The revision compilation will:
1. Check for comment/response pairs
2. Generate diff from original manuscript (if available)
3. Include revised figures and tables
4. Create formatted response document

## Tips

- Keep comments and responses numbered sequentially
- Use descriptive suffixes for complex reviews
- Include figure/table references in responses
- The diff feature highlights changes from original manuscript

<!-- EOF -->