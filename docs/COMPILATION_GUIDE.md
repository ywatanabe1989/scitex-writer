# SciTex Compilation Guide

This guide explains how the SciTex compilation system works, including the processing of LaTeX files, figures, and tables.

## Quick Start

To compile your manuscript with figures:

```bash
# From the root directory
./compile -m --figs

# OR from the manuscript directory
cd manuscript && ./compile -f
```

## Compilation Process Overview

The SciTex compilation process involves several steps:

1. **Preprocessing**: Collects all necessary input files
2. **Figure/Table Processing**: Processes figures and tables for inclusion
3. **Main Compilation**: Compiles the manuscript into a PDF
4. **Diff Generation**: Creates a diff version showing changes
5. **Cleanup**: Removes temporary files and organizes outputs

## Main Compilation Script (`./compile`)

The main script at the root level serves as a dispatcher that lets you compile different components:

- **Manuscript**: The main scientific document
- **Supplementary**: Additional materials
- **Revision**: Revisions for journal submission

### Options

```
-m, --manuscript    Compile manuscript
-s, --supplementary Compile supplementary materials
-r, --revision      Compile revision
-a, --all           Compile all components (default)
-h, --help          Show help message

Additional options:
-p,   --push        Enables push action
-f,   --figs        Includes figures
-p2t, --pptx2tif    Converts PowerPoint to TIF
-v,   --verbose     Shows detailed logs for LaTeX compilation
-c,   --citations   Inserts citations with GPT
-t,   --terms       Enables term checking with GPT
```

## Manuscript Compilation Process

When compiling the manuscript (`./manuscript/compile`), the following steps occur:

1. **Parse Arguments**: Process command-line flags
2. **Run Checks**: Verify system requirements and file integrity
3. **Revision Processing** (optional): Apply AI-assisted revisions
4. **Insert Citations** (optional): Insert citations using AI
5. **Process Figures**: Convert and prepare figures
6. **Process Tables**: Format and prepare tables
7. **Count Words/Figures/Tables**: Generate statistics
8. **Compile Main TeX**: Generate the main PDF
9. **Generate Compiled TeX**: Create a single consolidated TeX file
10. **Generate Diff TeX**: Create a diff file for version comparison
11. **Compile Diff TeX**: Generate the diff PDF
12. **Cleanup**: Remove temporary files
13. **Versioning**: Create a versioned backup
14. **Check Terms** (optional): Verify terminology consistency
15. **Generate Tree**: Create a file structure representation
16. **Git Push** (optional): Push changes to repository

## Figure Processing

The figure processing (`process_figures.sh`) includes these steps:

1. **Initialization**: Create necessary directories and clear previous outputs
2. **Caption Generation**: Ensure caption files exist for all figures
3. **Format Normalization**: Ensure consistent naming conventions
4. **PowerPoint Conversion** (optional): Convert PPTX to TIF
5. **Image Cropping**: Automatically crop TIF files
6. **TIF to JPG Conversion**: Convert TIF files to JPG for compatibility
7. **Legend Compilation**: Combine images with captions
8. **Figure Visibility Handling**: Enable/disable figures as requested
9. **TeX File Generation**: Create consolidated figure sections

### Key Figure Processing Functions

The `process_figures.sh` script contains several important functions:

- `init()`: Sets up directories and backs up existing files
- `ensure_caption()`: Creates caption files for images if they don't exist
- `ensure_lower_letters()`: Normalizes filenames to lowercase
- `pptx2tif()`: Converts PowerPoint files to TIF format
- `crop_tif()`: Crops TIF files to remove excess whitespace
- `tif2jpg()`: Converts TIF files to JPG format
- `compile_legends()`: Creates LaTeX files that combine images with captions
- `_toggle_figures()`: Enables or disables figure inclusion
- `gather_tex_files()`: Collects all figure files into a single section

## Table Processing

Table processing (`process_tables.sh`) follows these steps:

1. **Initialization**: Creates necessary directories
2. **CSV Processing**: Converts CSV files to LaTeX tables
3. **Caption Integration**: Combines tables with captions
4. **File Gathering**: Collects all table files into one section

## TeX File Gathering

The `gather_tex.sh` script consolidates all LaTeX files into a single manuscript:

1. Starts with the main template file
2. Recursively resolves all `\input{}` commands
3. Creates a single consolidated file for compilation and diff generation
4. Preserves comments and structure for debugging

### How File Gathering Works

