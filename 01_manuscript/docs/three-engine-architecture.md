# Three-Engine Compilation Architecture

**Status**: Design Phase
**Target**: v2.1.0
**Goal**: Position SciTeX Writer as Overleaf competitor through speed, flexibility, and reproducibility

---

## 1. Executive Summary

### Current State
- Single compilation path: latexmk (currently disabled) with 3-pass fallback
- Bibliography path resolution issues with latexmk + `-output-directory`
- No speed optimization for iterative editing
- Limited offline capability advantages over Overleaf

### Target State
- Three compilation engines available:
  - **Tectonic**: ⚡ Fast mode (1-3s incremental, 10× faster than Overleaf)
  - **latexmk**: 🔧 Standard mode (3-6s, industry standard)
  - **3-pass**: 🔒 Guaranteed mode (12-18s, maximum compatibility)
- Intelligent auto-detection with graceful degradation
- User-selectable via `--engine` flag or config file
- Unified error handling and logging

### Competitive Advantages
- **Speed**: Tectonic provides 10× faster compilation for rapid iteration
- **Offline**: True offline capability (vs Overleaf's cloud-only)
- **Reproducibility**: Container fallbacks ensure consistent builds
- **Choice**: Users select speed vs compatibility trade-offs

---

## 2. Configuration Schema

### 2.1 New Config Fields (config_manuscript.yaml)

```yaml
compilation:
  # Engine selection: tectonic, latexmk, 3pass, auto
  engine: "auto"

  # Auto-detection fallback order
  auto_order:
    - tectonic   # Try fastest first
    - latexmk    # Fall back to standard
    - 3pass      # Guaranteed fallback

  # Draft mode (single pass, skip bibliography)
  draft_mode: false

  # Per-engine settings
  engines:
    tectonic:
      # Use incremental compilation cache
      incremental: true
      # Cache directory (relative to project root)
      cache_dir: "./.tectonic-cache"
      # Bundle directory for offline packages
      bundle_dir: "./.tectonic-bundle"

    latexmk:
      # Use latexmk's smart recompilation
      incremental: true
      # Maximum passes before giving up
      max_passes: 10
      # Fix bibliography path resolution
      set_bibinputs: true

    3pass:
      # Always do full 3 passes (no incremental)
      incremental: false
      # Verbose output for each pass
      verbose_passes: false

# Existing verbosity settings
verbosity:
  pdflatex: true
  bibtex: true
  # Add per-engine verbosity
  tectonic: false   # Tectonic is verbose by default
  latexmk: false
```

### 2.2 CLI Flags

```bash
# Explicit engine selection
./compile.sh manuscript --engine=tectonic
./compile.sh manuscript --engine=latexmk
./compile.sh manuscript --engine=3pass

# Auto-detection (default)
./compile.sh manuscript --engine=auto

# Engine-specific options
./compile.sh manuscript --engine=tectonic --incremental
./compile.sh manuscript --engine=latexmk --max-passes=15

# Draft mode (works with all engines)
./compile.sh manuscript --draft --engine=tectonic
```

---

## 3. Engine Selection Logic

### 3.1 Decision Flow

```
┌─────────────────────────────────────┐
│ User Request: compile manuscript    │
└───────────────┬─────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│ Check --engine flag                 │
│   • Explicit: tectonic/latexmk/3pass│
│   • Auto: proceed to detection      │
└───────────────┬─────────────────────┘
                │
                ▼
         ┌──────┴───────┐
         │ Explicit?    │
         └──┬────────┬──┘
           Yes       No (auto)
            │         │
            │         ▼
            │  ┌─────────────────────┐
            │  │ Try engines in      │
            │  │ auto_order:         │
            │  │  1. Check tectonic  │
            │  │  2. Check latexmk   │
            │  │  3. Use 3pass       │
            │  └──────┬──────────────┘
            │         │
            ▼         ▼
┌─────────────────────────────────────┐
│ Verify Engine Available             │
│  • Command exists?                  │
│  • Version compatible?              │
│  • Container fallback available?   │
└───────────────┬─────────────────────┘
                │
                ▼
         ┌──────┴───────┐
         │ Available?   │
         └──┬────────┬──┘
           Yes       No
            │         │
            │         ▼
            │  ┌─────────────────────┐
            │  │ If explicit: ERROR  │
            │  │ If auto: try next   │
            │  └─────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│ Execute Compilation                 │
│  • Set engine-specific env vars    │
│  • Run engine-specific commands     │
│  • Parse engine-specific errors     │
└───────────────┬─────────────────────┘
                │
                ▼
         ┌──────┴───────┐
         │ Success?     │
         └──┬────────┬──┘
           Yes       No
            │         │
            │         ▼
            │  ┌─────────────────────┐
            │  │ If auto: try next   │
            │  │ If explicit: report │
            │  └─────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│ Post-processing                     │
│  • Validate PDF output              │
│  • Report statistics                │
│  • Update symlinks                  │
└─────────────────────────────────────┘
```

### 3.2 Implementation (compile_manuscript.sh)

**Location**: Before line 211 (before PDF generation phase)

```bash
# ----------------------------------------
# Engine Selection Phase (NEW)
# ----------------------------------------
echo_header "Engine Selection"

# Get engine from CLI flag or config
SELECTED_ENGINE="${FLAG_ENGINE:-${SCITEX_WRITER_ENGINE}}"

if [ "$SELECTED_ENGINE" = "auto" ]; then
    # Auto-detection: try engines in order
    source "${SCRIPTS_DIR}/modules/select_compilation_engine.sh"
    SELECTED_ENGINE=$(auto_detect_engine)
    echo_info "Auto-detected engine: $SELECTED_ENGINE"
else
    # Explicit selection: verify availability
    source "${SCRIPTS_DIR}/modules/select_compilation_engine.sh"
    if ! verify_engine "$SELECTED_ENGINE"; then
        echo_error "Requested engine '$SELECTED_ENGINE' not available"
        exit 1
    fi
    echo_info "Using requested engine: $SELECTED_ENGINE"
fi

# Export for downstream modules
export SCITEX_WRITER_SELECTED_ENGINE="$SELECTED_ENGINE"
```

---

## 4. Engine-Specific Implementations

### 4.1 Command Switching Module Extension

**File**: `scripts/shell/modules/command_switching.src`

**New functions to add**:

```bash
# ========================================
# TECTONIC COMMANDS
# ========================================
get_cmd_tectonic() {
    local orig_dir="${1:-$(pwd)}"

    # Check native tectonic
    if command -v tectonic &> /dev/null; then
        echo "tectonic"
        return 0
    fi

    # Check container fallback
    local container_cmd=$(get_container_cmd "$orig_dir")
    if [ -n "$container_cmd" ]; then
        echo "$container_cmd tectonic"
        return 0
    fi

    return 1
}

get_tectonic_version() {
    local cmd=$(get_cmd_tectonic)
    if [ -n "$cmd" ]; then
        $cmd --version 2>&1 | head -1
    fi
}

# ========================================
# LATEXMK COMMANDS (enhanced)
# ========================================
get_cmd_latexmk() {
    local orig_dir="${1:-$(pwd)}"

    # Check native latexmk
    if command -v latexmk &> /dev/null; then
        echo "latexmk"
        return 0
    fi

    # Check module load (HPC systems)
    if type module &> /dev/null; then
        if module load latexmk 2>&1 | grep -q "latexmk"; then
            echo "latexmk"
            return 0
        fi
    fi

    # Check container fallback
    local container_cmd=$(get_container_cmd "$orig_dir")
    if [ -n "$container_cmd" ]; then
        echo "$container_cmd latexmk"
        return 0
    fi

    return 1
}

# ========================================
# 3-PASS COMPILATION (existing)
# ========================================
# Already have get_cmd_pdflatex() and get_cmd_bibtex()
# No changes needed
```

### 4.2 Engine Selection Module (NEW)

**File**: `scripts/shell/modules/select_compilation_engine.sh`

```bash
#!/bin/bash
# Select and verify compilation engine

source "$(dirname ${BASH_SOURCE[0]})/command_switching.src"

# Auto-detect best available engine
auto_detect_engine() {
    local auto_order="${SCITEX_WRITER_AUTO_ORDER:-tectonic latexmk 3pass}"

    for engine in $auto_order; do
        if verify_engine "$engine"; then
            echo "$engine"
            return 0
        fi
    done

    # Fallback to 3pass (always works if pdflatex exists)
    echo "3pass"
}

# Verify engine is available
verify_engine() {
    local engine="$1"

    case "$engine" in
        tectonic)
            get_cmd_tectonic >/dev/null 2>&1
            return $?
            ;;
        latexmk)
            # Need both latexmk and pdflatex
            get_cmd_latexmk >/dev/null 2>&1 && \
            get_cmd_pdflatex >/dev/null 2>&1
            return $?
            ;;
        3pass)
            # Need pdflatex and bibtex
            get_cmd_pdflatex >/dev/null 2>&1 && \
            get_cmd_bibtex >/dev/null 2>&1
            return $?
            ;;
        *)
            echo_error "Unknown engine: $engine"
            return 1
            ;;
    esac
}

# Get human-readable engine info
get_engine_info() {
    local engine="$1"

    case "$engine" in
        tectonic)
            echo "Tectonic (Fast mode, 1-3s incremental)"
            ;;
        latexmk)
            echo "latexmk (Standard mode, 3-6s incremental)"
            ;;
        3pass)
            echo "3-pass (Guaranteed mode, 12-18s full)"
            ;;
    esac
}
```

### 4.3 Tectonic Engine Implementation (NEW)

**File**: `scripts/shell/modules/engines/compile_tectonic.sh`

```bash
#!/bin/bash
# Tectonic compilation engine

compile_with_tectonic() {
    local tex_file="$1"
    local pdf_file="${tex_file%.tex}.pdf"

    echo_info "Using Tectonic engine"

    # Get tectonic command
    local tectonic_cmd=$(get_cmd_tectonic)
    if [ -z "$tectonic_cmd" ]; then
        echo_error "Tectonic not available"
        return 1
    fi

    # Build tectonic options
    local opts=""

    # Output directory
    local tex_dir=$(dirname "$tex_file")
    opts="$opts --outdir=$tex_dir"

    # Incremental mode (use cache)
    if [ "$SCITEX_WRITER_TECTONIC_INCREMENTAL" = "true" ]; then
        opts="$opts --keep-intermediates"
        # Set cache directory
        if [ -n "$SCITEX_WRITER_TECTONIC_CACHE_DIR" ]; then
            export TECTONIC_CACHE_DIR="$SCITEX_WRITER_TECTONIC_CACHE_DIR"
        fi
    fi

    # Bundle directory (offline mode)
    if [ -n "$SCITEX_WRITER_TECTONIC_BUNDLE_DIR" ]; then
        opts="$opts --bundle=$SCITEX_WRITER_TECTONIC_BUNDLE_DIR"
    fi

    # Verbosity
    if [ "$SCITEX_WRITER_VERBOSE_TECTONIC" != "true" ]; then
        opts="$opts --print=error"
    fi

    # Run compilation
    local start=$(date +%s)
    echo_info "Running: $tectonic_cmd $opts $tex_file"

    local output=$($tectonic_cmd $opts "$tex_file" 2>&1)
    local exit_code=$?

    local end=$(date +%s)

    # Check result
    if [ $exit_code -eq 0 ]; then
        echo_success "Tectonic compilation: $(($end - $start))s"
        return 0
    else
        echo_error "Tectonic compilation failed (exit code: $exit_code)"

        # Show errors if verbose or on failure
        if [ "$SCITEX_WRITER_VERBOSE_TECTONIC" = "true" ] || [ $exit_code -ne 0 ]; then
            echo "$output"
        fi

        return 1
    fi
}
```

### 4.4 latexmk Engine Implementation (FIXED)

**File**: `scripts/shell/modules/engines/compile_latexmk.sh`

```bash
#!/bin/bash
# latexmk compilation engine with BIBINPUTS fix

compile_with_latexmk() {
    local tex_file="$1"
    local pdf_file="${tex_file%.tex}.pdf"

    echo_info "Using latexmk engine"

    # Get latexmk command
    local latexmk_cmd=$(get_cmd_latexmk)
    if [ -z "$latexmk_cmd" ]; then
        echo_error "latexmk not available"
        return 1
    fi

    # Setup paths
    local tex_dir=$(dirname "$tex_file")
    local project_root=$(git rev-parse --show-toplevel 2>/dev/null || pwd)

    # FIX: Set BIBINPUTS to find bibliography files
    # latexmk runs bibtex from output directory, need to point to project root
    if [ "$SCITEX_WRITER_LATEXMK_SET_BIBINPUTS" = "true" ]; then
        export BIBINPUTS="${project_root}:"
        echo_info "Set BIBINPUTS=${BIBINPUTS}"
    fi

    # Build latexmk options
    local opts="-pdf -bibtex -interaction=nonstopmode -file-line-error"

    # Output directory
    opts="$opts -output-directory='$tex_dir'"

    # Shell escape for minted, etc.
    opts="$opts -pdflatex='pdflatex -shell-escape %O %S'"

    # Quiet mode
    if [ "$SCITEX_WRITER_VERBOSE_LATEXMK" != "true" ]; then
        opts="$opts -quiet"
    fi

    # Draft mode (single pass)
    if [ "$SCITEX_WRITER_DRAFT_MODE" = "true" ]; then
        opts="$opts -dvi- -ps-"
        echo_info "Draft mode: single pass only"
    fi

    # Max passes
    if [ -n "$SCITEX_WRITER_LATEXMK_MAX_PASSES" ]; then
        opts="$opts -latexoption=-interaction=nonstopmode"
    fi

    # Run compilation
    local start=$(date +%s)
    local cmd="$latexmk_cmd $opts '$tex_file'"

    echo_info "Running: $cmd"

    local output=$(eval "$cmd" 2>&1 | grep -v "gocryptfs not found")
    local exit_code=$?

    local end=$(date +%s)

    # Check for critical errors
    if echo "$output" | grep -q "Missing bbl file\|failed to resolve\|gave return code"; then
        echo_warning "Compilation completed with warnings (check citations/references)"
    fi

    # Check result
    if [ $exit_code -eq 0 ]; then
        echo_success "latexmk compilation: $(($end - $start))s"
        return 0
    else
        echo_error "latexmk compilation failed (exit code: $exit_code)"

        # Show output if verbose or on failure
        if [ "$SCITEX_WRITER_VERBOSE_LATEXMK" = "true" ] || [ $exit_code -ne 0 ]; then
            echo "$output"
        fi

        return 1
    fi
}
```

### 4.5 3-Pass Engine Implementation (EXISTING)

**File**: `scripts/shell/modules/engines/compile_3pass.sh`

Extract from existing `compilation_compiled_tex_to_compiled_pdf.sh` lines 96-160:

```bash
#!/bin/bash
# 3-pass compilation engine (most compatible)

compile_with_3pass() {
    local tex_file="$1"
    local pdf_file="${tex_file%.tex}.pdf"

    echo_info "Using 3-pass engine"

    # Get commands
    local pdf_cmd=$(get_cmd_pdflatex)
    local bib_cmd=$(get_cmd_bibtex)

    if [ -z "$pdf_cmd" ] || [ -z "$bib_cmd" ]; then
        echo_error "No LaTeX installation found (native, module, or container)"
        return 1
    fi

    # Add compilation options
    local tex_dir=$(dirname "$tex_file")
    pdf_cmd="$pdf_cmd -output-directory=$tex_dir -shell-escape -interaction=nonstopmode -file-line-error"

    # Helper function for timed execution
    run_pass() {
        local cmd="$1"
        local verbose="$2"
        local desc="$3"

        echo_info "$desc"
        local start=$(date +%s)

        if [ "$verbose" = "true" ]; then
            eval "$cmd" 2>&1 | grep -v "gocryptfs not found"
            local ret=${PIPESTATUS[0]}
        else
            eval "$cmd" >/dev/null 2>&1
            local ret=$?
        fi

        local end=$(date +%s)
        echo_info "  ($(($end - $start))s)"

        return $ret
    }

    # Main compilation sequence
    local total_start=$(date +%s)
    local tex_base="${tex_file%.tex}"
    local aux_file="${tex_base}.aux"

    # Check draft mode
    if [ "$SCITEX_WRITER_DRAFT_MODE" = "true" ]; then
        # Draft: single pass only
        run_pass "$pdf_cmd $tex_file" "$SCITEX_WRITER_VERBOSE_PDFLATEX" "Single pass (draft mode)"
    else
        # Full: 3-pass compilation
        run_pass "$pdf_cmd $tex_file" "$SCITEX_WRITER_VERBOSE_PDFLATEX" "Pass 1/3: Initial"

        # Process bibliography if needed
        if [ -f "$aux_file" ]; then
            if grep -q "\\citation\|\\bibdata\|\\bibstyle" "$aux_file" 2>/dev/null; then
                run_pass "$bib_cmd $tex_base" "$SCITEX_WRITER_VERBOSE_BIBTEX" "Processing bibliography"
            fi
        fi

        run_pass "$pdf_cmd $tex_file" "$SCITEX_WRITER_VERBOSE_PDFLATEX" "Pass 2/3: Bibliography"
        run_pass "$pdf_cmd $tex_file" "$SCITEX_WRITER_VERBOSE_PDFLATEX" "Pass 3/3: Final"
    fi

    local total_end=$(date +%s)
    echo_success "3-pass compilation: $(($total_end - $total_start))s"
}
```

### 4.6 Unified Engine Interface

**File**: `scripts/shell/modules/compilation_compiled_tex_to_compiled_pdf.sh` (REFACTORED)

```bash
#!/bin/bash
# Main compilation orchestrator - delegates to engine-specific modules

# Source engine implementations
source "$(dirname ${BASH_SOURCE[0]})/engines/compile_tectonic.sh"
source "$(dirname ${BASH_SOURCE[0]})/engines/compile_latexmk.sh"
source "$(dirname ${BASH_SOURCE[0]})/engines/compile_3pass.sh"

compiled_tex_to_pdf() {
    echo_info "Converting $SCITEX_WRITER_COMPILED_TEX to PDF..."

    local tex_file="$SCITEX_WRITER_COMPILED_TEX"
    local engine="$SCITEX_WRITER_SELECTED_ENGINE"

    # Dispatch to engine-specific implementation
    case "$engine" in
        tectonic)
            compile_with_tectonic "$tex_file"
            ;;
        latexmk)
            compile_with_latexmk "$tex_file"
            ;;
        3pass)
            compile_with_3pass "$tex_file"
            ;;
        *)
            echo_error "Unknown compilation engine: $engine"
            return 1
            ;;
    esac

    local ret=$?

    # If compilation failed in auto mode, try next engine
    if [ $ret -ne 0 ] && [ "$SCITEX_WRITER_AUTO_ENGINE" = "true" ]; then
        echo_warning "Engine '$engine' failed, trying fallback..."
        # TODO: Implement fallback logic
    fi

    return $ret
}

# Existing cleanup() function unchanged
cleanup() {
    # ... (lines 163-203 unchanged)
}

main() {
    compiled_tex_to_pdf
    cleanup
}

main
```

---

## 5. Unified Error Handling

### 5.1 Error Categories

**Common errors across all engines**:

| Category | Symptoms | Tectonic | latexmk | 3-pass |
|----------|----------|----------|---------|--------|
| Missing Package | `! LaTeX Error: File not found` | Auto-downloads | Fails | Fails |
| Syntax Error | `! Undefined control sequence` | Shows line | Shows line | Shows line |
| Bibliography | `Warning: Citation undefined` | Auto-handles | Needs .bbl | Needs bibtex |
| File Not Found | `! I can't find file` | Clear error | In log | In log |
| Timeout | Process hangs | Rare | Possible | Rare |

### 5.2 Error Parser

**File**: `scripts/shell/modules/parse_compilation_errors.sh` (NEW)

```bash
#!/bin/bash
# Parse LaTeX errors from different engines

parse_tectonic_errors() {
    local output="$1"

    # Tectonic has clean JSON-like error output
    echo "$output" | grep "error:" | while read line; do
        echo_error "$line"
    done

    # Extract file:line references
    echo "$output" | grep -oP '(?<=error: ).*?:\d+' | head -5
}

parse_latexmk_errors() {
    local log_file="$1"

    # latexmk errors are in .log file
    if [ -f "$log_file" ]; then
        # Extract LaTeX errors
        grep "^!" "$log_file" | head -5

        # Extract missing files
        grep "! I can't find file" "$log_file"

        # Extract undefined references
        grep "Warning.*undefined" "$log_file" | head -3
    fi
}

parse_3pass_errors() {
    local log_file="$1"

    # Same as latexmk (both use pdflatex logs)
    parse_latexmk_errors "$log_file"
}

# Unified error reporting
report_compilation_errors() {
    local engine="$1"
    local tex_file="$2"
    local output="$3"

    local log_file="${tex_file%.tex}.log"

    case "$engine" in
        tectonic)
            parse_tectonic_errors "$output"
            ;;
        latexmk|3pass)
            parse_latexmk_errors "$log_file"
            ;;
    esac
}
```

### 5.3 Fallback Logic

When auto-detection is enabled and an engine fails:

1. **Tectonic fails** → Try latexmk
   - Reason: Might be version incompatibility or missing Tectonic-specific features

2. **latexmk fails** → Try 3-pass
   - Reason: Path resolution issues, latexmk bugs, missing dependencies

3. **3-pass fails** → Report error and exit
   - Reason: Fundamental LaTeX error that no engine can fix

**Implementation** in `compile_with_*` functions:

```bash
# At end of each engine function, add:
if [ $exit_code -ne 0 ] && [ "$SCITEX_WRITER_AUTO_ENGINE" = "true" ]; then
    echo_warning "Engine failed, will try fallback"
    return 2  # Special code: try next engine
else
    return $exit_code  # 0=success, 1=fatal error
fi
```

---

## 6. Testing Strategy

### 6.1 Test Matrix

| Scenario | Tectonic | latexmk | 3-pass |
|----------|----------|---------|--------|
| Simple document (no refs) | ✓ | ✓ | ✓ |
| With bibliography | ✓ | ✓ | ✓ |
| With figures (JPG/PNG) | ✓ | ✓ | ✓ |
| With tables (LaTeX) | ✓ | ✓ | ✓ |
| With minted (shell-escape) | ✓ | ✓ | ✓ |
| Draft mode | ✓ | ✓ | ✓ |
| Syntax error | ✓ | ✓ | ✓ |
| Missing package | ✓ | ✗ | ✗ |
| Missing .bib file | ✗ | ✗ | ✗ |
| Invalid citation | ⚠️ | ⚠️ | ⚠️ |

### 6.2 Performance Benchmarks

**Test document**: Current manuscript (~2000 words, 2 figures, 10 citations)

| Metric | Tectonic | latexmk | 3-pass | Target |
|--------|----------|---------|--------|--------|
| Cold start (first run) | 5-8s | 8-12s | 12-18s | <10s |
| Incremental (text change) | 1-3s | 3-6s | 12-18s | <5s |
| Bibliography update | 2-4s | 4-8s | 12-18s | <8s |
| Figure added | 3-5s | 5-9s | 12-18s | <10s |
| Container fallback | +2-3s | +2-3s | +2-3s | <5s overhead |

### 6.3 Test Implementation

**File**: `tests/test_compilation_engines.sh` (NEW)

```bash
#!/bin/bash
# Test all three compilation engines

set -e

SCRIPT_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
PROJECT_ROOT="$(cd $SCRIPT_DIR/.. && pwd)"

# Test cases
test_simple_document() {
    local engine="$1"
    echo "Testing simple document with $engine..."

    # Create minimal test doc
    cat > /tmp/test_simple.tex <<'EOF'
\documentclass{article}
\begin{document}
Hello World
\end{document}
EOF

    # Compile with engine
    export SCITEX_WRITER_SELECTED_ENGINE="$engine"
    $PROJECT_ROOT/scripts/shell/modules/compilation_compiled_tex_to_compiled_pdf.sh /tmp/test_simple.tex

    # Check PDF exists
    if [ -f /tmp/test_simple.pdf ]; then
        echo "✓ Simple document test passed"
        return 0
    else
        echo "✗ Simple document test FAILED"
        return 1
    fi
}

test_with_bibliography() {
    local engine="$1"
    echo "Testing bibliography with $engine..."

    # Create test doc with citations
    cat > /tmp/test_bib.tex <<'EOF'
\documentclass{article}
\begin{document}
Test citation \cite{test2020}.
\bibliography{/tmp/test}
\bibliographystyle{plain}
\end{document}
EOF

    cat > /tmp/test.bib <<'EOF'
@article{test2020,
  author = {Test Author},
  title = {Test Title},
  year = {2020}
}
EOF

    # Compile
    export SCITEX_WRITER_SELECTED_ENGINE="$engine"
    $PROJECT_ROOT/scripts/shell/modules/compilation_compiled_tex_to_compiled_pdf.sh /tmp/test_bib.tex

    # Check PDF exists and contains reference
    if [ -f /tmp/test_bib.pdf ] && pdftotext /tmp/test_bib.pdf - | grep -q "Test Author"; then
        echo "✓ Bibliography test passed"
        return 0
    else
        echo "✗ Bibliography test FAILED"
        return 1
    fi
}

# Run all tests
run_all_tests() {
    for engine in tectonic latexmk 3pass; do
        echo "========================================"
        echo "Testing engine: $engine"
        echo "========================================"

        test_simple_document "$engine"
        test_with_bibliography "$engine"

        echo ""
    done
}

# Benchmark tests
benchmark_engines() {
    echo "Benchmarking compilation speed..."

    for engine in tectonic latexmk 3pass; do
        echo "Engine: $engine"

        # Cold start
        rm -f /tmp/test_simple.pdf /tmp/test_simple.aux
        start=$(date +%s.%N)
        test_simple_document "$engine" >/dev/null 2>&1
        end=$(date +%s.%N)
        cold=$(echo "$end - $start" | bc)
        echo "  Cold start: ${cold}s"

        # Incremental (modify tex, recompile)
        echo "Modified" >> /tmp/test_simple.tex
        start=$(date +%s.%N)
        test_simple_document "$engine" >/dev/null 2>&1
        end=$(date +%s.%N)
        incremental=$(echo "$end - $start" | bc)
        echo "  Incremental: ${incremental}s"

        echo ""
    done
}

# Main
case "${1:-all}" in
    all)
        run_all_tests
        ;;
    benchmark)
        benchmark_engines
        ;;
    *)
        echo "Usage: $0 [all|benchmark]"
        exit 1
        ;;
esac
```

---

## 7. Migration Path

### Phase 1: Add Tectonic (v2.1.0)
**Status**: NEW feature, opt-in

```bash
# Default remains 3-pass (safe, compatible)
compilation:
  engine: "3pass"

# Users can opt-in to Tectonic
compilation:
  engine: "tectonic"
```

**Deliverables**:
- [ ] Tectonic command detection
- [ ] `compile_tectonic.sh` implementation
- [ ] Configuration options
- [ ] Documentation
- [ ] Basic tests

**Risk**: Low (new feature, doesn't break existing workflows)

---

### Phase 2: Fix latexmk (v2.1.1)
**Status**: BUG FIX, automatic

```bash
# Enable latexmk with BIBINPUTS fix
compilation:
  engine: "latexmk"
```

**Deliverables**:
- [ ] BIBINPUTS environment variable fix
- [ ] `compile_latexmk.sh` implementation
- [ ] Test with bibliography path resolution
- [ ] Re-enable in `compilation_compiled_tex_to_compiled_pdf.sh`

**Risk**: Medium (modifies existing behavior, but fixes known bug)

---

### Phase 3: Auto-detection (v2.2.0)
**Status**: BREAKING CHANGE (default behavior changes)

```bash
# New default: auto-detect best engine
compilation:
  engine: "auto"
  auto_order:
    - tectonic   # Fastest
    - latexmk    # Standard
    - 3pass      # Guaranteed
```

**Deliverables**:
- [ ] Auto-detection logic
- [ ] Fallback chain implementation
- [ ] Migration guide for users who want old behavior
- [ ] Comprehensive testing

**Risk**: High (changes default compilation, needs thorough testing)

---

### Phase 4: Optimization (v2.3.0)
**Status**: ENHANCEMENTS

**Features**:
- [ ] Parallel compilation for multiple documents
- [ ] Compilation cache management
- [ ] Pre-warming Tectonic bundle for offline use
- [ ] Benchmark dashboard
- [ ] Engine recommendation based on document complexity

**Risk**: Low (optional optimizations)

---

## 8. Documentation Requirements

### 8.1 User-Facing Documentation

**File**: `docs/compilation-engines.md` (NEW)

Topics to cover:
1. Overview of three engines
2. When to use each engine
3. How to select engine (CLI flag, config file)
4. Troubleshooting engine-specific issues
5. Performance comparison
6. Offline usage (Tectonic bundle)

### 8.2 Developer Documentation

**File**: `docs/dev/compilation-architecture.md` (NEW)

Topics to cover:
1. Engine interface specification
2. Adding new engines
3. Error handling patterns
4. Testing new engines
5. Container integration

### 8.3 Migration Guide

**File**: `docs/migration/v2.0-to-v2.1.md` (NEW)

Topics to cover:
1. What changed in v2.1
2. How to opt-in to new engines
3. Rollback procedure
4. Known issues
5. Performance improvements

---

## 9. Implementation Checklist

### Infrastructure (Week 1)
- [ ] Create engine-specific modules directory: `scripts/shell/modules/engines/`
- [ ] Create `select_compilation_engine.sh` module
- [ ] Extend `command_switching.src` with Tectonic/latexmk detection
- [ ] Add configuration schema to `config_manuscript.yaml`
- [ ] Add CLI flag parsing for `--engine`

### Tectonic Engine (Week 1-2)
- [ ] Implement `compile_tectonic.sh`
- [ ] Test with simple document
- [ ] Test with bibliography
- [ ] Test with figures
- [ ] Container fallback for Tectonic

### latexmk Engine (Week 2)
- [ ] Implement `compile_latexmk.sh` with BIBINPUTS fix
- [ ] Test bibliography path resolution
- [ ] Test incremental compilation
- [ ] Verify all flags work (--draft, --verbose, etc.)

### 3-Pass Engine (Week 2)
- [ ] Extract from existing code to `compile_3pass.sh`
- [ ] No functional changes (just refactoring)
- [ ] Ensure backward compatibility

### Integration (Week 3)
- [ ] Refactor `compilation_compiled_tex_to_compiled_pdf.sh` to dispatch
- [ ] Implement auto-detection logic
- [ ] Implement fallback chain
- [ ] Unified error reporting

### Testing (Week 3-4)
- [ ] Create `test_compilation_engines.sh`
- [ ] Test all engines with all scenarios
- [ ] Performance benchmarks
- [ ] Container tests (Singularity/Docker)
- [ ] Integration tests with full manuscript compilation

### Documentation (Week 4)
- [ ] User guide: `docs/compilation-engines.md`
- [ ] Developer guide: `docs/dev/compilation-architecture.md`
- [ ] Migration guide: `docs/migration/v2.0-to-v2.1.md`
- [ ] Update README with engine selection examples
- [ ] Update CHANGELOG

### Release (Week 4)
- [ ] Version bump to v2.1.0
- [ ] Release notes highlighting three engines
- [ ] Performance comparison vs Overleaf
- [ ] Social media announcement (if applicable)

---

## 10. Success Criteria

### Functional Requirements
✅ All three engines compile successfully
✅ Auto-detection works reliably
✅ Fallback chain handles failures gracefully
✅ Configuration overrides work (CLI flag > config file > default)
✅ All existing features work with all engines (draft mode, diff, etc.)
✅ Container fallbacks work for all engines

### Performance Requirements
✅ Tectonic: <3s incremental compilation
✅ latexmk: <6s incremental compilation
✅ 3-pass: <18s full compilation
✅ Auto-detection overhead: <500ms

### Quality Requirements
✅ Zero regressions in existing tests
✅ 100% test coverage for new engine modules
✅ Documentation complete and accurate
✅ No breaking changes for existing users (until v2.2.0 auto-detect default)

### Competitive Requirements
✅ Tectonic 10× faster than Overleaf for incremental edits
✅ True offline capability (Tectonic bundle)
✅ Reproducible builds (container fallbacks)
✅ User choice (flexibility not available in Overleaf)

---

## 11. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Tectonic version incompatibility | Medium | High | Container fallback, version pinning |
| latexmk BIBINPUTS doesn't fix all path issues | Medium | Medium | Keep 3-pass fallback, thorough testing |
| Users confused by three engines | Low | Medium | Clear documentation, sensible defaults |
| Performance regression | Low | High | Benchmarks before/after, A/B testing |
| Container overhead too high | Low | Medium | Optimize container warmup, cache layers |
| Breaking changes in Phase 3 (auto-detect) | Medium | High | Migration guide, deprecation warnings |

---

## 12. Open Questions

1. **Tectonic bundle management**: How do we pre-warm the bundle for offline use?
   - Option A: Include pre-built bundle in repository (large)
   - Option B: Download on first run (requires internet)
   - Option C: Provide `make tectonic-bundle` command
   - **Decision**: Option C, document in offline usage guide

2. **Container priority**: Should Tectonic-in-container be tried before latexmk-native?
   - Current: native > module > container (per command)
   - Proposed: Respect engine priority even across container boundary
   - **Decision**: TBD, test both approaches

3. **Error threshold for fallback**: How many errors before trying next engine?
   - Option A: Any non-zero exit code
   - Option B: Only specific error types (missing package, timeout)
   - **Decision**: Option A for auto-detect, Option B for explicit engine

4. **Parallel compilation**: Can we run multiple engines in parallel and pick fastest?
   - Pros: Maximum speed (first to finish wins)
   - Cons: Resource intensive, confusing logs
   - **Decision**: Defer to v2.3.0 optimization phase

---

## 13. Next Steps

**Immediate** (this week):
1. Create infrastructure (engine modules, config schema)
2. Implement Tectonic engine
3. Basic testing with simple documents

**Short-term** (next 2 weeks):
1. Implement latexmk with BIBINPUTS fix
2. Refactor 3-pass to separate module
3. Integration testing

**Medium-term** (next month):
1. Auto-detection and fallback logic
2. Comprehensive testing
3. Documentation
4. v2.1.0 release

**Long-term** (3-6 months):
1. Performance optimizations
2. Offline bundle management
3. Benchmark vs Overleaf
4. Marketing materials

---

## Appendix A: File Structure Changes

```
scitex-writer/
├── config/
│   └── config_manuscript.yaml         # Add engine selection
├── scripts/
│   └── shell/
│       ├── compile_manuscript.sh      # Add engine selection phase
│       └── modules/
│           ├── command_switching.src  # Add Tectonic/latexmk detection
│           ├── select_compilation_engine.sh  # NEW: Engine selection
│           ├── parse_compilation_errors.sh   # NEW: Error parsing
│           ├── compilation_compiled_tex_to_compiled_pdf.sh  # REFACTOR: Dispatch only
│           └── engines/               # NEW: Engine implementations
│               ├── compile_tectonic.sh
│               ├── compile_latexmk.sh
│               └── compile_3pass.sh
├── tests/
│   └── test_compilation_engines.sh    # NEW: Engine tests
└── docs/
    ├── compilation-engines.md         # NEW: User guide
    ├── dev/
    │   └── compilation-architecture.md  # NEW: Developer guide
    └── migration/
        └── v2.0-to-v2.1.md           # NEW: Migration guide
```

---

## Appendix B: Configuration Example

```yaml
# config_manuscript.yaml (v2.1.0+)

# Document metadata
document:
  type: "manuscript"
  version: "v2.1.0"

# Compilation engine selection
compilation:
  # Engine: tectonic, latexmk, 3pass, auto
  engine: "auto"

  # Auto-detection fallback order
  auto_order:
    - tectonic
    - latexmk
    - 3pass

  # Draft mode (single pass, skip bibliography)
  draft_mode: false

  # Per-engine settings
  engines:
    tectonic:
      incremental: true
      cache_dir: "./.tectonic-cache"
      bundle_dir: "./.tectonic-bundle"

    latexmk:
      incremental: true
      max_passes: 10
      set_bibinputs: true

    3pass:
      incremental: false
      verbose_passes: false

# Verbosity settings
verbosity:
  pdflatex: true
  bibtex: true
  tectonic: false  # Tectonic is verbose by default
  latexmk: false

# Citation style
citation:
  style: "unsrtnat"

# Paths
paths:
  manuscript_dir: "./01_manuscript"
  compiled_tex: "./01_manuscript/manuscript.tex"
  compiled_pdf: "./01_manuscript/manuscript.pdf"
  doc_log_dir: "./01_manuscript/logs"
  versions_dir: "./01_manuscript/archive"
  root_dir: "."
```

---

## Appendix C: CLI Examples

```bash
# Auto-detect best engine (default in v2.2.0+)
./compile.sh manuscript

# Explicit engine selection
./compile.sh manuscript --engine=tectonic
./compile.sh manuscript --engine=latexmk
./compile.sh manuscript --engine=3pass

# Draft mode with Tectonic (fastest iteration)
./compile.sh manuscript --draft --engine=tectonic

# Verbose output for debugging
./compile.sh manuscript --engine=latexmk --verbose

# Force container execution
./compile.sh manuscript --engine=tectonic --container

# Check available engines
./compile.sh manuscript --list-engines
# Output:
#   ✓ tectonic  (v0.14.1)  [Fast mode: 1-3s]
#   ✓ latexmk   (v4.77)    [Standard mode: 3-6s]
#   ✓ 3pass     (native)   [Guaranteed mode: 12-18s]

# Benchmark all engines
./compile.sh manuscript --benchmark
# Output:
#   tectonic:  2.3s (incremental: 1.1s)
#   latexmk:   4.7s (incremental: 3.2s)
#   3pass:    14.2s (incremental: 14.2s)
```

---

**END OF ARCHITECTURE DESIGN**

*This document will be updated as implementation progresses.*
