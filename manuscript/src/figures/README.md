# Figure Management in SciTex

This directory contains all figure-related files for the manuscript. SciTex uses a structured approach to manage figures efficiently.

## Directory Structure

- `compiled/`: Contains compiled LaTeX files for each figure, automatically generated during compilation.
- `src/`: Source directory for figure files.
  - Place your `.tif` image files here.
  - For each image, create a matching `.tex` caption file with the same name.
  - `jpg/`: Contains JPEG versions of figures (auto-generated).
- `templates/`: Templates for figure creation.
- `workspace/`: Working directory for figure development (optional).

## Naming Conventions

All figures must follow this naming pattern:

```
Figure_ID_XX_descriptive_name.[tif|tex]
```

Where:
- `Figure_ID` is the fixed prefix
- `XX` is a two-digit figure number (e.g., 01, 02)
- `descriptive_name` is an optional descriptive name (e.g., workflow, architecture)
- The extension is either `.tif` (for image files) or `.tex` (for caption files)

**Important**: The figure number (`XX`) is used to generate LaTeX reference labels in the format `\label{fig:XX}`.

## Quick Start Guide

### Creating a Figure

1. **Prepare your figure**:
   - Create your figure in PowerPoint or your preferred graphics software
   - Save as TIF file with 300 DPI resolution

2. **Add to SciTex**:
   - Place the TIF file in the `src/` directory
   - Create a caption file with the same name but `.tex` extension
   - Use the template from `templates/` directory

3. **Caption Template**:
   ```latex
   \caption{\textbf{
   FIGURE TITLE HERE
   }
   \smallskip
   \\
   FIGURE LEGEND HERE.
   }
   % width=1\textwidth
   ```

### PowerPoint to TIF Conversion

You can convert PowerPoint slides to TIF format using:

```bash
# From the manuscript directory
./compile -p2t
```

### Referencing Figures

To reference figures in your manuscript text, use:

```latex
Figure~\ref{fig:XX}
```

Where `XX` is the ID number from the figure filename (e.g., `Figure~\ref{fig:01}` for `Figure_ID_01_workflow.tif`).

## Example Structure

```
figures/
├── compiled/
│   └── Figure_ID_01_workflow.tex    # Auto-generated during compilation
├── src/
│   ├── Figure_ID_01_workflow.tex    # Caption file
│   ├── Figure_ID_01_workflow.tif    # Image file
│   ├── jpg/
│       └── Figure_ID_01_workflow.jpg # Auto-generated preview
├── templates/
│   └── z_Figure_XX.jnt
└── workspace/                      # Optional working directory
    └── 01_workflow/
        ├── Figure_01.pptx
        └── source_files/
```

## For More Information

See the comprehensive figure and table management guide in the documentation:

```
/docs/FIGURE_TABLE_GUIDE.md
```