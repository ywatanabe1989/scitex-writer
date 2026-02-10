# Table Management

Tables for the manuscript. Place source files in `caption_and_media/`; compiled output is auto-generated in `compiled/`.

## Directory Structure

```
tables/
├── caption_and_media/           # YOUR FILES GO HERE
│   ├── 01_example_table.csv     # Data file
│   ├── 01_example_table.tex     # Caption file (same basename)
│   └── ...
├── compiled/                    # Auto-generated during compilation
│   ├── 01_example_table.tex     # Individual table LaTeX
│   └── FINAL.tex                # Combined output included by base.tex
└── README.md
```

## Naming Convention

### Format: `XX_description.{csv,tex}`

- `XX`: Two-digit table number (01, 02, ...)
- `_description`: Descriptive name using underscores
- Each table needs TWO files with the same basename:
  - `.csv` (or `.xlsx`) - the data
  - `.tex` - the caption

### Examples

```
01_demographic_data.csv    + 01_demographic_data.tex
02_model_performance.csv   + 02_model_performance.tex
```

Files that don't start with digits are **silently ignored** by compilation.

## Caption Template

```latex
\caption{\textbf{
Table Title Here
}
\smallskip
\\
Description of the table contents and methodology.
}
\label{tab:01_example_table}
```

The `\label{tab:XX_description}` must match the file basename.

## Referencing Tables

```latex
Table~\ref{tab:01_example_table}
```

## CSV Format

```csv
Parameter,Value,Unit
Length,10.5,cm
Width,5.2,cm
```

- Use comma as separator
- Include a header row for column names
- CSV is auto-converted to LaTeX tabular format during compilation

## Validation

Run `make check` before compilation to verify naming conventions.

<!-- EOF -->
