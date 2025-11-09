# Figure Management System

Automated figure processing pipeline for multi-panel figures, format conversions, and LaTeX integration.

## Usage

### Adding a Figure

1. **Place figure file**: Add to `caption_and_media/` with format `XX_description.ext`
   - Single figure: `01_demographic_data.jpg`
   - Multi-panel: `01a_demographic_data.jpg`, `01b_demographic_data.jpg`
2. **Add caption**: Create `XX_description.tex` in same directory
3. **Compile**: Run `./compile -m` (figures included by default)
4. **Reference**: Use `Figure~\ref{fig:XX_description}` in manuscript

## Directory Structure

```
figures/
├── caption_and_media/           # Source files and captions
│   ├── [0-9]*.{jpg,png,tif,...} # Figure source files
│   ├── [0-9]*.tex               # Caption files
│   ├── jpg_for_compilation/     # Auto-generated final JPGs
│   └── templates/               # Caption templates
├── compiled/                    # Auto-generated LaTeX includes
│   ├── 00_Figures_Header.tex   # Section header (used only if no figures)
│   ├── [0-9]*.tex              # Individual figure metadata
│   └── FINAL.tex               # Combined output for manuscript
└── README.md
```

## Naming Convention

### Format: `XX[panel]_description.ext`

- `XX`: Two-digit figure number (01, 02, ...)
- `[panel]`: Optional panel letter (a, b, c, ... or A, B, C, ...)
- `_description`: Descriptive name (underscores allowed)
- `.ext`: File extension

### Examples

```
01_demographic_data.jpg         # Single figure
02a_pac_analysis.png           # Panel A of figure 2
02b_pac_analysis.png           # Panel B of figure 2 (auto-tiled with 2a)
03_standalone.tif               # Single figure
```

## Processing Pipeline

### 1. Format Conversion Cascade

The system automatically converts formats in priority order:

```
PPTX → TIF → PNG → JPG → Final Output
         ↓
      [Crop]  (optional)
```

| Source Format | Extensions | Conversion Path |
|--------------|------------|-----------------|
| PowerPoint | `.pptx` | → TIF → PNG → JPG |
| TIFF | `.tif`, `.tiff` | → PNG → JPG |
| Mermaid | `.mmd` | → PNG → JPG |
| PNG | `.png` | → JPG |
| SVG | `.svg` | → JPG |
| JPEG | `.jpg`, `.jpeg` | Direct use |

### 2. Panel Tiling

Multi-panel figures are automatically detected and combined:

1. **Detection**: Files matching `XXa_`, `XXb_`, etc. identified
2. **Grouping**: Panels grouped by base number (XX)
3. **Tiling**: Combined into single composed figure
4. **Labeling**: Panel labels (A, B, C) added automatically
5. **Output**: Single JPG created as `XX_description.jpg`

### 3. Compilation Flow

```
Source Files → Conversion → Tiling → JPG Output → LaTeX Integration → PDF
```

Key features:
- **Clean start**: Previous outputs cleared before processing
- **Temporary workspace**: Conversions in `.temp_jpg_conversion/`
- **Selective copying**: Only composed figures (not panels) to final directory
- **Automatic placeholders**: Generated for missing figures with captions

## Caption Files

### Basic Template

```latex
\caption{\textbf{
Title of the Figure
}
\smallskip
\\
Description text here.
}
% width=0.95\textwidth
```

### Multi-Panel Template

```latex
\caption{\textbf{
Multi-Panel Figure Title
}
\smallskip
\\
\textbf{(A)} Description of panel A showing specific results.
\textbf{(B)} Description of panel B with complementary data.
\textbf{(C)} Additional panel description if needed.
}
% width=0.95\textwidth
```

## Compilation Options

```bash
# Default: includes figures
./scripts/shell/compile_manuscript.sh

# Skip figures
./scripts/shell/compile_manuscript.sh --no_figs

# With PowerPoint conversion (WSL)
./scripts/shell/compile_manuscript.sh --ppt2tif

# With automatic cropping
./scripts/shell/compile_manuscript.sh --crop_tif

# Quiet mode
./scripts/shell/compile_manuscript.sh --quiet
```

## Advanced Features

### Symlink Support

Link to data files stored elsewhere:

```bash
ln -s /data/analysis/figure1.jpg caption_and_media/01_results.jpg
```

### Placeholder Generation

When caption exists without source image:
- Automatic placeholder with instructions
- Shows required file path and formats
- Includes LaTeX reference format

### Panel Specifications

- **Automatic detection**: Both lowercase (a-z) and uppercase (A-Z) supported
- **Smart tiling**: Optimizes layout based on panel count
- **Consistent sizing**: Panels resized to match for uniform appearance
- **Label positioning**: Automatic placement with appropriate font size

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Figures not in PDF | Check `jpg_for_compilation/` for output files |
| Panels not tiling | Verify naming pattern (`XXa_`, `XXb_`) matches |
| Wrong figure order | Ensure two-digit numbering (01, not 1) |
| Missing placeholders | Confirm ImageMagick installation |
| Compilation errors | Review `01_manuscript/logs/global.log` |

### Validation Checklist

- [ ] Figure files follow naming convention
- [ ] Caption files have matching base names
- [ ] Panel files share common base (before panel letter)
- [ ] All referenced figures exist
- [ ] JPGs appear in `jpg_for_compilation/`
- [ ] FINAL.tex contains figure entries

## Example Workflows

### Single Figure

```bash
# 1. Add figure
cp experiment_results.png caption_and_media/01_results.png

# 2. Create caption
echo '\caption{\textbf{Experimental Results}
\smallskip
\\
Data showing primary outcomes from the experiment.
}' > caption_and_media/01_results.tex

# 3. Compile
./scripts/shell/compile_manuscript.sh
```

### Multi-Panel Figure

```bash
# 1. Add panels (via symlinks)
ln -s /data/panel_a.jpg caption_and_media/02a_comparison.jpg
ln -s /data/panel_b.jpg caption_and_media/02b_comparison.jpg
ln -s /data/panel_c.jpg caption_and_media/02c_comparison.jpg

# 2. Create unified caption
cat > caption_and_media/02_comparison.tex << 'EOF'
\caption{\textbf{
Comparative Analysis
}
\smallskip
\\
\textbf{(A)} Baseline measurements.
\textbf{(B)} Treatment response.
\textbf{(C)} Long-term follow-up.
}
EOF

# 3. Compile (auto-tiles panels)
./scripts/shell/compile_manuscript.sh
```

## Technical Details

### File Processing Order

1. `process_figures.sh`: Main orchestrator
2. Format conversion functions (modular)
3. `tile_panels.py`: Panel combination
4. `compile_legends()`: LaTeX generation
5. `compile_figure_tex_files()`: Final assembly

### Key Functions

- `convert_figure_formats_in_cascade()`: Manages conversion pipeline
- `tile_panels()`: Handles multi-panel assembly
- `copy_composed_jpg_files()`: Filters final outputs
- `compile_legends()`: Generates LaTeX metadata
- `compile_figure_tex_files()`: Creates FINAL.tex

### Configuration

Paths configured in `config/load_config.sh`:
- `SCITEX_WRITER_FIGURE_CAPTION_MEDIA_DIR`: Source directory
- `SCITEX_WRITER_FIGURE_JPG_DIR`: Output directory
- `SCITEX_WRITER_FIGURE_COMPILED_DIR`: LaTeX directory
- `SCITEX_WRITER_FIGURE_COMPILED_FILE`: Final output (FINAL.tex)

<!-- EOF -->