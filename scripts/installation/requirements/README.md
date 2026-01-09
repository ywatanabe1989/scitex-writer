# Dependency Management

Dependency specifications for SciTeX Writer.

## Installation

### Automated Installation

Install all dependencies automatically:

```bash
./scripts/installation/requirements/install.sh
```

This will detect your system and install:
- System packages (LaTeX, ghostscript, imagemagick, etc.)
- yq (Go version) for YAML processing
- Python packages (xlsx2csv, csv2latex, etc.)

### Selective Installation

Install only specific dependencies:

```bash
# System packages only
./scripts/installation/requirements/install.sh --system-only

# Python packages only
./scripts/installation/requirements/install.sh --python-only

# yq only
./scripts/installation/requirements/install.sh --yq-only
```

## Files

### `system-debian.txt`
System packages for Debian/Ubuntu systems (apt-get).

**Usage:**
```bash
xargs sudo apt-get install -y < requirements/system-debian.txt
```

### `system-macos.txt`
System packages for macOS (Homebrew).

**Usage:**
```bash
while read pkg; do brew install "$pkg"; done < requirements/system-macos.txt
```

### `python.txt`
Python package dependencies.

**Usage:**
```bash
pip install -r requirements/python.txt
```

### `install.sh`
Universal installer script that handles all dependencies.

**Features:**
- Automatic system detection (Debian/Ubuntu, macOS)
- Installs system packages, yq, and Python packages
- Colored output and error handling
- Selective installation modes

## Container-Based Installation

For isolation and reproducibility:

### Docker

```bash
# Build the container
docker build -t scitex-writer .

# Run compilation
docker run --rm -v $(pwd):/workspace scitex-writer ./compile.sh manuscript
```

### Apptainer/Singularity

```bash
# Build the container
apptainer build scitex-writer.sif scitex-writer.def

# Run compilation
apptainer run scitex-writer.sif ./compile.sh manuscript
```

## Platform-Specific Notes

### Linux (Debian/Ubuntu)

All dependencies are available through apt:

```bash
./requirements/install.sh
```

### macOS

Requires Homebrew. After installation, update TeX Live Manager:

```bash
./requirements/install.sh
sudo tlmgr update --self
sudo tlmgr install collection-latexextra collection-fontsrecommended
```

### Windows (WSL2)

Use the Linux instructions within WSL2, or use Docker Desktop.

## Troubleshooting

### yq Version Issues

This project uses the **Go-based yq** (mikefarah/yq), not the Python-based one.

Check your yq version:
```bash
yq --version
```

Should output something like: `yq (https://github.com/mikefarah/yq/) version...`

If you have the wrong version:
```bash
./requirements/install.sh --yq-only
```

Or use the yq wrapper:
```bash
./scripts/shell/modules/yq_wrapper.sh detect
```

### LaTeX Packages Missing

If compilation fails with missing LaTeX packages:

**Debian/Ubuntu:**
```bash
# Install full TeX Live (large, ~5GB)
sudo apt-get install texlive-full

# Or install specific missing packages
sudo apt-get install texlive-<package-name>
```

**macOS:**
```bash
# Use TeX Live Manager
sudo tlmgr install <package-name>
```

### Python Package Conflicts

Use a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements/python.txt
```

## CI/CD Integration

GitHub Actions workflows automatically use these requirements:

- `.github/workflows/citation-style-test.yml` - Uses yq wrapper
- `.github/workflows/compile-test.yml` - Uses system-debian.txt
- `.github/workflows/python-tests.yml` - Uses python.txt

## Dependencies Overview

### System Dependencies

| Package | Purpose |
|---------|---------|
| texlive-* | LaTeX distribution |
| latexdiff | Generate diff PDFs |
| ghostscript | PDF manipulation |
| imagemagick | Image conversion |
| perl | Script execution |
| parallel | Parallel processing |

### Python Dependencies

| Package | Purpose |
|---------|---------|
| xlsx2csv | Excel to CSV conversion |
| csv2latex | CSV to LaTeX tables |
| pyyaml | YAML configuration |

### Additional Tools

| Tool | Purpose |
|------|---------|
| yq (Go) | YAML processing in shell scripts |

## Updating Dependencies

### Adding New Python Package

1. Add to `requirements/python.txt`
2. Test installation: `pip install -r requirements/python.txt`
3. Update this README if needed

### Adding New System Package

1. Add to `requirements/system-debian.txt` and/or `requirements/system-macos.txt`
2. Test with `install.sh`
3. Update container definitions (Dockerfile, scitex-writer.def)
4. Update CI workflows if needed

## Version Pinning

We use flexible version pinning:

- `package>=1.0.0` - Minimum version
- `package==1.0.0` - Exact version (use sparingly)

This balances reproducibility with compatibility.

## Support

For issues with dependencies:

1. Check this README's Troubleshooting section
2. Check GitHub Issues: https://github.com/ywatanabe1989/scitex-writer/issues
3. Try the container-based approach for guaranteed compatibility
