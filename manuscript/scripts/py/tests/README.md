# SciTex Python Module Tests

This directory contains tests for the SciTex Python modules used in the manuscript processing system.

## Directory Structure

```
tests/
├── fixtures/              # Test data and fixtures
│   ├── __init__.py
│   ├── sample_bib.bib     # Sample bibliography file for testing
│   └── sample_tex.tex     # Sample LaTeX file for testing
├── integration/           # Integration tests
│   ├── __init__.py
│   └── test_workflow.py   # Tests for complete workflows
├── unit/                  # Unit tests for individual modules
│   ├── __init__.py
│   ├── test_file_utils.py # Tests for file operations
│   ├── test_gpt_client.py # Tests for GPT integration
│   └── test_prompt_loader.py # Tests for prompt templates
└── README.md              # This file
```

## Running the Tests

### Using the Test Script

The easiest way to run tests is using the provided script:

```bash
# From the manuscript directory
./scripts/sh/run_tests.sh       # Run all tests
./scripts/sh/run_tests.sh -v    # Run with verbose output
./scripts/sh/run_tests.sh -p test_file_utils.py  # Run specific tests
```

### Using Python Directly

You can also run tests using Python directly:

```bash
# From the scripts/py directory
python run_tests.py

# Using pytest directly
cd scripts/py
pytest tests/
```

## Test Coverage

These tests cover the core Python modules used in SciTex:

1. **Core Utilities**
   - `file_utils.py`: File operations like loading/saving TeX files
   - `prompt_loader.py`: Loading and formatting prompt templates
   - `config.py`: Configuration management

2. **AI Integration**
   - `gpt_client.py`: Interface with OpenAI's GPT models
   - `revise.py`: Text revision functionality
   - `check_terms.py`: Terminology consistency checking
   - `insert_citations.py`: Citation management

3. **Tool Utilities**
   - `crop_tif.py`: Image processing for figures
   - `pptx2tif.py`: PowerPoint to TIF conversion
   - `diff.py`: Text comparison utilities

## Writing New Tests

When adding new functionality to the Python modules, follow these guidelines for writing tests:

1. **Unit Tests**
   - Place in the `unit/` directory
   - Name files as `test_<module_name>.py`
   - Test each function in isolation
   - Mock external dependencies

2. **Integration Tests**
   - Place in the `integration/` directory
   - Test entire workflows across multiple modules
   - Use test fixtures for input/output

3. **Test Fixtures**
   - Place reusable test data in the `fixtures/` directory
   - Use descriptive names for fixtures

## Test Skip Rules

Some tests may be skipped under certain conditions:

1. **API Tests**
   - Integration tests requiring the OpenAI API will be skipped if `OPENAI_API_KEY` is not set
   - Use the `@pytest.mark.skipif` decorator for these tests

2. **System-Dependent Tests**
   - Tests requiring specific system tools (like LibreOffice) should be skipped if unavailable
   - Check for dependencies before running tests

## Debug Tips

When tests fail, try these debugging approaches:

1. Run tests with increased verbosity: `pytest -vv tests/`
2. Isolate specific failing tests: `pytest tests/unit/test_file_utils.py::TestFileUtils::test_load_tex`
3. Add temporary print statements or breakpoints: `import pdb; pdb.set_trace()`
4. Check test fixtures and mock objects for correctness

## Continuous Integration

These tests are run automatically on GitHub Actions when changes are pushed to the repository. The workflow is defined in the `.github/workflows/python-tests.yml` file.