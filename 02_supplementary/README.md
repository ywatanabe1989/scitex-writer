# Supplementary Materials

This directory contains supplementary materials and supporting information.

## Quick Start

From the paper root directory:
```bash
# Basic compilation with figures (supplementary typically includes figures)
./compile_supplementary

# Quiet mode
./compile_supplementary -q

# Without figures (if needed)
./compile_supplementary --no-figs
```

## Directory Structure

```
02_supplementary/
├── base.tex                  # Main supplementary LaTeX document
├── contents/
│   ├── figures/
│   │   ├── caption_and_media/   # Supplementary figures
│   │   └── captions/            # Figure captions
│   ├── tables/
│   │   ├── caption_and_media/   # Supplementary tables
│   │   └── captions/            # Table captions
│   ├── latex_styles/            # LaTeX formatting (shared)
│   └── supplementary_*.tex     # Supplementary sections
├── archive/                    # Version history
├── logs/                       # Compilation logs
└── docs/                       # Documentation
```

## Output Files

After successful compilation:
- `supplementary.pdf` - Compiled supplementary materials
- `supplementary.tex` - Processed LaTeX source
- `supplementary_diff.pdf` - PDF with tracked changes
- `supplementary_diff.tex` - LaTeX with change tracking

## Adding Supplementary Figures

1. Place files in `contents/figures/caption_and_media/`
2. Use naming: `Supplementary_.XX_description.ext`
   - XX: Two-digit number (01, 02, ...)
   - Common extensions: png, jpg, tif, svg, mmd

Example: `Supplementary_.01_additional_analysis.png`

## Adding Supplementary Tables

1. Place files in `contents/tables/caption_and_media/`
2. Use naming: `Supplementary_.XX_description.tex`

## Compilation Options

Same as manuscript:
- `-f, --figs` - Include figures (default for supplementary)
- `-q, --quiet` - Suppress detailed output
- `-h, --help` - Show help

## Notes

- Supplementary materials share bibliography and styles with main manuscript
- Figures are included by default (unlike manuscript)
- Word counting and diff generation are enabled

<!-- EOF -->