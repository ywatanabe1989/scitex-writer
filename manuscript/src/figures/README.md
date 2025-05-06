# Figure Management in SciTex

This directory contains all figure-related files for the manuscript. SciTex uses a structured approach to manage figures efficiently.

## Quick Start Guide

### Adding a New Figure

1. **Create your figure** in PNG format (300 DPI recommended)
2. **Name it properly**: `Figure_ID_XX_description.png` (e.g., `Figure_ID_01_workflow.png`)
3. **Place it in**: `src/` directory
4. **Create a caption file**: `Figure_ID_XX_description.tex` with the same base name
5. **Reference it in text**: Use `Figure~\ref{fig:XX}` (e.g., `Figure~\ref{fig:01}`)
6. **Compile with figures**: Run `./compile --figs` or `./compile -f`

## Directory Structure

- `compiled/`: Contains compiled LaTeX files for each figure, automatically generated during compilation.
- `src/`: Source directory for figure files.
  - Place your `.png` image files here.
  - For each image, create a matching `.tex` caption file with the same name.
  - `png/`: Contains processed PNG versions of figures (auto-generated).
- `templates/`: Templates for figure creation.

## Naming Conventions

All figures must follow this naming pattern:

```
Figure_ID_XX_descriptive_name.[png|tex]
```

Where:
- `Figure_ID` is the fixed prefix
- `XX` is a two-digit figure number (e.g., 01, 02)
- `descriptive_name` is an optional descriptive name (e.g., workflow, architecture)
- The extension is `.png` for image files, and `.tex` for caption files

**Important**: The figure number (`XX`) is used to generate LaTeX reference labels in the format `\label{fig:XX}`.

## Caption Format

For each figure, create a caption file with the same name but `.tex` extension:

```latex
\caption{\textbf{
FIGURE TITLE HERE
}
\smallskip
\\
FIGURE LEGEND HERE. Provide a detailed description of the figure including all components and their significance.
}
% width=1\textwidth
```

Adjust figure width by modifying the `width=1\textwidth` comment. This width specification will be automatically used when compiling figures.

## Figure Compilation

When you compile with figures enabled (`./compile --figs`), SciTex:

1. Processes PNG images for proper display
2. Creates a dedicated "Figures" section at the end of the document
3. Formats each figure with proper spacing, bookmarks, and labels
4. Creates one figure per page in the final PDF

## Final Figure Format in Manuscript

Each figure in the final manuscript will appear like this:

```latex
\clearpage
\begin{figure*}[ht]
    \pdfbookmark[2]{ID XX}{figure_id_XX}
    \centering
    \includegraphics[width=1\textwidth]{./src/figures/png/Figure_ID_XX.png}
    \caption{\textbf{
    FIGURE TITLE HERE
    }
    \smallskip
    \\
    FIGURE LEGEND HERE.
    }
    % width=1\textwidth
    \label{fig:XX}
\end{figure*}
```

## PowerPoint to TIF Conversion

You can convert PowerPoint slides to TIF format using:

```bash
# From the manuscript directory
./compile --pptx2tif
# OR
./compile -p2t
```

**Note:** The PowerPoint to TIF conversion functionality requires Windows with PowerPoint installed, running through WSL (Windows Subsystem for Linux). This feature is not available on standalone Linux or macOS systems.

## Example Structure

```
figures/
├── compiled/          # Auto-generated during compilation
│   ├── 00_Figures_Header.tex     # Figure section header
│   ├── Figure_ID_01_workflow.tex # Compiled figure 1
│   └── Figure_ID_02_methods.tex  # Compiled figure 2
├── src/
│   ├── Figure_ID_01_workflow.tex # Caption file for figure 1
│   ├── Figure_ID_01_workflow.png # Image file for figure 1
│   ├── Figure_ID_02_methods.tex  # Caption file for figure 2
│   ├── Figure_ID_02_methods.png  # Image file for figure 2
│   └── png/                      # Auto-generated processed PNG versions
│       ├── Figure_ID_01_workflow.png 
│       └── Figure_ID_02_methods.png
└── templates/
    └── z_Figure_XX.jnt           # Figure template
```

## For More Information

See the comprehensive figure and table management guide in the documentation:

```
/docs/FIGURE_TABLE_GUIDE.md
```