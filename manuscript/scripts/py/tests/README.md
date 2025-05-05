# SciTex Tests

This directory contains tests for the SciTex Python modules.

## Test Structure

```
tests/
├── fixtures/         # Test fixtures and sample data
├── unit/             # Unit tests for individual modules
├── integration/      # Integration tests for workflows
└── README.md         # This file
```

## Running Tests

You can run the tests using the provided scripts:

```bash
# Run all tests
./scripts/sh/run_tests.sh

# Run with increased verbosity
./scripts/sh/run_tests.sh -v

# Run specific tests
./scripts/sh/run_tests.sh -p test_file_utils.py

# List available tests
./scripts/sh/run_tests.sh -l

# Stop on first failure
./scripts/sh/run_tests.sh -f
```

Alternatively, you can use the Python script directly:

```bash
cd scripts/py
python run_tests.py
```

## Writing Tests

When writing new tests:

1. Place unit tests in the `tests/unit/` directory
2. Place integration tests in the `tests/integration/` directory
3. Add any necessary test fixtures to the `tests/fixtures/` directory
4. Follow the existing test naming pattern: `test_*.py`
5. Use appropriate mocking for external services (e.g., OpenAI API)

## Test Coverage

The test suite covers:

- Core utilities in `file_utils.py`
- Prompt loading and formatting in `prompt_loader.py`
- GPT client functionality in `gpt_client.py`
- Integration workflows for revision, term checking, and citation insertion

## Skip Rules

- Integration tests that require the OpenAI API will be skipped if the `OPENAI_API_KEY` environment variable is not set