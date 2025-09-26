# SciTex Shell Module Tests

This directory contains test scripts for the shell modules in the SciTex project.

## Available Tests

- `test_load_config.sh`: Tests the configuration file
- `test_versioning.sh`: Tests version management functionality
- `test_check_commands.sh`: Tests dependency checking
- `test_process_figures.sh`: Tests figure processing
- `test_process_tables.sh`: Tests table processing

## Running Tests

### Run All Tests

To run all tests at once, use the master test script:

```bash
./run_all_tests.sh
```

This will execute all the test scripts in sequence and provide a summary of the results.

### Run Individual Tests

You can also run individual test scripts if you need to focus on testing a specific module:

```bash
./test_load_config.sh
./test_versioning.sh
./test_check_commands.sh
./test_process_figures.sh
./test_process_tables.sh
```

## Test Structure

Each test script follows a similar structure:

1. Setup phase: Creates a controlled test environment
2. Test execution: Runs individual test cases for each function
3. Cleanup phase: Removes temporary files and directories

## Adding New Tests

To add tests for another module:

1. Create a new test script file named `test_module_name.sh`
2. Follow the existing test patterns:
   - Create a temporary test environment
   - Source the module to test its functions
   - Use the `test_function()` helper to write test cases
   - Clean up after the tests

## Dependencies

The tests require the following commands to be available:

- `bash`: For executing the scripts
- `grep`, `sed`, `awk`: For text processing
- `convert`: For image creation in figure tests (from ImageMagick)

## Troubleshooting

If tests are failing:

1. Check the error output for details on which specific tests failed
2. Verify that all dependencies are installed
3. Ensure the original module files are present in `../modules/`