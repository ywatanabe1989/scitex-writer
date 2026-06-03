# Container Definitions

This directory contains container definition files for reproducible LaTeX compilation.

## Available Containers

| Container | Purpose | Format |
|-----------|---------|--------|
| `texlive.def` | Full TeX Live environment | Apptainer/Singularity |
| `mermaid.def` | Mermaid diagram generation | Apptainer/Singularity |
| `Dockerfile` | Full TeX Live environment | Docker |

## Building Containers

### Preferred — scitex-writer CLI

Builds the canonical SIF under the per-package convention
(`~/.scitex/writer/containers/<tool>.sif`, operator design 8566 + sac PR #293)
via `scitex-container.apptainer.build` so the artifact ships with a
`.def-hash`, build log, and top-level symlink — the same engine sac uses for
its own `:base` / `:scitex` SIFs.

```bash
scitex-writer containers install texlive -y
scitex-writer containers install mermaid -y    # follow-up: enable when canonicalized
```

### Raw apptainer (fallback)

```bash
apptainer build texlive.sif texlive.def
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

Built containers live under `~/.scitex/writer/containers/<tool>.sif` per the
per-package convention. The legacy `./.cache/containers/<tool>_container.sif`
path is still consulted by the shell modules as a deprecated fallback for
caches built before this migration (a `[DEPRECATED]` log line fires when it's
used) — please rebuild via the `scitex-writer containers install` CLI to
land on the canonical artifact.

## Automatic Download

The bulk downloader still works and now writes to the canonical location:

```bash
./scripts/installation/download_containers.sh
```
