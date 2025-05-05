<!-- ---
!-- Timestamp: 2025-05-05 12:06:09
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/SciTex/README.md
!-- --- -->

# SciTex: AI-assisted Template for Scientific Manuscripts

![Compile Test](https://github.com/ywatanabe1989/SciTex/actions/workflows/compile-test.yml/badge.svg)
![Python Tests](https://github.com/ywatanabe1989/SciTex/actions/workflows/python-tests.yml/badge.svg)
![Lint](https://github.com/ywatanabe1989/SciTex/actions/workflows/lint.yml/badge.svg)

SciTex is a comprehensive LaTeX template system for scientific manuscript preparation with integrated AI assistance. It complies with [Elsevier's manuscript guidelines](https://www.elsevier.com/researcher/author/policies-and-guidelines/latex-instructions) while remaining adaptable for other journals.

## Key Features

- **Modular Structure**: Organize your manuscript into logical components
- **AI-Powered Assistance**: Leverage GPT models for text revision, terminology checking, and citation management
- **Figure & Table Management**: Streamlined handling of figures and tables with automated processing
- **Versioning System**: Built-in versioning to track manuscript evolution
- **Multiple Components**: Separate workflows for manuscript, revision responses, and supplementary materials

## Table of Contents

- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Basic Workflow](#basic-workflow)
- [Git/GitHub Workflow](#gitgithub-workflow)
- [AI-Assisted Features](#ai-assisted-features)
- [Figure and Table Handling](#figure-and-table-handling)
- [Testing](#testing)
- [Documentation](#documentation)
- [Examples](#examples)
- [Support](#support)

## Quick Start

### Installation on Ubuntu

```bash
# Install LaTeX and system dependencies
$ ./manuscript/scripts/sh/install_on_ubuntu.sh

# Set up Python environment
$ ./manuscript/scripts/sh/gen_pyenv.sh
# OR
$ python_init_with_local_mngs.sh  # Creates ./.env
```

### Set Up OpenAI API

```bash
$ echo 'export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"' >> ~/.bashrc
$ source ~/.bashrc
```

### Basic Compilation

```bash
# From the root directory
$ ./compile.sh -m  # Compile manuscript
$ ./compile.sh -s  # Compile supplementary materials
$ ./compile.sh -r  # Compile revision

# Or compile all components at once
$ ./compile.sh
```

You can also navigate to individual component directories:

```bash
# From component directories
$ cd manuscript && ./compile
$ cd supplementary && ./compile
$ cd revision && ./compile
```

## Project Structure

SciTex organizes content into three main components:

- **manuscript/**: Main scientific manuscript
  - `main.tex`: Main document entry point
  - `src/`: Content sections and figures/tables
  - `scripts/`: Automation tools and AI integration

- **revision/**: Revision response documents
  - `src/reviewer*/`: Reviewer-specific comments and responses
  - `src/editor/`: Editor comments and responses

- **supplementary/**: Supplementary materials
  - `src/`: Additional content, figures, and tables

## Basic Workflow

1. **Create Content**:
   - Edit section files in `manuscript/src/`
   - Update bibliography in `manuscript/src/bibliography.bib`
   - Add figures to `manuscript/src/figures/src/`
   - Add tables to `manuscript/src/tables/src/`

2. **Compile Document**:
   ```bash
   # From the root directory
   $ ./compile.sh -m
   
   # Or from manuscript directory
   $ cd manuscript && ./compile
   ```

3. **Use AI Assistance**:
   ```bash
   # From the manuscript directory
   $ cd manuscript
   $ ./compile -r  # Revise text with GPT
   $ ./compile -t  # Check terminology
   $ ./compile -c  # Insert citations
   
   # Or from root with manuscript flags
   $ ./compile.sh -m --revise  # Revise text with GPT
   $ ./compile.sh -m --terms   # Check terminology
   $ ./compile.sh -m --cite    # Insert citations
   ```

4. **Manage Figures**:
   ```bash
   # From manuscript directory
   $ cd manuscript
   $ ./compile -p2t  # Convert PowerPoint to TIF
   $ ./compile -nf   # Compile without figures (faster)
   
   # Or from root with manuscript flags
   $ ./compile.sh -m --pptx2tif  # Convert PowerPoint to TIF
   $ ./compile.sh -m --no-figures  # Compile without figures
   ```

5. **Version Control**:
   ```bash
   # From manuscript directory
   $ cd manuscript
   $ ./compile -p  # Push changes to GitHub
   
   # Or from root directory
   $ ./compile.sh -m --push  # Push changes to GitHub
   ```

## Git/GitHub Workflow

SciTex follows a standardized Git workflow to maintain code quality and collaboration:

### Branch Structure

- Always work on the `develop` branch for ongoing development
- Create feature branches (`feature/xxx`) for new features
- Pull requests are created from `develop` to `main`

### Commit Guidelines

- Commit in meaningful, logical chunks
- Use descriptive commit messages that explain the purpose of changes
- Push to origin/develop regularly to maintain synchronization

### Pre-commit Workflow

Before committing changes, ensure:

```bash
# Run the test suite
$ ./run_tests.sh

# Ensure test synchronization
$ ./tests/sync_tests_with_source.sh

# Verify compile scripts work with figures
$ ./compile -m -- -f
```

### Release Process

- Releases use semantic versioning (v1.0.0)
- All tests must pass before creating a release
- Integration tests run automatically via GitHub Actions

### Code Organization

- Follow project structure conventions
- Keep source and test structures synchronized
- Adhere to naming conventions in [Naming Conventions](./docs/NAMING_CONVENTIONS.md)

For more details on the development workflow, see [Test Sync Guide](./docs/TEST_SYNC_GUIDE.md).

## AI-Assisted Features

SciTex leverages OpenAI's GPT models for several tasks:

- **Text Revision**: Improve grammar, style, and clarity
- **Terminology Checking**: Ensure consistent terminology and abbreviations
- **Citation Management**: Automatically insert appropriate citations

## Figure and Table Handling

SciTex provides a standardized system for managing figures and tables:

- **Naming Conventions**: Use predefined patterns for consistent referencing
- **Automated Processing**: Convert, format, and include figures and tables automatically
- **Caption Management**: Easily organize and maintain captions separately from images

For details, see:
- [Figure and Table Guide](./docs/FIGURE_TABLE_GUIDE.md)
- [Naming Conventions](./docs/NAMING_CONVENTIONS.md)

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
$ ./run_tests.sh

# Run with verbose output
$ ./run_tests.sh -v

# Run specific tests
$ ./run_tests.sh -p test_file_utils.py
```

## Documentation

Detailed documentation is available in the `docs/` directory:

- [Usage Guide](./docs/USAGE_FOR_LLM.md) - Comprehensive usage instructions
- [Compilation Guide](./docs/COMPILATION_GUIDE.md) - Document compilation workflow
- [Figure/Table Guide](./docs/FIGURE_TABLE_GUIDE.md) - Guide for figure and table management
- [Naming Conventions](./docs/NAMING_CONVENTIONS.md) - File naming and reference guidelines
- [Test Sync Guide](./docs/TEST_SYNC_GUIDE.md) - Test synchronization workflow
- [Project Plan](./docs/PLAN.md) - Project roadmap and milestones

## Examples

Example scripts demonstrating key functionality:

- [Basic Revision](./examples/basic_revision.py) - AI text revision
- [Check Terms](./examples/check_terms.py) - Terminology consistency
- [Insert Citations](./examples/insert_citations.py) - Citation management
- [Complete Workflow](./examples/complete_workflow.sh) - End-to-end usage

## Support

For help or feedback, please contact ywatanabe@alumni.u-tokyo.ac.jp or [open an issue](https://github.com/ywatanabe1989/SciTex/issues) on GitHub.

<!-- EOF -->