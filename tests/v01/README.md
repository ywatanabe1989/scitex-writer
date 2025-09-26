# SciTex Testing Guide

This directory contains the test suite for SciTex. The tests ensure the correct functioning of both Python modules and LaTeX compilation processes.

## Test Structure

```
tests/
├── conftest.py            # pytest configuration
├── pytest.ini             # pytest settings
├── sync_tests_with_source.sh  # Synchronization script
├── unit/                  # Unit tests
│   ├── test_file_utils.py
│   ├── test_gpt_client.py
│   └── ...
├── integration/           # Integration tests
│   └── test_workflow.py
└── fixtures/              # Test fixtures and sample data
    ├── sample_tex.tex
    ├── sample_bib.bib
    └── ...
```

## Setting Up the Testing Environment

### Prerequisites

- Python 3.8+
- pytest and related packages

### Installation

```bash
# Install required packages
pip install -r requirements.txt
```

## Running Tests

### Using the Test Script

The `run_tests.sh` script provides a convenient way to run the test suite:

```bash
# Run all tests
./run_tests.sh

# Run tests with verbose output
./run_tests.sh -v

# Run specific tests
./run_tests.sh -p test_file_utils.py

# Delete Python cache before running tests
./run_tests.sh -c

# Sync test structure with source files
./run_tests.sh -s

# Run tests with multiple workers (parallel execution)
./run_tests.sh -j 4

# Run tests multiple times
./run_tests.sh -n 3
```

### Using pytest Directly

You can also use pytest commands directly:

```bash
# Run all tests
pytest

# Run with increased verbosity
pytest -v

# Run specific test file
pytest tests/unit/test_file_utils.py

# Run specific test function
pytest tests/unit/test_file_utils.py::TestFileUtils::test_load_tex

# Generate coverage report
pytest --cov=manuscript/scripts/py tests/
```

## Test Categories

### Unit Tests

Unit tests focus on testing individual functions and classes in isolation. These tests are located in the `unit/` directory and verify the behavior of specific components.

Example unit test files:
- `test_file_utils.py`: Tests for file operations
- `test_gpt_client.py`: Tests for OpenAI API integration
- `test_prompt_loader.py`: Tests for prompt template loading

### Integration Tests

Integration tests verify the interaction between multiple components. These tests are located in the `integration/` directory and test complete workflows.

Example integration test files:
- `test_workflow.py`: Tests the complete manuscript preparation workflow

## Writing Tests

### Test File Structure

When creating new tests, follow this structure:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pytest
from manuscript.scripts.py.module_name import function_name

class TestClassName:
    def setup_method(self):
        # Setup code that runs before each test
        pass
        
    def teardown_method(self):
        # Cleanup code that runs after each test
        pass
        
    def test_function_name(self):
        # Test code
        result = function_name(arguments)
        assert result == expected_value
```

### Test Naming Conventions

- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`

### Using Fixtures

Fixtures are reusable test resources defined in `conftest.py` or within test files:

```python
@pytest.fixture
def sample_tex_content():
    return "\\section{Test}\nThis is a test."

def test_with_fixture(sample_tex_content):
    result = process_tex(sample_tex_content)
    assert "Test" in result
```

### Mocking External Dependencies

When testing code that depends on external services (like the OpenAI API), use mocking:

```python
from unittest.mock import patch, MagicMock

@patch('openai.OpenAI')
def test_gpt_client(mock_openai):
    # Configure the mock
    mock_instance = mock_openai.return_value
    mock_chat = mock_instance.chat.completions.create
    mock_chat.return_value.choices[0].message.content = "Mocked response"
    
    # Test with the mock
    client = GPTClient()
    response = client("Test prompt")
    assert response == "Mocked response"
```

## Test Coverage

To generate a coverage report:

```bash
# Generate coverage report
pytest --cov=manuscript/scripts/py tests/

# Generate HTML report
pytest --cov=manuscript/scripts/py tests/ --cov-report=html
```

The HTML report will be available in the `htmlcov/` directory.

## Synchronizing Tests with Source Files

The `sync_tests_with_source.sh` script automatically creates test files for Python modules:

```bash
# Synchronize test structure with source files
./tests/sync_tests_with_source.sh
```

This script:
1. Creates test directories mirroring the source structure
2. Creates test file templates for Python modules without tests
3. Updates imports and placeholders in test files

## Continuous Integration

SciTex uses GitHub Actions for continuous integration testing. The workflow configurations are located in the `.github/workflows/` directory.

- `python-tests.yml`: Runs Python unit and integration tests
- `compile-test.yml`: Tests LaTeX compilation
- `lint.yml`: Checks code style and formatting

## Troubleshooting Tests

### Common Issues

1. **Missing dependencies**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`

2. **OpenAI API Key**
   - Set the `OPENAI_API_KEY` environment variable or use a mock

3. **File path issues**
   - Use absolute paths or ensure correct working directory
   - Use test fixtures for standardized paths

4. **LaTeX compilation errors**
   - Check LaTeX dependencies are installed
   - Verify template files are accessible

### Debug Strategies

1. Use pytest's verbose mode: `pytest -v`
2. Enable step-by-step debugging: `pytest --pdb`
3. Inspect test failures with detailed output: `pytest -vv`
4. Use temporary breakpoints: `import pdb; pdb.set_trace()`