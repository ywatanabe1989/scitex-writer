# Test Synchronization Guide for SciTex

This document explains how the test synchronization system works in SciTex. The synchronization script (`sync_tests_with_source.sh`) ensures that test files match the structure of the source code, making it easier to maintain comprehensive test coverage.

## Overview

SciTex implements a test-driven development approach where the test structure mirrors the source code structure. This allows for easier navigation, better organization, and ensures test coverage for all Python modules.

The test synchronization system provides several key benefits:

1. **Mirrored Structure**: Test directories automatically mirror the source code structure
2. **Automatic Test Creation**: Creates test file templates for any Python modules without tests
3. **Test Preservation**: Preserves existing test code while updating references to source
4. **Source Code References**: Includes source code as comments for easy reference
5. **Cleanup**: Identifies and optionally relocates stale test files
6. **Consistent Test Structure**: Enforces a standard structure for all test files

## The Synchronization Script

The script is located at `./tests/sync_tests_with_source.sh` and can be run directly or through the test runner with the `-s` flag:

```bash
# Run directly
./tests/sync_tests_with_source.sh

# Through the test runner
./run_tests.sh -s
```

## Command Line Options

The script supports several command-line options:

```
Usage: sync_tests_with_source.sh [options]

Options:
  -m, --move         Move stale test files to .old directory
  -s, --source DIR   Specify custom source directory
  -t, --tests DIR    Specify custom tests directory
  -h, --help         Display help message
```

## How the Script Works

The synchronization process involves several steps:

### 1. Directory Structure Setup

The script first creates a directory structure in the tests directory that mirrors the source code:

```
SciTex/
├── manuscript/
│   └── scripts/
│       └── py/
│           ├── file_utils.py       # Source module
│           ├── gpt_client.py       # Source module
│           └── ...
└── tests/
    └── unit/
        ├── test_file_utils.py      # Test module
        ├── test_gpt_client.py      # Test module
        └── ...
```

This is done by scanning the source directory and creating corresponding directories in the test directory.

### 2. Test File Generation and Update

For each Python module in the source code:

1. **Find or Create Test File**: If a test file exists, it's updated; otherwise, a new one is created
2. **Preserve Test Code**: If updating an existing file, the script extracts and preserves the actual test code
3. **Standard Structure**: Each test file follows a structure:
   - Test code at the top
   - Standard pytest guard for running individual tests
   - Optional source code as comments for reference

### 3. Cleanup and Maintenance

The script also performs several cleanup tasks:

1. **Remove Temporary Files**: Cleans up Python cache files and other temporary files
2. **Identify Stale Tests**: Identifies test files that don't have corresponding source files
3. **Optional File Relocation**: With the `-m` flag, moves stale tests to an archive directory

## Test File Structure

Generated test files follow this structure:

```python
# Test code goes here

def test_example():
    # Test implementation
    pass

if __name__ == "__main__":
    import os
    import pytest
    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /path/to/source/file.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# ...source code as comments...
# --------------------------------------------------------------------------------
# End of Source Code from: /path/to/source/file.py
# --------------------------------------------------------------------------------
```

This structure allows:
- Tests to be written at the top for easy access
- Individual test files to be run directly (e.g., `python test_file_utils.py`)
- Source code to be referenced without leaving the test file

## Best Practices

### When to Run the Sync Script

Run the synchronization script:

1. **After Adding New Source Files**: To generate corresponding test files automatically
2. **Before Major Test Development**: To ensure you have the latest test structure
3. **During Code Cleanup**: To identify and archive stale tests
4. **As Part of CI/CD Pipeline**: To enforce test coverage requirements

### Writing Tests

When writing tests for SciTex:

1. **Preserve Test Structure**: Write test code above the pytest guard to ensure it's preserved during sync
2. **One Test File Per Source File**: Follow the one-to-one mapping between source and test files
3. **Use Pytest Fixtures**: Leverage fixtures defined in `conftest.py` for reusable test resources
4. **Follow Naming Conventions**:
   - Test files: `test_*.py`
   - Test classes: `Test*`
   - Test methods: `test_*`
