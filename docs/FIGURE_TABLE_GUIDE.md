# SciTex Figure and Table Management Guide

This document provides comprehensive instructions for managing figures and tables within SciTex.

## Table of Contents

1. [Overview](#overview)
2. [Figure Management](#figure-management)
   - [Directory Structure](#figure-directory-structure)
   - [Naming Conventions](#figure-naming-conventions)
   - [Creating Figures](#creating-figures)
   - [PowerPoint to TIF Conversion](#powerpoint-to-tif-conversion)
   - [Figure Captions](#figure-captions)
   - [Referencing Figures](#referencing-figures)
3. [Table Management](#table-management)
   - [Directory Structure](#table-directory-structure)
   - [Naming Conventions](#table-naming-conventions)
   - [Creating Tables](#creating-tables)
   - [Table Captions](#table-captions)
   - [Referencing Tables](#referencing-tables)
4. [Compilation Process](#compilation-process)
   - [Figure Processing](#figure-processing)
   - [Table Processing](#table-processing)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

## Overview

SciTex provides a comprehensive system for managing figures and tables in scientific manuscripts, handling conversion, compilation, and reference management automatically. The system follows a standardized workflow to ensure consistency and ease of use.

## Figure Management

### Figure Directory Structure

```
manuscript/src/figures/
├── compiled/           # Auto-generated LaTeX files for figures
├── src/                # Source files for figures
│   ├── Figure_ID_XX.tif  # Source image files 
│   ├── Figure_ID_XX.tex  # Caption files
│   └── jpg/              # Auto-generated JPEG versions for preview
├── templates/          # Templates for creating new figures
└── workspace/          # Optional working directory for figure development
```

### Figure Naming Conventions

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

### Creating Figures

#### Method 1: From PowerPoint Slides

1. Create your figure in PowerPoint
2. Save the PowerPoint file in the `workspace` directory for tracking
3. Convert to TIF using the built-in conversion tool:

```bash
# From the manuscript directory
./compile -p2t
```

This will automatically process all PowerPoint files and convert them to TIF format.

#### Method 2: Direct TIF Creation

1. Create a TIF file with appropriate resolution (300 DPI recommended)
2. Name it according to the naming convention (e.g., `Figure_ID_01_workflow.tif`)
3. Place it in the `src/figures/src/` directory

### PowerPoint to TIF Conversion

SciTex includes a dedicated tool for converting PowerPoint presentations to TIF files:

```bash
# Convert a single PowerPoint file
python manuscript/scripts/py/pptx2tif.py file -i path/to/figure.pptx -o manuscript/src/figures/src/

# Convert all PowerPoint files in a directory
python manuscript/scripts/py/pptx2tif.py batch -d path/to/pptx/directory -o manuscript/src/figures/src/
```

Options:
- `--resolution`: Set image resolution in DPI (default: 300)
- `--no-crop`: Disable automatic cropping of whitespace
- `--margin`: Set margin size in pixels when cropping (default: 30)
- `--verbose`: Enable detailed output

### Figure Captions

For each figure image file, you must create a corresponding caption file with the same name but a `.tex` extension. For example:

```
Figure_ID_01_workflow.tif   # Image file
Figure_ID_01_workflow.tex   # Caption file
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

You can adjust the figure width by modifying the `width=1\textwidth` comment. This value will be extracted and used during compilation.

### Referencing Figures

To reference figures in your manuscript text, use:

```latex
Figure~\ref{fig:XX}
```

Where `XX` is the ID number from the figure filename. For example, to reference `Figure_ID_01_workflow.tif`, use:

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
manuscript/src/tables/
├── compiled/           # Auto-generated LaTeX files for tables
└── src/                # Source files for tables
    ├── Table_ID_XX.csv  # Source data files
    ├── Table_ID_XX.tex  # Caption files
    └── _Table_ID_XX.tex # Template file
```

### Table Naming Conventions

All tables must follow this naming pattern:

```
Table_ID_XX_descriptive_name.[csv|tex]
```

Where:
- `Table_ID` is the fixed prefix
- `XX` is a two-digit table number (e.g., 01, 02)
- `descriptive_name` is an optional descriptive name (e.g., results, parameters)
- The extension is either `.csv` (for data files) or `.tex` (for caption files)

**Important**: The table number (`XX`) is used to generate LaTeX reference labels in the format `\label{tab:XX}`.

### Creating Tables

1. **Create CSV File**:
   - Create a CSV file with your table data
   - Place it in `manuscript/src/tables/src/` directory
   - Follow the naming convention: `Table_ID_XX_descriptive_name.csv`
   - First row should contain column headers

2. **Example CSV Format**:
   ```csv
   Parameter,Value,Unit
   Length,10.5,cm
   Width,5.2,cm
   Height,3.7,cm
   ```

### Table Captions

For each CSV file, create a corresponding caption file with the same name but a `.tex` extension:

```
Table_ID_01_parameters.csv  # Data file
Table_ID_01_parameters.tex  # Caption file
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

Where `XX` is the ID number from the table filename. For example, to reference `Table_ID_01_parameters.csv`, use:

```latex
Table~\ref{tab:01}
```

## Compilation Process

During the manuscript compilation process, SciTex performs several steps to handle figures and tables:

### Figure Processing

1. **Format Conversion**:
   - TIF files are converted to JPEG for preview
   - PowerPoint files are converted to TIF (if using `-p2t` option)

2. **Caption Integration**:
   - Caption files (.tex) are combined with image references
   - Width parameters are extracted from caption files

3. **LaTeX Generation**:
   - LaTeX code is generated to include figures with proper formatting
   - Labels are automatically inserted based on figure IDs

### Table Processing

1. **CSV Processing**:
   - CSV files are parsed and formatted into LaTeX tables
   - Column headers are properly formatted

2. **Caption Integration**:
   - Caption files are combined with table content
   - Width parameters are extracted for proper sizing

3. **LaTeX Generation**:
   - LaTeX code is generated with proper table formatting
   - Labels are automatically inserted based on table IDs

## Best Practices

1. **Use Descriptive Filenames**:
   - Include meaningful descriptive terms in filenames
   - Example: `Figure_ID_01_workflow.tif` instead of just `Figure_ID_01.tif`

2. **Maintain Consistent Formatting**:
   - Use the same style for all figures in your manuscript
   - Keep fonts, colors, and line weights consistent

3. **Optimize Image Resolution**:
   - Use 300 DPI for publication-quality figures
   - Crop images appropriately to remove unnecessary whitespace

4. **Version Control**:
   - Keep previous versions of important figures in the workspace directory
   - Use descriptive commit messages when updating figures

5. **Test Compilation Frequently**:
   - Use the `-nf` option to compile without figures during development
   - Check the final PDF to ensure figures and tables appear correctly

## Troubleshooting

### Common Figure Issues

1. **Figure Not Appearing**:
   - Check that the TIF and TEX files have matching names
   - Verify that the TIF file is in the correct format (8-bit, RGB, or grayscale)
   - Ensure the file is in the correct directory (src/figures/src/)

2. **Figure Too Large or Small**:
   - Adjust the width parameter in the caption file
   - Example: `% width=0.8\textwidth` for 80% width

3. **Image Quality Issues**:
   - Ensure the source image has sufficient resolution (300 DPI)
   - Check for compression artifacts in the TIF file
   - Use a lossless format for the source file

### Common Table Issues

1. **Table Formatting Problems**:
   - Ensure the CSV file uses commas as separators
   - Check for special characters that might need escaping
   - Verify column headers are properly formatted

2. **Table Too Wide**:
   - Consider using a landscape orientation for wide tables
   - Abbreviate column headers if appropriate
   - Use smaller font size by adjusting the LaTeX code

3. **Missing References**:
   - Ensure the table ID in the filename matches the reference in the text
   - Check for typos in the reference command
   - Verify the table is included in the compilation process

For more persistent issues, check the LaTeX compilation log or contact the SciTex support team.