The script processes the main LaTeX file and all its included files recursively:

1. It reads the main file line by line
2. When it encounters an `\input{file}` command, it replaces it with the contents of the referenced file
3. It repeats this process until no more `\input{}` commands remain
4. The result is a single, self-contained LaTeX file that can be compiled

## Handling Figure and Table References

When you reference figures and tables in your LaTeX files using `\ref{fig:XX}` or `\ref{tab:XX}`, the compilation process ensures these references work correctly:

1. Figure/table files are processed to include proper `\label{fig:XX}` or `\label{tab:XX}` commands
2. LaTeX's reference system connects these labels with your `\ref{}` commands
3. The resulting PDF displays the correct figure/table numbers

## Debugging the Compilation Process

### Debug Directories

Debugging information is stored in these locations:

```
manuscript/main/debug/                       # Main manuscript debugging
manuscript/src/figures/compiled/debug/       # Figure compilation debugging
manuscript/src/tables/compiled/debug/        # Table compilation debugging
```

### Log Files

Key log files to check for issues:

```
./.logs/compile.log                          # Main compilation log
manuscript/src/figures/compiled/debug/compile_legends.log  # Figure processing log
manuscript/src/figures/compiled/debug/toggle_figures_*.log # Figure visibility logs
```

### Examining Intermediate Files

For troubleshooting, examine these intermediate files:

1. **Original source files**: `manuscript/src/figures/src/Figure_ID_XX.tex`
2. **Generated figure files**: `manuscript/src/figures/compiled/Figure_ID_XX.tex`
3. **Debug copies**: `manuscript/src/figures/compiled/debug/Figure_ID_XX.tex.debug`
4. **Combined figure file**: `manuscript/src/figures/.tex/.All_Figures.tex`

## Troubleshooting Common Compilation Issues

### Figure Processing Issues

1. **Figures not appearing in PDF**:
   - Check if `--figs` flag was used during compilation
   - Verify image files exist in `manuscript/src/figures/src/`
   - Check that JPG versions were generated in `manuscript/src/figures/src/jpg/`
   - Examine debug logs for errors

2. **Caption formatting issues**:
   - Ensure caption files follow the correct format with `\textbf{}` for the title
   - Check for LaTeX syntax errors in captions (unmatched braces, etc.)
   - Verify that the `\smallskip` and `\\` are present between title and legend

3. **Image conversion problems**:
   - Verify that TIF files are valid and can be converted to JPG
   - Check if the conversion tool (ImageMagick's `convert`) is installed
   - Look for errors in the compilation log related to image conversion

### Table Processing Issues

1. **Tables not appearing**:
   - Check CSV file format (comma-separated, proper headers)
   - Verify caption files exist and follow the correct format
   - Look for LaTeX errors in the table content (special characters, etc.)

2. **Table formatting problems**:
   - Examine the generated LaTeX table code
   - Check for very wide tables that might exceed page width
   - Consider adjusting column widths or using landscape orientation

### LaTeX Compilation Errors

1. **Missing packages**:
   - Check LaTeX logs for missing package errors
   - Install required LaTeX packages

2. **Syntax errors**:
   - Look for errors in the LaTeX compilation logs
   - Check problematic lines in the source files

3. **Reference errors**:
   - Ensure you're using the correct reference format (`\ref{fig:XX}` or `\ref{tab:XX}`)
   - Check for warnings about undefined references

## Advanced Topics

### Customizing the Compilation Process

You can customize the compilation process by modifying these files:

- `manuscript/scripts/sh/modules/config.sh`: Contains path configurations
- `manuscript/scripts/sh/modules/process_figures.sh`: Figure processing logic
- `manuscript/scripts/sh/modules/process_tables.sh`: Table processing logic

### Creating a Custom Template

To create a custom template for figures:

1. Edit `manuscript/src/figures/templates/_Figure_ID_XX.tex`
2. For tables, edit `manuscript/src/tables/src/_Table_ID_XX.tex`

### Batch Processing Multiple Figures

For batch processing of multiple figures:

1. Place all image files in `manuscript/src/figures/src/`
2. Ensure they follow the naming convention `Figure_ID_XX_name.[tif|jpg]`
3. Run `./compile -f` to process all figures at once

## Conclusion

The SciTex compilation system automates the complex process of preparing scientific manuscripts with figures and tables. By following the guidelines in this document and the `FIGURE_TABLE_GUIDE.md`, you can effectively create, manage, and reference figures and tables in your scientific documents.