# Container Definitions

This directory contains container definition files for reproducible LaTeX compilation.

## Available Containers

| Container | Purpose | Format |
|-----------|---------|--------|
| `texlive.def` | Full TeX Live environment | Apptainer/Singularity |
| `mermaid.def` | Mermaid diagram generation | Apptainer/Singularity |
| `Dockerfile` | Full TeX Live environment | Docker |

## Building Containers

### Apptainer/Singularity

```bash
# Build TeX Live container
apptainer build texlive.sif texlive.def

# Build Mermaid container
apptainer build mermaid.sif mermaid.def
```

### Docker

```bash
docker build -t scitex-writer -f scripts/containers/Dockerfile .
```

## Usage

### With Apptainer

```bash
# Compile manuscript
apptainer run --bind $(pwd):/workspace texlive.sif ./compile.sh manuscript

# Generate mermaid diagrams
apptainer run --bind $(pwd):/workspace mermaid.sif mmdc -i input.mmd -o output.png
```

### With Docker

```bash
docker run --rm -v $(pwd):/workspace scitex-writer ./compile.sh manuscript
```

## Cache Location

Built containers are cached in `.cache/containers/` for faster subsequent runs.

## Automatic Download

The compilation system automatically downloads pre-built containers if available:

```bash
./scripts/installation/download_containers.sh
```
