# SciTex Examples

This directory contains example scripts and workflows demonstrating SciTex features.

## Examples Overview

1. [Basic Revision](#basic-revision) - Demonstrates using GPT to revise a TeX file
2. [Citation Insertion](#citation-insertion) - Shows automatic citation insertion
3. [Terminology Check](#terminology-check) - Checks for consistent terminology
4. [Complete Workflow](#complete-workflow) - Demonstrates a complete manuscript preparation workflow

## Basic Revision

The `basic_revision.py` script demonstrates how to use the GPT-powered revision functionality:

```bash
# Run from the SciTex root directory
python examples/basic_revision.py --input manuscript/src/introduction.tex

# Run with custom output path
python examples/basic_revision.py --input manuscript/src/introduction.tex --output revised_introduction.tex
```

## Citation Insertion

The `insert_citations.py` script demonstrates automatic citation insertion:

```bash
# Run from the SciTex root directory
python examples/insert_citations.py --input manuscript/src/introduction.tex --bib manuscript/src/bibliography.bib
```

## Terminology Check

The `check_terms.py` script demonstrates terminology consistency checking:

```bash
# Run from the SciTex root directory
python examples/check_terms.py --input manuscript/src/abstract.tex
```

## Complete Workflow

The `complete_workflow.sh` script demonstrates a complete manuscript preparation workflow:

```bash
# Run from the SciTex root directory
./examples/complete_workflow.sh
```

This script:
1. Revises all TeX files
2. Checks terminology consistency
3. Inserts citations
4. Compiles the document

## Using the Python API

The `using_python_api.py` script demonstrates how to use the SciTex Python API:

```python
from scitex.gpt_client import GPTClient
from scitex.file_utils import load_tex, save_tex
from scitex.prompt_loader import load_prompt

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