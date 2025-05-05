# Tables Directory

This directory contains all table-related files for your manuscript.

## Directory Structure

- `src/`: Place your source table files and caption files here
  - Data files: `Table_ID_XX_descriptive_name.csv`
  - Caption files: `Table_ID_XX_descriptive_name.tex`
  - Template: `_Table_ID_XX.tex`
- `compiled/`: Auto-generated files for LaTeX inclusion

## How to Add a Table

1. **Prepare your table data**:
   - Create a CSV file with your table data
   - Name it using the convention: `Table_ID_XX_descriptive_name.csv`
     (e.g., `Table_ID_01_results.csv`)
   - Use comma as the column separator
   - Include headers in the first row

2. **Create a caption file**:
   - Copy the template `src/_Table_ID_XX.tex`
   - Rename it to match your table data file (with .tex extension)
   - Fill in the title and description

## Table Naming Convention

```
Table_ID_XX_descriptive_name.[csv|tex]
```

Where:
- `Table_ID` is the fixed prefix
- `XX` is a two-digit table number (e.g., 01, 02)
- `descriptive_name` is an optional descriptive name (e.g., results, parameters)
- The extension is either `.csv` (for data files) or `.tex` (for caption files)

The table number (`XX`) will be used to generate the LaTeX label: `\label{tab:XX}`

## CSV Format

For best results, format your CSV file like this:

```csv
Header 1,Header 2,Header 3
Value 1,Value 2,Value 3
Value 4,Value 5,Value 6
```

Notes:
- First row must contain column headers
- Use comma as the separator
- Wrap values containing commas in quotes: `"Value, with comma"`
- For best alignment of numeric values, ensure consistent decimal places

## Referencing Tables

In your manuscript text, reference tables using:

```latex
\tabref{01}  % Custom command: Table~\ref{tab:01}
```

## Table Width

You can adjust the table width in the caption file:

```
% width=0.8\textwidth
```

Use values between 0.5 and 1.0 for typical tables.