5. **Include Edge Cases**: Test normal operation and edge cases/error conditions

### Clean Test Maintenance

To keep the test suite clean and maintainable:

1. **Use Flag for Cleanup**: Use the `-m` flag when you want to move stale tests instead of just reporting them
2. **Check Sync Results**: Review the output to ensure all tests are properly synchronized
3. **Maintain Test Independence**: Tests should be independent and not rely on state from other tests
4. **Clean Up Temporary Files**: Remove any temporary files created during tests
5. **Commit With Sync**: Run sync before committing to ensure test structure is up to date

## Customization

The script can be customized in several ways:

1. **Exclude Patterns**: Modify the `EXCLUDE_PATHS` array to add patterns for files/directories to ignore
2. **Test Templates**: Modify the default test file structure in the `update_test_file` function
3. **Custom Directories**: Use the `-s` and `-t` flags to specify custom source and test directories

## Troubleshooting

### Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| Script fails to create test files | Check file permissions and paths |
| Stale tests not identified | Review exclude patterns and ensure paths are correct |
| Test code lost after sync | Ensure test code is above the pytest guard |
| Source files not found | Check source directory setting and file exclude patterns |

### Debug Steps

If you encounter issues with the synchronization script:

1. **Check Permissions**: Ensure the script has execute permissions
   ```bash
   chmod +x ./tests/sync_tests_with_source.sh
   ```

2. **Review Exclude Patterns**: Make sure your source files aren't being excluded in the `EXCLUDE_PATHS` array

3. **Check Log Files**: Review detailed output in the log file
   ```bash
   cat ./tests/.sync_tests_with_source.sh.log
   ```

4. **Run with Verbose Output**: Monitor the script's execution
   ```bash
   bash -x ./tests/sync_tests_with_source.sh
   ```

5. **Force Cleanup**: Use the move flag to clean up stale tests
   ```bash
   ./tests/sync_tests_with_source.sh -m
   ```

## Integration with Development Workflow

### Continuous Integration

The test synchronization script integrates seamlessly with your CI/CD pipeline:

1. **Pre-commit Hook**: Add to your `.git/hooks/pre-commit` script:
   ```bash
   #!/bin/bash
   ./tests/sync_tests_with_source.sh
   if [ $? -ne 0 ]; then
     echo "Test sync failed! Run ./tests/sync_tests_with_source.sh manually to fix issues"
     exit 1
   fi
   ```

2. **GitHub Actions**: Add to your workflow file:
   ```yaml
   - name: Sync tests with source
     run: |
       ./tests/sync_tests_with_source.sh
       git diff --exit-code tests/ || (echo "Test structure out of sync" && exit 1)
   ```

3. **Coverage Integration**: Run before coverage analysis:
   ```bash
   ./tests/sync_tests_with_source.sh && pytest --cov=manuscript/scripts/py tests/
   ```

### Test-Driven Development Workflow

To implement test-driven development with the sync system:

1. **Start With Tests**: Write test files first, following the naming convention
2. **Run Sync Script**: Use the sync script to create the source file structure
3. **Implement Source Code**: Write the source code to make tests pass
4. **Verify Coverage**: Use coverage tools to ensure tests cover all source code
5. **Repeat**: Add more tests for new features and run sync again

## Examples

### Example: Creating a Test for a New Module

1. Run the sync script with your new source file:
   ```bash
   # Assuming you created manuscript/scripts/py/new_feature.py
   ./tests/sync_tests_with_source.sh
   ```

2. Edit the generated test file:
   ```python
   # tests/unit/test_new_feature.py
   import pytest
   from manuscript.scripts.py.new_feature import MyNewFeature

   class TestMyNewFeature:
       def test_initialization(self):
           feature = MyNewFeature()
           assert feature is not None
       
       def test_process_data(self):
           feature = MyNewFeature()
           result = feature.process_data("test")
           assert result == "processed test"
   
   # [pytest guard and source code will follow automatically]
   ```

3. Run the test:
   ```bash
   pytest tests/unit/test_new_feature.py -v
   ```