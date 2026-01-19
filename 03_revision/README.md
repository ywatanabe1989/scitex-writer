# Revision Response

This directory contains reviewer comments and author responses for manuscript revision.

## Usage

From project root:
```bash
# Compile revision response
./scripts/shell/compile_revision.sh

# Quiet mode
./scripts/shell/compile_revision.sh --quiet

# Draft mode
./scripts/shell/compile_revision.sh --draft
```

## Directory Structure

```
03_revision/
├── base.tex                  # Main revision response document
├── contents/
│   ├── editor/              # Editor comments and responses
│   │   ├── E_01_comments.tex   # ─┐
│   │   ├── E_01_response.tex   # ─┼─ TRIPLET for editor comment #1
│   │   ├── E_01_revision.tex   # ─┘
│   │   ├── E_02_comments.tex   # ─┐
│   │   ├── E_02_response.tex   # ─┼─ TRIPLET for editor comment #2
│   │   └── E_02_revision.tex   # ─┘
│   ├── reviewer1/           # Reviewer 1 comments and responses
│   │   ├── R1_01_comments.tex  # ─┐
│   │   ├── R1_01_response.tex  # ─┼─ TRIPLET for reviewer 1 comment #1
│   │   ├── R1_01_revision.tex  # ─┘
│   │   ├── R1_02_comments.tex  # ─┐
│   │   ├── R1_02_response.tex  # ─┼─ TRIPLET for reviewer 1 comment #2
│   │   └── R1_02_revision.tex  # ─┘
│   ├── reviewer2/           # Reviewer 2 (same triplet pattern)
│   │   └── ...
│   ├── figures/             # Revised/new figures for responses
│   │   └── caption_and_media/
│   ├── tables/              # Revised/new tables for responses
│   │   └── caption_and_media/
│   └── latex_styles/        # LaTeX formatting
├── archive/                 # Version history
├── logs/                    # Compilation logs
└── docs/                    # Documentation
```

## File Naming Convention

### Comments and Responses

Use consistent prefixes for each reviewer:
- **Editor**: `E_XX_comments.tex`, `E_XX_response.tex`, `E_XX_revision.tex`
- **Reviewer 1**: `R1_XX_comments.tex`, `R1_XX_response.tex`, `R1_XX_revision.tex`
- **Reviewer 2**: `R2_XX_comments.tex`, `R2_XX_response.tex`, `R2_XX_revision.tex`

Where XX is a two-digit number (01, 02, 03, ...)

**IMPORTANT**: Use the SAME number (XX) for one reviewer comment paragraph!

### File Purposes

- `*_comments.tex` : Copied paragraph from reviewer's email (verbatim quote)
- `*_response.tex` : Your response/explanation to the reviewer's comment
- `*_revision.tex` : Actual text revision made in manuscript (shown with diff)

### Example for One Comment

```
R1_01_comments.tex  -> "The methodology section lacks detail on..."
R1_01_response.tex  -> "Thank you for this suggestion. We have expanded..."
R1_01_revision.tex  -> "We added the following text to Methods section: ..."
```

### Optional Descriptive Suffixes

For better organization, you can add descriptive suffixes:
- `E_01_comments_methodology.tex`
- `R1_02_response_statistical_analysis.tex`
- `R2_03_comments_figure_quality.tex`

The compilation script will match comments to responses based on the base ID (prefix + number).

## Adding Reviewer Comments and Responses (TRIPLET)

For each reviewer comment, create a TRIPLET of files with the same number:

1. **Copy reviewer comment** (verbatim from email):
   ```
   contents/reviewer1/R1_03_comments.tex
   ```

2. **Write your response** (explanation to reviewer):
   ```
   contents/reviewer1/R1_03_response.tex
   ```

3. **Show manuscript revision** (actual changes with diff):
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