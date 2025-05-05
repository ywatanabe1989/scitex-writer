# Figures Directory

This directory contains all figure-related files for your manuscript.

## Directory Structure

- `src/`: Place your source figure files and caption files here
  - Figure files: `Figure_ID_XX_descriptive_name.tif`
  - Caption files: `Figure_ID_XX_descriptive_name.tex`
- `compiled/`: Auto-generated files for LaTeX inclusion
- `templates/`: Templates for creating new figures

## How to Add a Figure

1. **Prepare your figure**:
   - Create your figure in PowerPoint, R, Python, etc.
   - Save as a TIF file with 300 DPI resolution
   - Name it using the convention: `Figure_ID_XX_descriptive_name.tif`
     (e.g., `Figure_ID_01_workflow.tif`)

2. **Create a caption file**:
   - Copy the template from `templates/_Figure_ID_XX.tex`
   - Rename it to match your figure file (with .tex extension)
   - Fill in the title and description

3. **PowerPoint Conversion**:
   If your figure is in PowerPoint:
   ```bash
   # From the manuscript directory
   ./compile -p2t
   ```

## Figure Naming Convention

```
Figure_ID_XX_descriptive_name.[tif|tex]
```

Where:
- `Figure_ID` is the fixed prefix
- `XX` is a two-digit figure number (e.g., 01, 02)
- `descriptive_name` is an optional descriptive name (e.g., workflow, architecture)
- The extension is either `.tif` (for image files) or `.tex` (for caption files)

The figure number (`XX`) will be used to generate the LaTeX label: `\label{fig:XX}`

## Referencing Figures

In your manuscript text, reference figures using:

```latex
\figref{01}  % Custom command: Figure~\ref{fig:01}
```

For different parts of multi-panel figures:

```latex
Figure~\ref{fig:01}A     % Panel A
Figure~\ref{fig:01}(i)   % Sub-panel i
```

## Figure Width

You can adjust the figure width in the caption file:

```
% width=0.8\textwidth
```

Use values between 0.5 and 1.0 for typical figures.