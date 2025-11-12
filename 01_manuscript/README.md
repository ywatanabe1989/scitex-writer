<!-- ---
!-- Timestamp: 2025-09-27 15:35:10
!-- Author: ywatanabe
!-- File: /ssh:sp:/home/ywatanabe/proj/neurovista/paper/01_manuscript/README.md
!-- --- -->

# Manuscript

This directory contains the main manuscript files and compilation outputs.

## Usage

From project root:
```bash
# Basic compilation
./scripts/shell/compile_manuscript.sh

# Skip figures
./scripts/shell/compile_manuscript.sh --no_figs

# Quiet mode
./scripts/shell/compile_manuscript.sh --quiet

# Draft mode (single-pass)
./scripts/shell/compile_manuscript.sh --draft
```

## Directory Structure

```
01_manuscript/
├── base.tex                  # Main LaTeX document
├── contents/
│   ├── figures/
│   │   ├── caption_and_media/   # Place figure files here
│   │   └── captions/            # Figure captions (auto-generated)
│   ├── tables/
│   │   ├── caption_and_media/   # Place table files here
│   │   └── captions/            # Table captions (auto-generated)
│   ├── latex_styles/            # LaTeX packages and formatting
│   ├── abstract.tex
│   ├── introduction.tex
│   ├── methods.tex
│   ├── results.tex
│   ├── discussion.tex
│   └── conclusion.tex
├── archive/                    # Version history
├── logs/                       # Compilation logs
└── docs/                       # Documentation
```

## Output Files

After successful compilation:
- `manuscript.pdf` - Final compiled manuscript
- `manuscript.tex` - Processed LaTeX source
- `manuscript_diff.pdf` - PDF showing changes (when diff enabled)
- `manuscript_diff.tex` - LaTeX with change tracking

## Adding Figures

1. Place figure files in `contents/figures/caption_and_media/`
2. Use naming convention: `.NN_description.ext`
   - NN: Two-digit number (01, 02, ...)
   - description: Brief description (optional)
   - ext: png, jpg, tif, svg, mmd (Mermaid), pptx

Example: `.01_workflow.png`

Missing figures automatically generate placeholder images with instructions.

## Adding Tables

1. Place table files in `contents/tables/caption_and_media/`
2. Use naming convention: `.NN_description.tex`

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

## Troubleshooting

- Check `logs/global.log` for compilation errors
- Ensure all symlinks in `contents/` are properly set
- Verify LaTeX container is available (Apptainer/Singularity)

<!-- EOF -->