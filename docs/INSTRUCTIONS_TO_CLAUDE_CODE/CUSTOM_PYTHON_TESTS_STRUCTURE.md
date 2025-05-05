<!-- ---
!-- Timestamp: 2025-05-06 08:42:10
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/SciTex/docs/INSTRUCTIONS_TO_CLAUDE_CODE/CUSTOM_PYTHON_TESTS_STRUCTURE.md
!-- --- -->

# Python Custom Test Structure (src/tests Mirror Rule)

#### ALL SOURCE CODE MUST HAVE THE CORRESPONDING TEST CODE
    - WE DO NEVER ALLOW ANY SOURCE CODE WITHOUT TEST IMPLEMENTED
    - TEST-DRIVEN DEVELOPMENT IS A GOOD STRUTEGY FOR AGENTIC DEVELOPMENT

#### Project Structure
  - `./src`
    - Should include a pip-installable package

  - `./scripts` 
    - Should include analytic or AI code
      - This is often a scientific project, as the nature of uncertainty

  - `./tests`
    - Should include all test codes
    - Must mirror the src/ directory hierarchy exactly
      - For every src/xxx/path/module.py, put tests in tests/xxx/path/test_module.py.
      - Subdirectories and nesting must be preserved.
      - Every source file in src/ gets a corresponding test_*.py file in tests/.
    - Custom/integration/CLI/non-mirrored tests go in tests/custom/, never in tests/xxx/....
    - Test file should be named as `test_<source-file-name>.py`

#### Test File Template
Each test file starts with:

``` python
# ADD YOUR TESTS HERE

if __name__ == "__main__":
    import os
    
    import pytest
    
    pytest.main([os.path.abspath(__file__)])

# HERE IS THE SOURCE CODE COMMENT SECTION
# DO NOT EDIT THIS
# A CUSTOM SCRIPT WILL UPDATE THIS SECTION TO REFLECT THE SOURCE SCRIPTS
```

- DO NOT FORGET SPACCE BETWEEN `import os`, `import pytest`, and `pytest.main([os.path.abspath(__file__)])`.
  - This is because of the use of a custom linter

#### Tooling and Updates
- Use this to maintain test file structure, code stubs, and synchronization of code
  - `./tests/sync_tests_with_source.sh`
  - This script guarantees that `./tests/` always matches the structure of `./src/`.
  - Unmatched or obsolete test files will be moved to .old-TIMESTAMP/, not deleted.
  - Test code themselves and mainguard for pytest are preserved; just the source code is updated

#### Writing and Modifying Tests
- Test file must be always associated with a source file
  - When new source file created, use the `./tests/sync_tests_with_source.sh` script to initialize the corresponding test file as an template.
    - Then, implement test logic and supporting utilities at the top (above main guard and source comments)
    - Use pytest, following its conventions for test function/class names.
    - Do NOT remove the source code comment at the bottom.
    - Import statements should use path from the repository root: `from mngs.[...module path...] import ...`
      - Never use relative or risky import patterns.
    - Do not combine unrelated test code; always keep per-source modules separate.
    - Custom/integration tests belong in `./tests/custom/` or similar, NOT within the mirrored hierarchy.
  - If tests/source scripts are moved/renamed, move relevant test file accordingly.
  - If a source file is removed, move the test file to .old-TIMESTAMP/.
    - However, this is handled by `./tests/sync_tests_with_source.sh` as well

#### Running Tests (for reference)
- All tests can be run with: `pytest`
- You may run individual modules, e.g.: `pytest tests/mngs/foo/test_bar.py`
- Use `./run_tests.sh` for custom settings
- Locate the pytest.ini to `./tests/pytest.ini`

#### GitHub CI/CD
- Implement `./github/workflows/<job-name>.yml`
- Implement `./github/workflows/run_tests.yml` for the custom `./run_tests.sh`
- Do not forget to install dependencies
- Use ubuntu

<!-- EOF -->