---
description: |
  [TOPIC] CLI Reference
  [DETAILS] CLI commands for scitex-writer..
tags: [scitex-writer-cli-reference]
---

# CLI Reference

```bash
scitex-writer compile [project_dir]          # Compile manuscript
scitex-writer compile --supplementary        # Compile supplementary
scitex-writer compile --revision             # Compile revision

scitex-writer export [project_dir]           # Export for submission
scitex-writer export --overleaf              # Export to Overleaf

scitex-writer bib add KEY                    # Add bibliography entry
scitex-writer bib list                       # List entries

scitex-writer mcp start                      # Start MCP server
scitex-writer mcp doctor                     # Diagnose MCP setup

scitex-writer skills list                    # List skills
scitex-writer skills get                     # Get skill content
```

## Project-local `./compile.sh` subcommands

```bash
./compile.sh manuscript                      # (also -m) compile manuscript
./compile.sh supplementary                   # (also -s) compile supplementary
./compile.sh revision                        # (also -r) compile revision

./compile.sh builds [-n N]                   # list recent build IDs (#77)
./compile.sh show <BUILD_ID>                 # show metadata for one build
```

Each compile stamps a 6-char build ID into the PDF `/Info` dictionary
(`pdfsubject=build:XXXXXX`) and records it in
`.scitex/writer/builds/builds.json`. Verify on any PDF via
`pdfinfo manuscript.pdf | grep Subject`.
