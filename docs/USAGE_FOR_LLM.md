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
  - `src/`: Content sections
  - `scripts/`: Automation scripts

- `revision/`: For revision responses
  - `src/`: Revision content
  - `editor/`: Editor comments and responses
  - `reviewer*/`: Reviewer comments and responses

- `supplementary/`: Supplementary materials
  - `src/`: Supplementary content
  - `figures/`: Supplementary figures
  - `tables/`: Supplementary tables

## Basic Workflow

### 1. Create Content

Edit the following files to create your manuscript:

- `manuscript/src/*.tex`: Section files (introduction, methods, etc.)
- `manuscript/src/bibliography.bib`: Bibliography file
- `manuscript/src/figures/`: Figure directories
- `manuscript/src/tables/`: Table directories

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
- `manuscript/src/figures/src/`: Place source files here with naming format `Figure_ID_XX.tif`
- `manuscript/src/figures/src/Figure_ID_XX.tex`: Caption files with matching names
- `manuscript/src/figures/compiled/`: Auto-generated compilation files
- `manuscript/src/figures/templates/`: Templates for creating new figures

### Table Organization

Tables follow a similar structure:
- `manuscript/src/tables/src/`: Place source files here with naming format `Table_ID_XX.csv`
- `manuscript/src/tables/src/Table_ID_XX.tex`: Caption files with matching names
- `manuscript/src/tables/compiled/`: Auto-generated compilation files

### Naming Conventions

All figures and tables must follow these naming conventions:
- Figures: `Figure_ID_XX.tif/tex` (e.g., `Figure_ID_01_workflow.tif`)
- Tables: `Table_ID_XX.csv/tex` (e.g., `Table_ID_01_results.csv`)

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
   Place a CSV file in `manuscript/src/tables/src/` with the naming format `Table_ID_XX.csv`

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
   - Generates JPEG versions for preview
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
./.scripts/sh/.clear_versions.sh  # Reset versioning from v001
```

Previous versions are stored in:
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

## Overview

SciTex is an AI-assisted LaTeX template for scientific manuscripts. It provides tools for manuscript preparation with integrated GPT assistance for text revision, terminology checking, and citation insertion.

## Repository Structure

```
SciTex/
├── manuscript/        # Main manuscript directory
│   ├── main.tex       # Main document entry point
│   ├── src/           # Content sections (introduction, methods, etc.)
│   ├── scripts/       # Automation scripts
│      ├── py/         # Python scripts for AI assistance
│      ├── sh/         # Bash scripts for compilation
├── revision/          # Revision response documents
├── supplementary/     # Supplementary materials
├── examples/          # Example scripts demonstrating functionality
├── docs/              # Documentation
│   ├── progress/      # Progress tracking
│   ├── structure/     # Project structure documentation
│   └── USAGE_FOR_LLM.md  # This file
```

## Core Functionality

SciTex combines LaTeX document preparation with AI assistance through:

1. **Document Framework**: Modular LaTeX template following Elsevier guidelines
2. **AI Integration**: GPT-powered tools for text improvement
3. **Automated Compilation**: Shell scripts to assemble the final PDF

## Using SciTex

### Basic Compilation

```bash
./compile               # Compile manuscript
./compile -h            # Show help
```

### AI-Assisted Features

```bash
./compile -r            # Revise with GPT
./compile -t            # Check terminology
./compile -c            # Insert citations
```

### Additional Tools

```bash
./compile -p2t          # Convert PowerPoint to TIF
./compile -nf           # Compile without figures
./compile -p            # Push changes to GitHub
```

## Python Module Usage

The refactored Python modules can be used directly:

```python
# Text revision
from revise import revise_by_GPT
revise_by_GPT("path/to/file.tex")

# Terminology checking
from check_terms import check_terms_by_GPT
check_terms_by_GPT("path/to/file.tex")

# Citation insertion
from insert_citations import insert_citations
insert_citations("path/to/file.tex", "path/to/bibliography.bib")
```

## CLI Usage

The unified command-line interface:

```bash
# Revise text
python scitex.py revise --input path/to/file.tex

# Check terminology
python scitex.py check-terms --input path/to/file.tex

# Insert citations
python scitex.py insert-citations --input path/to/file.tex --bibliography path/to/bib.bib
```

## Common Tasks

### Creating a New Manuscript

1. Edit content in `manuscript/src/` files (abstract.tex, introduction.tex, etc.)
2. Add references to `manuscript/src/bibliography.bib`
3. Run `./compile` to generate the PDF

### Revising Content

1. Make changes to the relevant section files
2. Use `./compile -r` to apply AI revision
3. Review changes and adjust as needed

### Adding Figures

1. Place PowerPoint slides in designated directory
2. Run `./compile -p2t` to convert to TIF format
3. Edit figure captions in the corresponding TeX files

### Preparing for Submission

1. Finalize all content and run `./compile`
2. Check the generated PDF for errors
3. Submit the final PDF along with source files if requested

## LLM Agent Integration Tips

For LLM agents interacting with SciTex:

1. **Document Analysis**: Begin by examining the structure in manuscript/src/
2. **Content Creation**: Generate content for specific sections (introduction, methods, etc.)
3. **AI Assistance**: Use the built-in GPT tools for polishing content
4. **Check References**: Ensure bibliography.bib contains all necessary citations

## Common Errors and Solutions

1. **Compilation Failures**: Check LaTeX syntax in recently edited files
2. **Missing References**: Ensure citations match entries in bibliography.bib
3. **Figure Issues**: Verify figure paths and format compatibility
4. **AI Integration Errors**: Check API key setup in environment variables

## Examples

SciTex includes various examples to help you understand its functionality:

### Basic Examples

- `examples/basic_revision.py`: Demonstrates basic text revision using GPT
- `examples/check_terms.py`: Shows how to check terminology consistency
- `examples/insert_citations.py`: Illustrates citation insertion from a bibliography

### Complete Workflow Example

- `examples/complete_workflow.sh`: A comprehensive bash script demonstrating the full manuscript preparation workflow

### Python API Example

- `examples/using_python_api.py`: Demonstrates how to use the SciTex Python API programmatically

To run these examples:

```bash
# For Python examples
python examples/basic_revision.py

# For shell script examples
bash examples/complete_workflow.sh
```

These examples serve as both documentation and functional tests of the SciTex system. Refer to them when implementing your own workflows or when you need to understand how specific features work.

<!-- EOF -->