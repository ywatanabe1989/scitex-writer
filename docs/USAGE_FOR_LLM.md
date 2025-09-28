<!-- ---
!-- Timestamp: 2025-05-05 11:51:33
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/SciTex/docs/USAGE_FOR_LLM.md
!-- --- -->

# SciTex Usage Guide

This document provides comprehensive instructions for using SciTex, an AI-assisted LaTeX template for scientific manuscripts.

## Table of Contents

1. [Installation](#installation)
2. [Project Structure](#project-structure)
3. [Basic Workflow](#basic-workflow)
4. [AI-Assisted Features](#ai-assisted-features)
5. [Figure and Table Handling](#figure-and-table-handling)
6. [Version Management](#version-management)
7. [Python API](#python-api)
8. [For LLM Agents](#for-llm-agents)
9. [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites

- LaTeX distribution (e.g., TexLive)
- Python 3.8+
- Git

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/ywatanabe1989/SciTex.git
   cd SciTex
   ```

2. Install LaTeX dependencies:
   ```bash
   ./manuscript/scripts/sh/install_on_ubuntu.sh
   ```

3. Set up the Python environment:
   ```bash
   ./manuscript/scripts/sh/gen_pyenv.sh
   # OR
   ./python_init_with_local_mngs.sh
   ```

4. Set your OpenAI API key:
   ```bash
   echo 'export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"' >> ~/.bashrc
   source ~/.bashrc
   ```

## Project Structure

SciTex is organized into three main components:

- `manuscript/`: Main manuscript directory
  - `main.tex`: Main document entry point
  - `contents/`: Content sections
  - `scripts/`: Automation scripts

- `revision/`: For revision responses
  - `contents/`: Revision content
  - `editor/`: Editor comments and responses
  - `reviewer*/`: Reviewer comments and responses

- `supplementary/`: Supplementary materials
  - `contents/`: Supplementary content
  - `figures/`: Supplementary figures
  - `tables/`: Supplementary tables

## Basic Workflow

### 1. Create Content

Edit the following files to create your manuscript:

- `manuscript/contents/*.tex`: Section files (introduction, methods, etc.)
- `manuscript/contents/bibliography.bib`: Bibliography file
- `manuscript/contents/figures/`: Figure directories
- `manuscript/contents/tables/`: Table directories

### 2. Compile the Document

```bash
cd manuscript
./compile
```

This will generate:
- `main/manuscript.pdf`: The final PDF
- `main/manuscript.tex`: The compiled LaTeX source
- `main/diff.tex`: A diff file showing changes

### 3. Preview and Iterate

Open the PDF, review, make changes, and repeat the compilation process until satisfied.

## AI-Assisted Features

SciTex includes several AI-powered features:

### Text Revision

```bash
./compile -r
```

This will:
1. Send your text to GPT
2. Receive revised text with improved grammar and style
3. Save the changes to your files

### Citation Insertion

```bash
./compile -c
```

This will:
1. Analyze your text and bibliography
2. Insert appropriate citations
3. Save the changes to your files

### Terminology Checking

```bash
./compile -t
```

This will:
1. Check your text for consistent terminology and abbreviations
2. Report any inconsistencies

## Figure and Table Handling

SciTex provides a comprehensive system for managing figures and tables in scientific manuscripts, handling conversion, compilation, and reference management automatically.

### Figure Organization

Figures follow a specific organizational structure:
- `manuscript/contents/figures/contents/`: Place source files here with naming format `.XX.tif`
- `manuscript/contents/figures/contents/.XX.tex`: Caption files with matching names
- `manuscript/contents/figures/compiled/`: Auto-generated compilation files
- `manuscript/contents/figures/templates/`: Templates for creating new figures

### Table Organization

Tables follow a similar structure:
- `manuscript/contents/tables/contents/`: Place source files here with naming format `.XX.csv`
- `manuscript/contents/tables/contents/.XX.tex`: Caption files with matching names
- `manuscript/contents/tables/compiled/`: Auto-generated compilation files

### Naming Conventions

All figures and tables must follow these naming conventions:
- Figures: `.XX.tif/tex` (e.g., `.01_workflow.tif`)
- Tables: `.XX.csv/tex` (e.g., `.01_results.csv`)

The ID number in the filename is used for LaTeX reference labels, automatically generating `\label{fig:XX}` or `\label{tab:XX}`.

### Creating Figures

1. **From PowerPoint**:
   ```bash
   ./compile -p2t
   ```
   This converts PowerPoint slides to TIF format for inclusion in the manuscript.

2. **Figure Caption Template**:
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

3. **Manual Figure Processing**:
   ```bash
   # Crop TIF images
   python manuscript/scripts/py/crop_tif.py -i /path/to/figure.tif -o /path/to/output.tif
   
   # Convert PowerPoint slides in a directory
   ./manuscript/scripts/sh/modules/pptx2tif_all.sh /path/to/pptx/directory
   ```

### Creating Tables

1. **Create CSV File**:
   Place a CSV file in `manuscript/contents/tables/contents/` with the naming format `.XX.csv`

2. **Create Caption File**:
   Create a corresponding `.tex` file with the same name containing:
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

### Referencing in Text

Reference figures and tables in your text using:
- Figures: `Figure~\ref{fig:XX}` (e.g., `Figure~\ref{fig:01}`)
- Tables: `Table~\ref{tab:XX}` (e.g., `Table~\ref{tab:01}`)

For specific parts of multi-panel figures, use:
- `Figure~\ref{fig:XX}A` or `Figure~\ref{fig:XX}(i)`

### Compilation Process

During manuscript compilation:

1. The system automatically:
   - Converts figures to appropriate formats
   - Generates JPEG archive for preview
   - Compiles figure and table captions
   - Creates LaTeX inclusion code
   - Adds proper references and labels

2. The compiled manuscript includes:
   - All properly formatted figures with captions
   - All tables with proper styling and captions
   - Cross-references resolved correctly

3. Disable figures during development:
   ```bash
   ./compile -nf  # Compile without including figures
   ```

## Version Management

SciTex includes a versioning system:

```bash
./.scripts/sh/.clear_archive.sh  # Reset versioning from v001
```

Previous archive are stored in:
- `manuscript/main/old/`

## Python API

You can use the SciTex Python API directly:

```python
from manuscript.scripts.py.gpt_client import GPTClient
from manuscript.scripts.py.file_utils import load_tex, save_tex
from manuscript.scripts.py.prompt_loader import load_prompt

# Initialize GPT client
client = GPTClient()

# Load TeX file and prompt
tex_content = load_tex("path/to/file.tex")
prompt = load_prompt("revise")

# Revise the text
revised_text = client(prompt + tex_content)

# Save the revised text
save_tex(revised_text, "path/to/output.tex")
```

## For LLM Agents

This section provides information for LLM agents working with the SciTex codebase.

### Key Components

1. **Core Modules**:
   - `gpt_client.py`: Handles interactions with OpenAI's GPT models
   - `file_utils.py`: Provides file operations for TeX files
   - `prompt_loader.py`: Manages prompt templates
   - `config.py`: Centralizes settings and constants

2. **Main Scripts**:
   - `revise.py`: Revises TeX files for grammar and style
   - `check_terms.py`: Checks terminology consistency
   - `insert_citations.py`: Inserts citations from bibliography
   - `scitex.py`: Unified CLI for all operations

3. **Testing**:
   - Unit tests in `tests/unit/`
   - Integration tests in `tests/integration/`
   - Test fixtures in `tests/fixtures/`

### Common Operations

1. **Text Revision**:
   ```python
   from revise import revise_by_GPT
   revise_by_GPT("path/to/file.tex")
   ```

2. **Citation Insertion**:
   ```python
   from insert_citations import insert_citations
   insert_citations("path/to/file.tex", "path/to/bibliography.bib")
   ```

3. **Terminology Checking**:
   ```python
   from check_terms import check_terms_by_GPT
   check_terms_by_GPT("path/to/file.tex")
   ```

### Guidelines for LLM Agents

1. **File Structure**: Maintain the modular organization of content
2. **LaTeX Conventions**: Follow standard scientific LaTeX conventions
3. **Citation Handling**: Use `\cite{}` for references
4. **Error Handling**: Handle file not found and OpenAI API errors
5. **Versioning**: Preserve versioning information in the output

## Troubleshooting

### Common Issues

1. **Compilation Errors**:
   - Check LaTeX syntax in recently edited files
   - Verify that all referenced figures exist

2. **API Key Issues**:
   - Ensure your OpenAI API key is correctly set
   - Check for rate limiting or quota issues

3. **Figure Conversion**:
   - Install required dependencies for image conversion
   - Check file permissions for PowerPoint files

### Getting Help

If you encounter issues:
1. Check the documentation in the `docs/` directory
2. Run with verbose output: `./compile -v`
3. Contact support at ywatanabe@alumni.u-tokyo.ac.jp

# SciTex Usage Guide for LLM Agents

This comprehensive guide is designed specifically for LLM agents working with the SciTex scientific manuscript system. It provides detailed information about the repository structure, key workflows, and important conventions.

## Table of Contents

1. [Repository Overview](#repository-overview)
2. [Key Components](#key-components)
3. [Compilation Workflow](#compilation-workflow)
4. [Figure and Table Management](#figure-and-table-management)
5. [AI-Assisted Features](#ai-assisted-features)
6. [LaTeX Conventions](#latex-conventions)
7. [Common Operations](#common-operations)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)

## Repository Overview

SciTex is a LaTeX-based system for scientific manuscript preparation with AI assistance. It follows Elsevier's guidelines but can be adapted for other journals. The repository is organized into these main components:

```
SciTex/
├── manuscript/      # Main scientific manuscript
├── revision/        # Revision response documents
├── supplementary/   # Supplementary materials
├── examples/        # Example usage
├── docs/            # Documentation
├── scripts/         # Build/automation scripts
└── tests/           # Test suite
```

## Key Components

### Manuscript Component

The `manuscript/` directory contains the core scientific manuscript files:

```
manuscript/
├── main.tex         # Main LaTeX entry point
├── compile          # Compilation script
├── scripts/         # Processing scripts
│   ├── py/          # Python utilities
│   └── sh/          # Shell scripts
└── contents/             # Content source files
    ├── abstract.tex
    ├── introduction.tex
    ├── methods.tex
    ├── results.tex
    ├── discussion.tex
    ├── bibliography.bib
    ├── figures/     # Figure files
    └── tables/      # Table files
```

### Revision Component

The `revision/` directory contains materials for responding to reviewer comments:

```
revision/
├── main.tex         # Main revision document
├── compile          # Compilation script
└── contents/             # Response content
    ├── reviewer1/   # Responses to reviewer 1
    ├── reviewer2/   # Responses to reviewer 2
    └── editor/      # Responses to editor
```

### Supplementary Component

The `supplementary/` directory contains supplementary materials:

```
supplementary/
├── main.tex         # Main supplementary document
├── compile          # Compilation script
└── contents/             # Supplementary content
    ├── methods.tex
    ├── results.tex
    ├── figures/     # Supplementary figures
    └── tables/      # Supplementary tables
```

## Compilation Workflow

SciTex uses a sophisticated compilation process that handles figures, tables, and references automatically.

### Basic Compilation

From the root directory:

```bash
# Compile manuscript only
./compile.sh -m

# Compile manuscript with figures
./compile.sh -m --figs

# Compile all components
./compile.sh
```

From component directories:

```bash
# Navigate to component directory
cd manuscript

# Basic compilation
./compile

# With figures
./compile -f
```

### Compilation Steps

The compilation process performs these steps:

1. **Initial Checks**: Validate directory structure and dependencies
2. **Figure Processing**: Convert and prepare figures (if enabled)
3. **Table Processing**: Format tables from CSV data
4. **TeX Files Gathering**: Combine separate TeX files
5. **LaTeX Compilation**: Generate PDF output
6. **Diff Generation**: Create diff version showing changes
7. **Cleanup**: Remove temporary files
8. **Versioning**: Create versioned backup

### Important Flags

When using compilation scripts, these flags control behavior:

- `-f, --figs`: Include figures (slower compilation)
- `-r, --revise`: Enable AI-assisted text revision
- `-t, --terms`: Check terminology consistency
- `-c, --citations`: Insert citations automatically
- `-p2t, --pptx2tif`: Convert PowerPoint to TIF
- `-p, --push`: Push changes to GitHub

## Figure and Table Management

SciTex provides a standardized system for managing figures and tables.

### Figure Directory Structure

```
manuscript/contents/figures/
├── compiled/           # Auto-generated LaTeX files (DO NOT EDIT)
├── contents/                # Source files (PLACE YOUR FILES HERE)
│   ├── .XX.tif  # Source image files
│   ├── .XX.tex  # Caption files
│   └── jpg/              # Auto-generated JPEG archive
├── templates/          # Templates for new figures
└── .tex/               # Hidden directory for compiled figure files
```

### Figure Naming Conventions

All figures must follow this pattern:
```
.XX_descriptive_name.ext
```

Where:
- `Figure_ID`: Fixed prefix (required)
- `XX`: Two-digit figure number (01, 02, etc.) (required)
- `descriptive_name`: Short, descriptive name (required)
- `.ext`: File extension: `.tif` for images or `.tex` for captions

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

All tables must follow this pattern:
```
.XX_descriptive_name.ext
```

Where:
- `Table_ID`: Fixed prefix (required)
- `XX`: Two-digit table number (01, 02, etc.) (required)
- `descriptive_name`: Short, descriptive name (required)
- `.ext`: File extension: `.csv` for data or `.tex` for captions

### Referencing Figures and Tables

In LaTeX files, use these reference formats:

```latex
Figure~\ref{fig:XX}   % For figures (e.g., Figure~\ref{fig:01})
Table~\ref{tab:XX}    % For tables (e.g., Table~\ref{tab:01})
```

For more details, see the [Figure and Table Guide](./FIGURE_TABLE_GUIDE.md) and [Naming Conventions](./NAMING_CONVENTIONS.md).

## AI-Assisted Features

SciTex integrates AI assistance through Python scripts that use OpenAI's GPT models.

### Text Revision

Automatically revise text for clarity, grammar, and style:

```bash
# From manuscript directory
./compile -r

# Or from root
./compile.sh -m --revise
```

The process reads LaTeX files, identifies text blocks, submits them to GPT for revision, and updates the files with improved text.

### Terminology Checking

Check for consistent terminology and abbreviations:

```bash
# From manuscript directory
./compile -t

# Or from root
./compile.sh -m --terms
```

The process scans the manuscript for inconsistent terminology and abbreviations, providing a report and suggestions.

### Citation Management

Automatically insert appropriate citations:

```bash
# From manuscript directory
./compile -c

# Or from root
./compile.sh -m --cite
```

The process identifies statements that need citation, searches the bibliography for relevant references, and inserts proper citation commands.

## LaTeX Conventions

SciTex uses specific LaTeX conventions to ensure consistent formatting.

### Document Structure

- `\documentclass{elsarticle}`: Base class for manuscript
- Two-column layout with standard academic formatting
- Section structure: Introduction, Methods, Results, Discussion
- References using BibTeX and natbib

### Label Conventions

- Sections: `\label{sec:name}` (e.g., `\label{sec:methods}`)
- Figures: `\label{fig:XX}` (e.g., `\label{fig:01}`)
- Tables: `\label{tab:XX}` (e.g., `\label{tab:01}`)
- Equations: `\label{eq:name}` (e.g., `\label{eq:energy}`)

### Citation Conventions

- Standard citation: `\cite{author_year}`
- Parenthetical citation: `\citep{author_year}`
- Textual citation: `\citet{author_year}`

## Common Operations

### Adding a New Figure

1. Create your figure in TIF format (300 DPI recommended)
2. Name it following the convention: `.XX_description.tif`
3. Place it in `manuscript/contents/figures/contents/`
4. Create a caption file with the same name but `.tex` extension
5. Reference it in text with `Figure~\ref{fig:XX}`
6. Compile with the `-f` or `--figs` flag

### Adding a New Table

1. Create your table data in CSV format
2. Name it following the convention: `.XX_description.csv`
3. Place it in `manuscript/contents/tables/contents/`
4. Create a caption file with the same name but `.tex` extension
5. Reference it in text with `Table~\ref{tab:XX}`
6. Compile the document

### Updating Bibliography

1. Edit the `manuscript/contents/bibliography.bib` file
2. Add new entries following BibTeX format:
   ```bibtex
   @article{author_year,
     author  = {Author, A. and Another, B.},
     title   = {Title of the article},
     journal = {Journal Name},
     volume  = {42},
     number  = {3},
     pages   = {123--456},
     year    = {2022},
     doi     = {10.xxxx/xxxxx}
   }
   ```
3. Reference citations in text using `\cite{author_year}`
4. Compile the document to update references

### Running Tests

The test suite can be executed to verify system functionality:

```bash
# Run all tests
./run_tests.sh

# Run with verbose output
./run_tests.sh -v

# Run specific tests
./run_tests.sh -p test_file_utils.py
```

## Troubleshooting

### Common Issues

1. **Figures Not Appearing**:
   - Check naming follows convention exactly
   - Ensure files are in the correct directories
   - Verify compilation uses the `-f` flag

2. **References Not Resolving**:
   - Check label formats match the conventions
   - Run multiple LaTeX passes to resolve references
   - Verify reference commands use correct IDs

3. **Python Script Errors**:
   - Ensure OpenAI API key is properly set
   - Check Python dependencies are installed
   - Verify file permissions allow script execution

### Debugging Compilation

For detailed debugging information:

```bash
# Enable verbose compilation
./compile -v

# Check LaTeX logs
cat manuscript/main.log

# Check script logs
cat manuscript/.logs/compile.log
```

## Best Practices

1. **Consistent Naming**: Follow naming conventions exactly
2. **Regular Compilation**: Compile frequently to catch issues early
3. **Version Control**: Use git for tracking changes
4. **Backup Original Files**: Keep copies of important originals
5. **Modular Editing**: Work on one section at a time
6. **Comment Code**: Add helpful LaTeX comments
7. **Use Templates**: Start from provided templates
8. **Test References**: Verify all cross-references work
9. **Organize Figures**: Keep figures in appropriate directories
10. **Follow Documentation**: Refer to guides for specific tasks

For LLM agents in particular:
1. **Preserve Structure**: Maintain the existing directory structure
2. **Follow Conventions**: Adhere to naming and reference patterns
3. **Use Appropriate Commands**: Use the right LaTeX commands for different elements
4. **Understand the Workflow**: Know how compilation processes figures and tables
5. **Check Reference Formats**: Ensure cross-references use correct label formats

## Examples

SciTex includes various examples to help you understand its functionality:

### Basic Examples

- `examples/basic_revision.py`: Demonstrates text revision using GPT
- `examples/check_terms.py`: Shows terminology consistency checking
- `examples/insert_citations.py`: Illustrates citation insertion

### Complete Workflow Example

- `examples/complete_workflow.sh`: End-to-end manuscript preparation workflow

### Python API Example

- `examples/using_python_api.py`: Programmatic use of the SciTex Python API

For more detailed information, refer to the other documentation files in the `docs/` directory.

<!-- EOF -->