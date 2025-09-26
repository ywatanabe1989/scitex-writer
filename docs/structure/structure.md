# SciTex Project Structure

This document explains the structure of the SciTex project, an AI-assisted LaTeX template for scientific manuscripts. Last updated on 2025-05-05.

![SciTex Project Structure](./structure.png)

## Overview

The SciTex project is organized into several main components:

1. **Manuscript** - The main scientific paper
2. **Revision** - Tools and templates for handling reviewer feedback
3. **Supplementary** - Additional materials to accompany the main manuscript
4. **Scripts** - Root level scripts for various compilation tasks
5. **Examples** - Example usage of SciTex functionality
6. **Tests** - Testing infrastructure
7. **Documentation** - Project documentation and guidelines

## Manuscript Component

The manuscript component is the core of the project and contains:

- **main.tex** - The primary LaTeX file that combines all sections
- **src/** - Contains all the content sections, figures, tables, and latex_styles
  - **LaTeX files** - Main content files
    - introduction.tex - Introduction section
    - methods.tex - Methods section
    - results.tex - Results section
    - discussion.tex - Discussion section
    - abstract.tex - Abstract section
    - bibliography.bib - Bibliography file
  - **figures/** - Directory for figures and their templates
    - src/ - Source figure files (tif and tex caption files)
    - compiled/ - Compiled figure files ready for inclusion
    - templates/ - Templates for creating new figures
  - **tables/** - Directory for tables
    - src/ - Source CSV and caption files
    - compiled/ - Compiled table files
  - **latex_styles/** - Contains formatting and styling LaTeX files
- **scripts/** - Automation tools
  - Python scripts for AI-assisted tasks
  - Shell scripts for compilation and general automation

### Python Scripts

The Python scripts provide AI-assisted manuscript preparation:

- **scitex.py** - Main entry point for Python functionality
- **revise.py** - Handles AI-powered text revision
- **insert_citations.py** - Manages citation insertion assistance
- **check_terms.py** - Ensures terminology consistency
- **gpt_client.py** - Interface with OpenAI's GPT models
- **file_utils.py** - Utilities for file operations
- **config.py** - Configuration and settings
- **prompt_loader.py** - Loads templates for prompts
- **crop_tif.py** - Crops TIF images for figures
- **templates/** - Prompt template files for AI interactions
- **tests/** - Testing infrastructure
  - unit/ - Unit tests
  - integration/ - Integration tests
  - fixtures/ - Test data and fixtures

### Shell Scripts

The shell scripts automate the compilation and manuscript preparation:

- **compile.sh** - Main entry point for compilation
- **revise.sh** - Triggers AI-powered revision
- **insert_citations.sh** - Helps with citation insertion
- **run_tests.sh** - Runs test suite
- **modules/** - Modular scripts for specific tasks
  - config.sh - Configuration settings
  - compile_main_tex.sh - LaTeX compilation
  - check_terms.sh - Term consistency checking
  - process_figures.sh - Figure processing pipeline
  - process_tables.sh - Table processing pipeline
  - pptx2tif.sh - Converting PowerPoint to TIF
  - custom_tree.sh - Generates directory tree
  - versioning.sh - Handles version management

## Revision Component

The revision component helps manage the peer review process:

- **main.tex** - Main LaTeX file for the revision response
- **src/** - Source files for revision 
  - **reviewer1/**, **reviewer2/** - Directories for each reviewer
    - comments.tex - Reviewer comments
    - response.tex - Author responses
    - revision.tex - Description of revisions made
  - **editor/** - Editor-specific communications
  - **commands.tex** - LaTeX commands for revision

## Supplementary Component

The supplementary component contains additional materials:

- **main.tex** - Main LaTeX file for supplementary materials
- **src/** - Source files for supplementary content
  - LaTeX source files
  - figures/ - Supplementary figures
  - tables/ - Supplementary tables

## Root Scripts

The root scripts provide easy entry points for different tasks:

- **compile-all.sh** - Compile manuscript, revision, and supplementary
- **compile-manuscript.sh** - Compile only the manuscript
- **compile-revision.sh** - Compile only the revision
- **compile-supplementary.sh** - Compile only the supplementary
- **run_tests.sh** - Run test suite

## Documentation

The docs directory contains project documentation:

- **progress/** - Progress tracking
  - progress.md - Text description of progress
  - progress.mmd - Mermaid diagram source
  - progress.png - Rendered progress diagram
- **structure/** - Project structure documentation
  - structure.md - This document
  - structure.mmd - Mermaid diagram source
  - structure.png - Rendered structure diagram
- **USAGE_FOR_LLM.md** - Guide for LLM agents to use the project
- **PLAN.md** - Project roadmap, goals, and milestones
- **TO_CLAUDE.md** - Instructions for Claude AI assistance

## Examples

The examples directory contains sample usage of SciTex functionality:

- **README.md** - Overview of examples
- **basic_revision.py** - Demonstrates using GPT for text revision
- **check_terms.py** - Shows how to check terminology consistency
- **insert_citations.py** - Illustrates citation insertion
- **complete_workflow.sh** - A full workflow example
- **using_python_api.py** - How to use the SciTex Python API

## Tests

The tests directory contains the project test suite:

- **README.md** - Testing documentation
- **conftest.py** - pytest configuration
- **pytest.ini** - pytest settings
- **sync_tests_with_source.sh** - Keeps tests in sync with source code

## Data Flow

The SciTex project follows a clear data flow for manuscript preparation:

1. **Content Creation** - Authors write content in src/*.tex files
2. **Figure Preparation** - Figures are prepared and placed in src/figures/src/
3. **Table Preparation** - Tables are prepared and placed in src/tables/src/
4. **AI Assistance** - GPT models help with revision, term checking, and citations
5. **Compilation** - Shell scripts compile everything into final PDF
6. **Version Management** - Changes are tracked and versioned
7. **Revision Process** - Reviewer feedback is managed through the revision component

This modular structure allows for easy maintenance, extension, and collaboration on scientific manuscripts.