# SciTeX Writer Test Suite

Comprehensive test suite for validating compilation engines, document types, and integration features.

## Quick Start

```bash
# Run all tests
./tests/scripts/run_all_tests.sh

# Run specific test
./tests/scripts/test_compilation_engines.sh
./tests/scripts/test_document_types.sh
./tests/scripts/test_tectonic_integration.sh
./tests/scripts/test_parallel_compilation.sh
```

## Test Files

### Core Tests

- **test_compilation_engines.sh** - Tests all three compilation engines (latexmk, 3pass, tectonic)
  - Verifies each engine compiles successfully
  - Checks PDF output existence
  - Validates engine-specific behavior
  - ~45s sequential, ~15s parallel

- **test_document_types.sh** - Tests all three document types (manuscript, supplementary, revision)
  - Uses parallel compilation (3 documents simultaneously)
  - Verifies PDF and diff generation
  - Tests all engines on manuscript
  - ~45s with parallelization

- **test_tectonic_integration.sh** - Tests tectonic-specific features
  - Absolute path detection and usage
  - Package compatibility (lineno, bashful disabled)
  - Reruns optimization (--reruns=1)
  - Path style verification (absolute vs relative)
  - ~30s

### Performance Tests

- **test_parallel_compilation.sh** - Stress test with safe parallelization
  - Tests all 9 combinations (3 engines × 3 documents)
  - **Parallelizes by document type only** (3 at a time)
  - Engines run sequentially to avoid file conflicts
  - Demonstrates ~3x speedup on document types
  - ~45s (vs ~135s fully sequential)

## Parallelization Strategy

### Safe Parallelization: By Document Type Only

The test suite parallelizes **document types** but NOT **engines** to avoid file conflicts:

```bash
# ✓ SAFE - Different directories
(./compile.sh manuscript > log1 2>&1) &      # → 01_manuscript/
(./compile.sh supplementary > log2 2>&1) &   # → 02_supplementary/
(./compile.sh revision > log3 2>&1) &        # → 03_revision/
wait

# ❌ UNSAFE - Same files (race condition!)
# export SCITEX_WRITER_ENGINE=latexmk
# (./compile.sh manuscript > log1 2>&1) &     # → 01_manuscript/manuscript.pdf
# export SCITEX_WRITER_ENGINE=tectonic
# (./compile.sh manuscript > log2 2>&1) &     # → 01_manuscript/manuscript.pdf (CONFLICT!)
```

**Why not parallelize engines?**
- Multiple engines on the same document write to the same output files
- Creates race conditions: `01_manuscript/manuscript.pdf` written by multiple processes
- Results in corrupted PDFs or test failures

**Pattern used throughout tests:**
```bash
# Run 3 documents in parallel (SAFE)
(./compile.sh manuscript > log1 2>&1; echo $? > exit1) &
(./compile.sh supplementary > log2 2>&1; echo $? > exit2) &
(./compile.sh revision > log3 2>&1; echo $? > exit3) &
wait

# Check exit codes
exit1=$(cat exit1)
exit2=$(cat exit2)
exit3=$(cat exit3)
```

### Performance Impact

**Sequential execution:**
- 3 documents × 3 engines = 9 compilations
- Average: ~15s per compilation
- Total: ~135s

**Parallel by document type:**
- 3 documents in parallel per engine
- 3 engine passes (sequential)
- Total: ~45s (3 passes × 15s)
- **Speedup: ~3x**

## Test Output Format

Tests use colored output for clarity:

- 🟡 **YELLOW**: Test name/description
- 🟢 **GREEN**: Passed assertion
- 🔴 **RED**: Failed assertion
- 🔵 **BLUE**: Info message

## Exit Codes

- `0`: All tests passed
- `1`: One or more tests failed

## Dependencies

All tests require:
- bash (background jobs support)
- latexmk, pdflatex, bibtex (for latexmk engine)
- tectonic (for tectonic engine)
- Standard Unix utilities (grep, cat, rm, etc.)

## Debugging Failed Tests

If a test fails, check the log files in `/tmp/`:
- `/tmp/test_manuscript.log`
- `/tmp/test_supplementary.log`
- `/tmp/test_revision.log`
- `/tmp/test_latexmk.log`
- `/tmp/test_3pass.log`
- `/tmp/test_tectonic.log`

## Adding New Tests

1. Create `test_<name>.sh` in this directory
2. Make it executable: `chmod +x test_<name>.sh`
3. Follow the existing pattern (see examples above)
4. Use the assertion functions: `assert_success`, `assert_file_exists`, `assert_string_in_log`
5. The `run_all_tests.sh` will auto-discover it

## CI/CD Integration

Tests are designed for CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run Tests
  run: ./tests/scripts/run_all_tests.sh
  timeout-minutes: 5
```

<!-- EOF -->
