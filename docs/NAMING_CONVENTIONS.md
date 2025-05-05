# SciTex Naming Conventions

This document outlines the naming conventions used in the SciTex project.

## File Naming Principles

1. **Consistency**: Follow the same pattern across all files of the same type
2. **Descriptiveness**: Names should indicate the file's purpose
3. **Organization**: Names should enable proper sorting and grouping
4. **Simplicity**: Keep names as concise as possible while maintaining clarity

## Directory Structure

SciTex follows a structured directory hierarchy:

```
SciTex/
├── docs/                  # Documentation
├── manuscript/            # Main manuscript
│   ├── main/              # Compiled output
│   ├── scripts/           # Processing scripts
│   └── src/               # Source files
│       ├── figures/       # Figure sources and captions
│       └── tables/        # Table sources and captions
├── revision/              # Revision documents
└── supplementary/         # Supplementary materials
```

## Figure Naming

### Figure Files

All figure files must follow this pattern:

```
Figure_ID_XX_descriptive_name.ext
```

Where:
- `Figure_ID`: Fixed prefix (required)
- `XX`: Two-digit figure number (01, 02, etc.) (required)
- `descriptive_name`: Short, descriptive name (required)
- `.ext`: File extension: `.tif` or `.jpg` for images, `.tex` for captions

Examples:
```
Figure_ID_01_workflow.tif
Figure_ID_02_architecture.jpg
Figure_ID_03_results.tif
```

### Figure Captions

Caption files match the corresponding figure name but use the `.tex` extension:

```
Figure_ID_01_workflow.tex
Figure_ID_02_architecture.tex
Figure_ID_03_results.tex
```

### Figure Labels

In LaTeX, figure labels follow this pattern:

```latex
\label{fig:XX}
```

Where `XX` is the two-digit figure number.

Examples:
```latex
\label{fig:01}  % For Figure_ID_01_workflow
\label{fig:02}  % For Figure_ID_02_architecture
```

## Table Naming

### Table Files

All table files follow this pattern:

```
Table_ID_XX_descriptive_name.ext
```

Where:
- `Table_ID`: Fixed prefix (required)
- `XX`: Two-digit table number (01, 02, etc.) (required)
- `descriptive_name`: Short, descriptive name (required)
- `.ext`: File extension: `.csv` for data, `.tex` for captions/definition

Examples:
```
Table_ID_01_results.csv
Table_ID_02_methods.csv
Table_ID_03_parameters.csv
```

### Table Captions

Caption files match the corresponding table name with `.tex` extension:

```
Table_ID_01_results.tex
Table_ID_02_methods.tex
Table_ID_03_parameters.tex
```

### Table Labels

In LaTeX, table labels follow this pattern:

```latex
\label{tab:XX}
```

Where `XX` is the two-digit table number.

Examples:
```latex
\label{tab:01}  % For Table_ID_01_results
\label{tab:02}  % For Table_ID_02_methods
```

## Script Naming

### Shell Scripts

Shell scripts use lowercase names with hyphens:

```
compile-all.sh
process-figures.sh
generate-pdf.sh
```

### Python Scripts

Python scripts use lowercase with underscores:

```
file_utils.py
process_data.py
generate_figures.py
```

## Using Placeholders

Template files use placeholder names:

```
_Figure_ID_XX.tex   # Figure template
_Table_ID_XX.tex    # Table template
```

## Best Practices

1. **Always use the correct prefix** for figures (`Figure_ID_`) and tables (`Table_ID_`)
2. **Maintain leading zeros** in figure/table numbers (e.g., `01` not `1`)
3. **Use descriptive names** that indicate the content (e.g., `workflow` not `fig1`)
4. **Be consistent with file extensions** (`.tif` for source figures, `.tex` for captions)
5. **Match caption filenames exactly** to their corresponding image files
EOFF < /dev/null
