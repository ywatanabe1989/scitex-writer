# Installation Guide

Complete installation instructions for SciTeX Writer for different environments and use cases.

## Table of Contents

- [Quick Start](#quick-start)
- [System Requirements](#system-requirements)
- [Installation Methods](#installation-methods)
  - [Native Installation (Recommended)](#native-installation-recommended)
  - [Container-Based](#container-based)
  - [HPC/Cluster Environments](#hpccluster-environments)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

```bash
# 1. Clone or download the repository
git clone https://github.com/ywatanabe1989/scitex-writer.git
cd scitex-writer

# 2. Run compilation (auto-checks dependencies)
./scripts/shell/compile_manuscript.sh

# 3. If dependencies missing, install suggested packages and retry
```

---

## System Requirements

### Minimum Requirements
- **OS**: Linux, macOS, or Windows (WSL2)
- **Bash**: 4.0+
- **LaTeX**: TeX Live 2020+ or equivalent

### Core Dependencies

| Package | Purpose | Ubuntu/Debian | macOS |
|---------|---------|---------------|-------|
| `texlive-latex-extra` | LaTeX core + packages | `apt-get install` | `brew install texlive` |
| `latexdiff` | Diff PDF generation | `apt-get install` | `brew install latexdiff` |
| `parallel` | Parallel job execution | `apt-get install` | `brew install parallel` |
| `imagemagick` | Image format conversion | `apt-get install` | `brew install imagemagick` |
| `ghostscript` | PDF manipulation | `apt-get install` | `brew install ghostscript` |

### Optional Dependencies

| Package | Purpose | When Needed |
|---------|---------|------------|
| `python3-pip` | Python package manager | Python integration |
| `git-lfs` | Large file storage | Binary assets in git |
| `docker` | Container runtime | Docker-based workflows |
| `singularity` | Container runtime | HPC environments |

---

## Installation Methods

### Native Installation (Recommended)

**Best for**: Local development, personal use, standard Linux/macOS systems

#### Ubuntu/Debian (Fastest)

```bash
# 1. Update package manager
sudo apt-get update

# 2. Install core dependencies
sudo apt-get install texlive-latex-extra latexdiff parallel imagemagick ghostscript

# 3. Clone repository
git clone https://github.com/ywatanabe1989/scitex-writer.git
cd scitex-writer

# 4. Test compilation
./scripts/shell/compile_manuscript.sh
```

**Expected output**:
```
INFO: =========================
INFO: Dependency Check
INFO: =========================
INFO: ✓ All dependencies found
...
SUCC: TOTAL COMPILATION TIME: 15s
```

#### macOS

```bash
# 1. Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Install dependencies
brew install texlive latexdiff parallel imagemagick ghostscript

# 3. Clone repository
git clone https://github.com/ywatanabe1989/scitex-writer.git
cd scitex-writer

# 4. Test compilation
./scripts/shell/compile_manuscript.sh
```

#### Windows (WSL2)

```bash
# 1. Enable WSL2 (Windows Terminal as Admin)
wsl --install
wsl --install Ubuntu-22.04

# 2. Open Ubuntu terminal and run Ubuntu instructions above
sudo apt-get update
sudo apt-get install texlive-latex-extra latexdiff parallel imagemagick ghostscript
git clone https://github.com/ywatanabe1989/scitex-writer.git
cd scitex-writer
./scripts/shell/compile_manuscript.sh
```

---

### Container-Based

**Best for**: Guaranteed consistency, CI/CD, no local setup needed

#### Docker

```bash
# 1. Build image (optional, pulls pre-built by default)
docker build -t scitex-writer:latest .

# 2. Run container
docker run --rm -v $(pwd):/work scitex-writer:latest \
  ./scripts/shell/compile_manuscript.sh

# 3. View output
ls -la manuscript.pdf
```

**docker-compose.yml** example:
```yaml
version: '3'
services:
  scitex:
    image: scitex-writer:latest
    volumes:
      - .:/work
    command: ./scripts/shell/compile_manuscript.sh
```

#### Singularity (HPC)

```bash
# 1. Build Singularity image
singularity build scitex-writer.sif docker://ywatanabe1989/scitex-writer:latest

# 2. Run compilation
singularity exec scitex-writer.sif ./scripts/shell/compile_manuscript.sh

# 3. Or bind to local directory
singularity run --bind $(pwd):/work scitex-writer.sif
```

---

### HPC/Cluster Environments

**Best for**: Scientific computing clusters, job schedulers (SLURM, PBS)

#### Using Module System

```bash
# 1. Load TeX module (cluster-specific)
module load texlive/2023  # or similar
module load latexdiff
module load parallel

# 2. Clone repository
git clone https://github.com/ywatanabe1989/scitex-writer.git
cd scitex-writer

# 3. Compile
./scripts/shell/compile_manuscript.sh
```

#### SLURM Job Submission

```bash
#!/bin/bash
#SBATCH --job-name=scitex
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=00:30:00
#SBATCH --output=slurm-%j.log

module load texlive latexdiff parallel

cd /path/to/scitex-writer
./scripts/shell/compile_manuscript.sh
```

Submit with:
```bash
sbatch submit_job.sh
```

#### Using Singularity on HPC

```bash
#!/bin/bash
#SBATCH --job-name=scitex
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4

singularity exec /path/to/scitex-writer.sif \
  ./scripts/shell/compile_manuscript.sh
```

---

## Verification

### Test Basic Functionality

```bash
# 1. Check dependency availability
./scripts/shell/compile_manuscript.sh --help

# 2. Run dependency check (no compilation)
./scripts/shell/modules/check_dependancy_commands.sh

# 3. Test with sample manuscript
./scripts/shell/compile_manuscript.sh

# 4. Check output
ls -lah 01_manuscript/manuscript.pdf
```

### Expected Results

After successful installation:

```
✓ PDF compiled: 01_manuscript/manuscript.pdf
✓ Diff generated: 01_manuscript/manuscript_diff.pdf
✓ Logs created: scripts/shell/.compile_manuscript.sh.log
✓ Compilation time: ~15-30 seconds (first run)
                    ~5-10 seconds (subsequent runs with caching)
```

### Run Test Suite

```bash
# Run all tests
./tests/run_all_tests.sh
```

---

## Troubleshooting

### Common Issues

#### Issue: "command not found: pdflatex"

**Solution**: Install LaTeX
```bash
# Ubuntu/Debian
sudo apt-get install texlive-latex-extra

# macOS
brew install texlive

# Verify
which pdflatex  # Should show path
```

#### Issue: "latexdiff: command not found"

**Solution**: Install latexdiff
```bash
# Ubuntu/Debian
sudo apt-get install latexdiff

# macOS
brew install latexdiff

# Verify
latexdiff --version
```

#### Issue: "parallel: command not found"

**Solution**: Install GNU parallel
```bash
# Ubuntu/Debian
sudo apt-get install parallel

# macOS
brew install parallel

# Verify
parallel --version
```

#### Issue: "Logs are empty" or "Output not captured"

**Solution**: Check log directory permissions
```bash
# Make logs directory writable
chmod 755 scripts/shell/
touch scripts/shell/.compile_manuscript.sh.log
chmod 644 scripts/shell/.compile_manuscript.sh.log

# Re-run compilation
./scripts/shell/compile_manuscript.sh
```

#### Issue: "Container not found" or "Singularity image error"

**Solution**: Pull/build container
```bash
# Docker
docker pull ywatanabe1989/scitex-writer:latest

# Singularity
singularity pull scitex-writer.sif docker://ywatanabe1989/scitex-writer:latest
```

### Getting Help

If you encounter issues:

1. **Check logs**: `cat scripts/shell/.compile_manuscript.sh.log`
2. **Run dependency check**: `./scripts/shell/modules/check_dependancy_commands.sh`
3. **Check documentation**: Read relevant guide in `docs/`
4. **Report issue**: https://github.com/ywatanabe1989/scitex-writer/issues
5. **Include in report**:
   - OS and version
   - LaTeX version: `pdflatex --version`
   - Bash version: `bash --version`
   - Full error message and logs

---

## Next Steps

After successful installation:

1. **Quick Start**: Read [`01_GUIDE_QUICK_START.md`](01_GUIDE_QUICK_START.md)
2. **Content Creation**: See [`01_GUIDE_CONTENT_CREATION.md`](01_GUIDE_CONTENT_CREATION.md)
3. **Bibliography Management**: Check [`01_GUIDE_BIBLIOGRAPHY.md`](01_GUIDE_BIBLIOGRAPHY.md)
4. **Architecture Details**: Review [`02_ARCHITECTURE_IMPLEMENTATION.md`](02_ARCHITECTURE_IMPLEMENTATION.md)

---

## Version Information

- **Tested on**:
  - Ubuntu 20.04, 22.04, 24.04
  - macOS 12+
  - Windows 11 (WSL2)
  - CentOS/RHEL 7+
- **LaTeX**: TeX Live 2020+ recommended
- **Python**: 3.8+ for Python API
- **Last Updated**: 2025-11-10
