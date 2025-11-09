# Test Plan for SciTeX Writer v2.0.0-alpha

## Overview

Test suite for scitex-writer covering Python API, CLI, version management, and compilation workflows.

## Test Structure

```
tests/
├── conftest.py                          # Shared fixtures
├── pytest.ini                           # Pytest configuration
└── scitex/
    └── writer/
        ├── __init__.py
        ├── run_test.sh                  # Test runner script
        ├── TEST_PLAN.md                 # This file
        ├── test_version.py              # Version management tests
        ├── test_writer.py               # Writer class tests
        ├── test_compile.py              # Compilation function tests
        ├── test_template.py             # Template cloning tests
        └── test__integration.py         # Integration tests
```

## Test Coverage

### ✅ Implemented (v2.0.0-alpha)

**Version Management** (`test_version.py`):
- Version exists in pyproject.toml
- Python can import __version__
- Shell can load version from pyproject.toml
- Makefile can extract version
- Python and shell versions match (single source of truth)

**Writer Class** (`test_writer.py`):
- Writer initialization with valid/invalid project dirs
- Doc type parameter handling
- Project directory path resolution
- Attribute validation

**Compilation** (`test_compile.py`):
- Import of compilation functions
- CompilationResult class
- Compilation with mock scripts
- Error handling for missing scripts

**Template Cloning** (`test_template.py`):
- clone_writer_project function exists
- Project creation (basic)
- Rejection of existing directories
- Git strategy placeholders

**Integration** (`test__integration.py`):
- All main interfaces importable
- Version consistency across Python/Shell/Makefile
- Project structure validation
- Required files exist

### 🔜 Future Tests (Post v2.0.0)

**Compilation Workflows:**
- Full end-to-end LaTeX compilation
- Figure processing pipeline
- Table processing pipeline
- Bibliography generation
- Diff generation

**CLI Tests:**
- scitex-writer compile commands
- scitex-writer new command
- scitex-writer update command
- scitex-writer watch command

**Update Mechanism:**
- Update script behavior
- User content preservation
- Git conflict handling
- Backup creation

**Container Integration:**
- Apptainer/Singularity detection
- Container download
- LaTeX command resolution
- Container fallback behavior

## Running Tests

### Run all tests:
```bash
pytest tests/ -v
./tests/scitex/writer/run_test.sh
make test
```

### Run specific test file:
```bash
pytest tests/scitex/writer/test_version.py -v
```

### Run with markers:
```bash
pytest tests/ -m unit          # Unit tests only
pytest tests/ -m integration   # Integration tests only
pytest tests/ -m "not slow"    # Skip slow tests
```

## Test Requirements

**Minimal (for current tests):**
- Python 3.8+
- pytest
- No LaTeX required (uses mocks)

**Full (for future tests):**
- Apptainer or Singularity
- LaTeX (or containers)
- Git

## Success Criteria

- [x] All imports work without errors
- [x] Version consistency validated
- [x] Project structure validated
- [x] Basic Writer class functionality tested
- [ ] Full compilation workflows tested (future)
- [ ] CLI commands tested (future)
- [ ] Update mechanism tested (future)

## Notes

- Tests use temporary directories for isolation
- Mock scripts avoid LaTeX dependency
- Integration tests validate real project structure
- Version tests ensure single source of truth (pyproject.toml)

<!-- EOF -->
