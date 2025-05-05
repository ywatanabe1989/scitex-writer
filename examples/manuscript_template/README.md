# Example Manuscript Template

This directory contains a self-descriptive example manuscript to demonstrate how to use SciTex effectively. You can use this template as a starting point for your own scientific manuscripts.

## Directory Structure

```
manuscript_template/
├── README.md              # This file
├── compile.sh             # Compilation script
├── main.tex               # Main LaTeX file
├── src/                   # Content sections
│   ├── abstract.tex       # Abstract section
│   ├── bibliography.bib   # Bibliography file
│   ├── commands.tex       # Custom LaTeX commands
│   ├── conclusion.tex     # Conclusion section
│   ├── discussion.tex     # Discussion section
│   ├── figures/           # Figures directory
│   │   ├── README.md      # Figure management guide
│   │   ├── compiled/      # Auto-generated files (DO NOT EDIT)
│   │   ├── src/           # Figure source files
│   │   │   ├── Figure_ID_01_workflow.tex       # Example figure caption
│   │   │   ├── Figure_ID_02_architecture.tex   # Example figure caption
│   │   │   └── ...
│   │   └── templates/     # Figure templates
│   │       └── _Figure_ID_XX.tex               # Figure template
│   ├── introduction.tex   # Introduction section
│   ├── methods.tex        # Methods section
│   ├── results.tex        # Results section
│   ├── styles/            # Style definitions
│   │   ├── formatting.tex # Formatting settings
│   │   └── packages.tex   # Package imports
│   └── tables/            # Tables directory
│       ├── README.md      # Table management guide
│       ├── src/           # Table source files
│       │   ├── Table_ID_01_prompts.tex         # Example table caption
│       │   ├── Table_ID_01_prompts.csv         # Example table data
│       │   ├── Table_ID_02_performance.tex     # Example table caption
│       │   ├── Table_ID_02_performance.csv     # Example table data
│       │   └── _Table_ID_XX.tex                # Table template
│       └── ...
└── ...
```

## Quick Start

1. Copy this directory to your project location
2. Edit the content files in the `src/` directory
3. Add your figures and tables
4. Run the compilation script:

```bash
# Without figures (faster for drafts)
./compile.sh

# With figures included
./compile.sh --figs

# With PowerPoint to TIF conversion and figures
./compile.sh --pptx2tif --figs
```

## Figure Management

### Adding Figures

1. Create your figure image file (TIF or JPG format, 300 DPI recommended)
2. Name it following the pattern: `Figure_ID_XX_descriptive_name.tif` 
   - Example: `Figure_ID_03_results.tif`
3. Place it in `src/figures/src/`
4. Create a caption file with the same base name but .tex extension
   - Example: `Figure_ID_03_results.tex`
5. Use the `_Figure_ID_XX.tex` template as a guide for your caption

### Referencing Figures

In your LaTeX text files (introduction.tex, methods.tex, etc.), reference figures using:

```latex
Figure~\ref{fig:XX} shows the results of our analysis.
```

Where XX is the figure number from your filename.

## Table Management

### Adding Tables

1. Create your table data as a CSV file with comma separators
2. Name it following the pattern: `Table_ID_XX_descriptive_name.csv`
   - Example: `Table_ID_03_statistics.csv`
3. Place it in `src/tables/src/`
4. Create a caption file with the same base name but .tex extension
   - Example: `Table_ID_03_statistics.tex`
5. Use the `_Table_ID_XX.tex` template as a guide for your caption

### Referencing Tables

In your LaTeX text files, reference tables using:

```latex
Table~\ref{tab:XX} presents the statistical analysis.
```

Where XX is the table number from your filename.

## Content Organization

### Main Sections

The manuscript is organized into standard scientific sections:

- **Abstract**: A concise summary of the paper
- **Introduction**: Background and motivation for the research
- **Methods**: Approach and techniques used
- **Results**: Findings and observations
- **Discussion**: Interpretation and implications
- **Conclusion**: Final remarks and future work

### Special Features Demonstrated

1. **Figure Handling**:
   - Converting PowerPoint to TIF
   - Creating figure captions
   - Multi-panel figure organization
   - Figure referencing
   - TikZ vector-based figures

2. **Table Handling**:
   - CSV-based table creation
   - Table captions and formatting
   - Table referencing

3. **AI-Assisted Writing**:
   - GPT-based text revision
   - Terminology checking
   - Citation insertion

4. **LaTeX Features**:
   - Document sectioning
   - Mathematical equations
   - Cross-referencing
   - Custom commands

## Example Usage

### Figure Example

**Figure File**: `src/figures/src/Figure_ID_01_workflow.tif`

**Caption File**: `src/figures/src/Figure_ID_01_workflow.tex`
```latex
\caption{\textbf{
SciTex workflow diagram.
}
\smallskip
\\
The figure illustrates the key components and workflow of the SciTex system, 
including manuscript preparation, AI-assisted revision, figure processing,
citation management, and LaTeX compilation to create the final document.
}
% width=0.9\textwidth
```

**Reference in Text**: (in `src/introduction.tex`)
```latex
As shown in Figure~\ref{fig:01}, the SciTex system provides an integrated 
workflow for manuscript preparation and compilation.
```

### Table Example

**Data File**: `src/tables/src/Table_ID_01_prompts.csv`
```csv
Prompt Type,Description,Success Rate (%)
Term Check,Identifies inconsistent terminology,92.5
Citation,Suggests relevant citations,87.3
Revision,General text improvement,94.1
```

**Caption File**: `src/tables/src/Table_ID_01_prompts.tex`
```latex
\caption{\textbf{
SciTex AI Prompts and Their Performance
}
\smallskip
\\
This table shows the different types of AI prompts used in the SciTex system, 
their primary functions, and their success rates as measured by user acceptance 
of suggested changes in a sample of 100 manuscripts.
}
% width=0.8\textwidth
```

**Reference in Text**: (in `src/methods.tex`)
```latex
Table~\ref{tab:01} summarizes the AI prompt types used in SciTex and their 
respective performance metrics.
```

## Customization

This template can be customized for different journal requirements:

- Edit styles in the `src/styles/` directory
- Adjust formatting parameters in the `main.tex` file
- Modify section structure as needed

## Tips and Best Practices

1. Keep figure filenames consistent with their ID numbers
2. Use descriptive names for both figures and tables
3. Provide detailed captions that can stand alone
4. Always reference figures and tables in the text
5. Compile frequently to check for errors
6. Use the debug files in compiled/debug/ for troubleshooting

## Common Issues

- **Missing figures in output**: Ensure you used the `--figs` flag when compiling
- **Figure caption formatting issues**: Verify your caption files follow the template structure
- **Reference errors**: Check that figure/table numbers match between filenames and references
- **Table formatting problems**: Ensure CSV files use comma separators and have consistent columns

## Further Help

For more detailed information:

- See the main [SciTex documentation](../../docs/)
- Refer to the [Figure and Table Guide](../../docs/FIGURE_TABLE_GUIDE.md)
- Check the [Compilation Guide](../../docs/COMPILATION_GUIDE.md)