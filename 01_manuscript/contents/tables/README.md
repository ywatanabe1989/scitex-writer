# Table Management

Table-related files for the manuscript.

## Directory Structure

- `compiled/`: Compiled LaTeX files for each table (auto-generated)
- `contents/`: Source directory for table files
  - Place `.csv` data files here
  - Create matching `.tex` caption file with same name
  - `_.XX.tex`: Template file for table captions

## Naming Conventions

All tables must follow this naming pattern:

```
.XX_descriptive_name.[csv|tex]
```

Where:
- `Table_ID` is the fixed prefix
- `XX` is a two-digit table number (e.g., 01, 02)
- `descriptive_name` is an optional descriptive name (e.g., parameters, results)
- The extension is either `.csv` (for data files) or `.tex` (for caption files)

**Important**: The table number (`XX`) is used to generate LaTeX reference labels in the format `\label{tab:XX}`.

## Usage

### Creating a Table

1. **Prepare your table data**:
   - Create a CSV file with your table data
   - Use comma as separator
   - Include header row for column names

2. **Example CSV Format**:
   ```csv
   Parameter,Value,Unit
   Length,10.5,cm
   Width,5.2,cm
   Height,3.7,cm
   ```

3. **Add to SciTex**:
   - Place the CSV file in the `contents/` directory
   - Create a caption file with the same name but `.tex` extension
   - Use the template from `_.XX.tex`

4. **Caption Template**:
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

Where `XX` is the ID number from the table filename (e.g., `Table~\ref{tab:01}` for `.01_parameters.csv`).

## Example Structure

```
tables/
├── compiled/
│   └── .01_parameters.tex    # Auto-generated during compilation
└── contents/
    ├── .01_parameters.csv    # Data file
    ├── .01_parameters.tex    # Caption file
    └── _.XX.tex              # Template file
```

## For More Information

See the comprehensive figure and table management guide in the documentation:

```
/docs/FIGURE_TABLE_GUIDE.md
```