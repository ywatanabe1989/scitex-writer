# Supplementary Materials

This directory contains supplementary materials and supporting information.

## Usage

From project root:
```bash
# Basic compilation
./scripts/shell/compile_supplementary.sh

# Skip figures
./scripts/shell/compile_supplementary.sh --no_figs

# Quiet mode
./scripts/shell/compile_supplementary.sh --quiet

# Draft mode
./scripts/shell/compile_supplementary.sh --draft
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
│   ├── latex_styles/            # LaTeX formatting (00_shared)
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

- `-nf, --no_figs` - Skip figure processing
- `-nt, --no_tables` - Skip table processing
- `-nd, --no_diff` - Skip diff generation
- `-d, --draft` - Single-pass compilation
- `-dm, --dark_mode` - Black background, white text
- `-p2t, --ppt2tif` - Convert PowerPoint to TIF (WSL)
- `-c, --crop_tif` - Auto-crop TIF images
- `-q, --quiet` - Suppress detailed output
- `--force` - Force full recompilation
- `-h, --help` - Show help

## Notes

- Shares bibliography and LaTeX styles with main manuscript
- Word counting and diff generation enabled

<!-- EOF -->