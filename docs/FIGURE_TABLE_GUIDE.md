<!-- ---
!-- Timestamp: 2025-05-06 19:57:46
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/SciTex/docs/FIGURE_TABLE_GUIDE.md
!-- --- -->

# SciTex Figure and Table Management Guide

This comprehensive guide explains how to manage figures and tables in the SciTex system, including naming conventions, directory structure, file formats, and referencing in your manuscript.

## Table of Contents

1. [Quick Start Guide](#quick-start-guide)
2. [Figure Management](#figure-management)
   - [Figure Directory Structure](#figure-directory-structure)
   - [Figure Naming Conventions](#figure-naming-conventions)
   - [Creating and Adding Figures](#creating-and-adding-figures)
   - [Figure Captions](#figure-captions)
   - [Figure Format in Manuscript](#figure-format-in-manuscript)
   - [Referencing Figures](#referencing-figures)
3. [Table Management](#table-management)
   - [Table Directory Structure](#table-directory-structure)
   - [Table Naming Conventions](#table-naming-conventions)
   - [Creating and Adding Tables](#creating-and-adding-tables)
   - [Table Captions](#table-captions)
   - [Referencing Tables](#referencing-tables)
4. [Compilation Process](#compilation-process)
   - [How Figures Are Processed](#how-figures-are-processed)
   - [How Tables Are Processed](#how-tables-are-processed)
5. [Troubleshooting](#troubleshooting)
6. [Examples](#examples)

## Quick Start Guide

### Adding a New Figure

1. **Create your figure** in PNG format (recommended 300 DPI)
2. **Name it properly**: `.XX_description.png` (e.g., `.01_workflow.png`)
3. **Place it in**: `manuscript/contents/figures/contents/`
4. **Create a caption file**: `.XX_description.tex` with the same base name
5. **Reference it in text**: Use `Figure~\ref{fig:XX}` (e.g., `Figure~\ref{fig:01}`)
6. **Compile with figures**: Run `./compile --figs` or `./compile -f`

### Adding a New Table

1. **Create your table** in CSV format or directly in LaTeX
2. **Name it properly**: `.XX_description.csv` (e.g., `.01_results.csv`)
3. **Place it in**: `manuscript/contents/tables/contents/`
4. **Create a caption file**: `.XX_description.tex` with the same base name
5. **Reference it in text**: Use `Table~\ref{tab:XX}` (e.g., `Table~\ref{tab:01}`)
6. **Compile**: Run `./compile`

## Figure Management

### Figure Directory Structure

The figure management system uses the following directory structure:

```
manuscript/contents/figures/
├── compiled/           # Auto-generated LaTeX files (DO NOT EDIT)
│   ├── 00_Figures_Header.tex     # Figure section header
│   ├── .01_workflow.tex # Compiled figure 1
│   └── .02_methods.tex  # Compiled figure 2
├── contents/                # Source files (PLACE YOUR FILES HERE)
│   ├── .XX.png  # Source image files (PNG format)
│   ├── .XX.tex  # Caption files
│   └── png/              # Auto-generated processed PNG archive
├── templates/          # Templates for new figures
└── .tex/               # Hidden directory for compiled figure files
```

### Figure Naming Conventions

All figures must follow this naming pattern:

```
.XX_descriptive_name.ext
```

Where:
- `Figure_ID`: Fixed prefix (required)
- `XX`: Two-digit figure number (01, 02, etc.) (required)
- `descriptive_name`: Short, descriptive name (required)
- `.ext`: File extension: `.png` for images or `.tex` for captions

**Important**: The figure number (`XX`) is used to generate LaTeX reference labels in the format `\label{fig:XX}`.

### Creating and Adding Figures

#### Method 1: Direct Image Creation

1. Create a PNG or JPG file with appropriate resolution (300 DPI recommended)
2. Name it according to the naming convention (e.g., `.01_workflow.png`)
3. Place it in the `manuscript/contents/figures/contents/` directory

#### Method 2: From PowerPoint Slides

1. Create your figure in PowerPoint
2. Convert to PNG using the built-in conversion tool:

```bash
# From the root directory
./compile -m --pptx2png

# OR from the manuscript directory
cd manuscript && ./compile -p2p
```

#### Method 3: Using SVG Vector Graphics (NEW)

For high-quality vector graphics created in tools like Inkscape, Illustrator, or other vector editors:

1. Create your figure in your preferred vector drawing tool
2. Export as SVG format
3. Name according to convention (e.g., `.03_flowchart.svg`)
4. Place in the `manuscript/contents/figures/contents/` directory
5. Create a caption file with same base name (e.g., `.03_flowchart.tex`)
6. Use the SVG template from templates directory for better formatting

The system will automatically convert SVG files to high-resolution JPGs for inclusion in the PDF.

#### Method 4: Using TikZ (LaTeX Drawing)

For vector-based figures created directly in LaTeX, you can use TikZ:

1. Create a .tex file following the naming convention
2. Include a TikZ environment with your figure code
3. Add a proper caption

Example:

```latex
\begin{tikzpicture}[
    block/.style={rectangle, draw, fill=blue!20, 
                 text width=2.5cm, text centered, rounded corners, minimum height=1.5cm},
    line/.style={draw, -latex'},
    cloud/.style={draw, ellipse, fill=red!20, minimum height=1cm}
]

% Place blocks
\node [block] (manuscript) {Manuscript Preparation};
\node [block, right=of manuscript] (AI) {AI-Assisted Revision};
\node [block, right=of AI] (compile) {LaTeX Compilation};

% Connect blocks with arrows
\path [line] (manuscript) -- (AI);
\path [line] (AI) -- (compile);

\end{tikzpicture}

\caption{\textbf{SciTex workflow diagram.} The figure illustrates the key components...}
```

### Figure Captions

For each figure image file, create a corresponding caption file with the same name but a `.tex` extension:

```
.01_workflow.png   # Image file
.01_workflow.tex   # Caption file
```

The caption file should follow this template:

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

Adjust figure width by modifying the `width=1\textwidth` comment. This width specification will be automatically used when compiling figures.

### Figure Format in Manuscript

In the final manuscript, figures are compiled into a dedicated "Figures" section. Each figure follows this structure:

```latex
\clearpage
\begin{figure*}[ht]
    \pdfbookmark[2]{ID XX}{.XX}
    \centering
    \includegraphics[width=1\textwidth]{./contents/figures/png/.XX.png}
    \caption{\textbf{
    FIGURE TITLE HERE
    }
    \smallskip
    \\
    FIGURE LEGEND HERE describing the content and significance of the figure in detail.
    }
    % width=1\textwidth
    \label{fig:XX}
\end{figure*}
```

This format creates:
- One figure per page with `\clearpage` command
- Consistent figure size and positioning
- PDF bookmarks for easy navigation
- Proper reference labels

### Referencing Figures

To reference figures in your manuscript text, use:

```latex
Figure~\ref{fig:XX}
```

Where `XX` is the ID number from the figure filename. For example, to reference `.01_workflow.tif`, use:

```latex
Figure~\ref{fig:01}
```

For multi-panel figures, use:

```latex
Figure~\ref{fig:01}A
Figure~\ref{fig:01}(i)
```

## Table Management

### Table Directory Structure

```
manuscript/contents/tables/
├── compiled/           # Auto-generated LaTeX files (DO NOT EDIT)
└── contents/                # Source files (PLACE YOUR FILES HERE)
    ├── .XX.csv  # Source data files
    ├── .XX.tex  # Caption files
    └── _.XX.tex # Template file
```

### Table Naming Conventions

All tables must follow this naming pattern:

```
.XX_descriptive_name.ext
```

Where:
- `Table_ID`: Fixed prefix (required)
- `XX`: Two-digit table number (01, 02, etc.) (required)
- `descriptive_name`: Short, descriptive name (required)
- `.ext`: File extension: `.csv` for data or `.tex` for captions

**Important**: The table number (`XX`) is used to generate LaTeX reference labels in the format `\label{tab:XX}`.

### Creating and Adding Tables

1. Create a CSV file with your table data following this structure:
   ```csv
   Column1,Column2,Column3
   Value1,Value2,Value3
   Value4,Value5,Value6
   ```

2. Name it according to the naming convention (e.g., `.01_results.csv`)
3. Place it in the `manuscript/contents/tables/contents/` directory

### Table Captions

For each table data file, create a corresponding caption file with the same name but a `.tex` extension:

```
.01_results.csv   # Data file
.01_results.tex   # Caption file
```

The caption file should follow this template:

```latex
\caption{\textbf{
TABLE TITLE HERE
}
\smallskip
\\
TABLE LEGEND HERE.
}
% width=1\textwidth
```

### Referencing Tables

To reference tables in your manuscript text, use:

```latex
Table~\ref{tab:XX}
```

Where `XX` is the ID number from the table filename. For example, to reference `.01_results.csv`, use:

```latex
Table~\ref{tab:01}
```

## Compilation Process

### How Figures Are Processed

During compilation, when you run `./compile --figs` or `./compile -f`, the following steps occur:

1. **Initialization**: Creates necessary directories and clears previous outputs
2. **PowerPoint Conversion** (if requested): Converts PPTX to PNG files
3. **Filename Normalization**: Ensures consistent lowercase naming
4. **Caption Generation**: Creates caption files if missing
5. **Image Cropping**: Crops PNG files to remove excess white space
6. **Image Processing**: Converts any existing TIF/JPG files to PNG format
7. **Legend Compilation**: Combines images with captions in LaTeX format
8. **Figure Visibility**: Enables or disables figure inclusion based on flags
9. **File Gathering**: Collects all figure files into one section

All these steps are handled by the `process_figures.sh` script, which is called during compilation.

### How Tables Are Processed

Tables are processed in a similar way:

1. **Initialization**: Creates necessary directories
2. **CSV Processing**: Converts CSV data to LaTeX tables
3. **Caption Integration**: Combines tables with captions
4. **File Gathering**: Collects all table files into one section

The processing is handled by the `process_tables.sh` script.

## Troubleshooting

### Common Figure Issues

1. **Figure Not Appearing**:
   - Check that the PNG and TEX files have matching names
   - Verify the PNG file format (8-bit, RGB, or grayscale)
   - Ensure the file is in the correct directory
   - Examine debug files in `manuscript/contents/figures/compiled/debug/`

2. **Figure Too Large or Small**:
   - Adjust the width parameter in the caption file
   - Example: `% width=0.8\textwidth` for 80% width

3. **Resolution Issues**:
   - Ensure source image has sufficient resolution (300 DPI)
   - Check for compression artifacts in the PNG file

4. **Caption Problem**:
   - Ensure your caption follows the correct format
   - Check for LaTeX syntax errors in your caption
   - Verify that title and legend are properly formatted

5. **Format Issues**:
   - Check if the figure contains special characters
   - Verify that your TikZ code is correct (if using TikZ)
   - Look for mismatched braces or commands

### Common Table Issues

1. **Table Formatting Problems**:
   - Ensure the CSV file uses commas as separators
   - Check for special characters that might need escaping
   - Verify column headers are properly formatted

2. **Table Too Wide**:
   - Consider landscape orientation for wide tables
   - Abbreviate column headers
   - Use smaller font size

## Examples

### Example Figure Files

File: `manuscript/contents/figures/contents/.01_workflow.png` (Image file)

File: `manuscript/contents/figures/contents/.01_workflow.tex` (Caption file)
```latex
\caption{\textbf{
Workflow diagram for the SciTex system.
}
\smallskip
\\
The figure illustrates the key components and workflow of the SciTex system, 
including manuscript preparation, AI-assisted revision, figure processing,
citation management, and LaTeX compilation.
}
% width=0.9\textwidth
```

Referenced in text (`manuscript/contents/introduction.tex`):
```latex
Figure~\ref{fig:01} illustrates the overall workflow of the SciTex system.
```

### Example Table Files

File: `manuscript/contents/tables/contents/.01_results.csv` (Data file)
```csv
Method,Accuracy (%),Runtime (s)
Baseline,85.2,12.3
SciTex,92.7,8.9
```

File: `manuscript/contents/tables/contents/.01_results.tex` (Caption file)
```latex
\caption{\textbf{
Performance comparison of baseline and SciTex methods.
}
\smallskip
\\
The table shows accuracy (in percentage) and runtime (in seconds) for the 
baseline method compared to the SciTex approach across standardized tests.
}
% width=0.8\textwidth
```

Referenced in text (`manuscript/contents/results.tex`):
```latex
Table~\ref{tab:01} shows the performance comparison between the baseline and 
SciTex methods.
```

### Example Complete Figure Section

Below is an example of a complete Figure section that will be generated:

```latex
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% FIGURES
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\clearpage
\section*{Figures}
\label{figures}
\pdfbookmark[1]{Figures}{figures}

        \clearpage
        \begin{figure*}[ht]
            \pdfbookmark[2]{ID 01}{.01}
            \centering
            \includegraphics[width=1\textwidth]{./contents/figures/png/.01_workflow.png}
            \caption{\textbf{
Workflow diagram for the SciTex system.
}
\smallskip
\\
The figure illustrates the key components and workflow of the SciTex system, 
including manuscript preparation, AI-assisted revision, figure processing,
citation management, and LaTeX compilation.
}
% width=0.9\textwidth
            \label{fig:01}
        \end{figure*}
        \clearpage
        \begin{figure*}[ht]
            \pdfbookmark[2]{ID 02}{.02}
            \centering
            \includegraphics[width=0.8\textwidth]{./contents/figures/png/.02_architecture.png}
            \caption{\textbf{
Architecture of the SciTex system.
}
\smallskip
\\
The figure shows the hierarchical organization of the SciTex repository, with emphasis on 
the manuscript component. The modular structure separates content files, supporting materials, 
styling definitions, and automation scripts.
}
% width=0.8\textwidth
            \label{fig:02}
        \end{figure*}
```

This format ensures that each figure appears on its own page with proper labeling, referencing, and formatting for academic publications.

<!-- EOF -->