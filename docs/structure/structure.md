# SciTex Project Structure

This document explains the structure of the SciTex project, an AI-assisted LaTeX template for scientific manuscripts.

![SciTex Project Structure](./structure.png)

## Overview

The SciTex project is organized into three main components:

1. **Manuscript** - The main scientific paper
2. **Revision** - Tools and templates for handling reviewer feedback
3. **Supplementary** - Additional materials to accompany the main manuscript

Each component has a similar structure with LaTeX files, source content, and scripts for automation.

## Manuscript Component

The manuscript component is the core of the project and contains:

- **main.tex** - The primary LaTeX file that combines all sections
- **src/** - Contains all the content sections, figures, tables, and styles
  - LaTeX source files (abstract.tex, introduction.tex, methods.tex, etc.)
  - figures/ - Directory for figures and their templates
  - tables/ - Directory for tables
  - styles/ - Contains formatting and styling LaTeX files
- **scripts/** - Automation tools
  - Python scripts for AI-assisted tasks
  - Shell scripts for compilation and general automation

### Python Scripts

The Python scripts provide AI-assisted manuscript preparation through:

- **scitex.py** - Main entry point for Python functionality
- **revise.py** - Handles AI-powered text revision
- **insert_citations.py** - Manages citation insertion assistance
- **check_terms.py** - Ensures terminology consistency
- **gpt_client.py** - Interface with OpenAI's GPT models
- **file_utils.py** - Utilities for file operations
- **config.py** - Configuration and settings
- **prompt_loader.py** - Loads templates for prompts
- **tests/** - Testing infrastructure
  - unit/ - Unit tests
  - integration/ - Integration tests
  - fixtures/ - Test data and fixtures

### Shell Scripts

The shell scripts automate the compilation and manuscript preparation process:

- **compile.sh** - Main entry point for compilation
- **revise.sh** - Triggers AI-powered revision
- **insert_citations.sh** - Helps with citation insertion
- **modules/** - Modular scripts for specific tasks
  - config.sh - Configuration settings
  - compile_main_tex.sh - LaTeX compilation
  - check_terms.sh - Term consistency checking
  - Other utility scripts for figures, tables, versioning, etc.

## Revision Component

The revision component helps manage the peer review process:

- **main.tex** - Main LaTeX file for the revision response
- **src/** - Source files for revision 
  - reviewer1/, reviewer2/ - Directories for each reviewer
    - comments.tex - Reviewer comments
    - response.tex - Author responses
    - revision.tex - Description of revisions made
  - editor/ - Editor-specific communications
  - commands.tex - LaTeX commands for revision

## Supplementary Component

The supplementary component contains additional materials:

- **main.tex** - Main LaTeX file for supplementary materials
- **src/** - Source files for supplementary content
  - LaTeX source files
  - figures/ - Supplementary figures
  - tables/ - Supplementary tables

## Root Scripts

The root scripts provide easy entry points for different compilation tasks:

- **compile-all.sh** - Compile manuscript, revision, and supplementary
- **compile-manuscript.sh** - Compile only the manuscript
- **compile-revision.sh** - Compile only the revision
- **compile-supplementary.sh** - Compile only the supplementary

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