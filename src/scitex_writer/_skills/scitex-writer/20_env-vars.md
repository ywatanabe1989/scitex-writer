---
description: |
  [TOPIC] scitex-writer — Environment Variables
  [DETAILS] Environment variables read by scitex-writer at import / runtime. Follow SCITEX_<MODULE>_* convention — see general/10_arch-environment-variables.md..
tags: [scitex-writer-env-vars]
---

# scitex-writer — Environment Variables

## Paths & output

| Variable | Purpose | Default | Type |
|---|---|---|---|
| `SCITEX_WRITER_ROOT` | Root directory for manuscript projects. | `~/proj` | path |
| `SCITEX_WORKING_DIR` | Current working project directory (overrides `SCITEX_WRITER_ROOT`). | `$PWD` | path |
| `SCITEX_WRITER_GUIDELINE_DIR` | Directory with custom writing-guideline YAMLs. | bundled | path |
| `SCITEX_WRITER_PROMPT_DIR` | Directory with custom LLM prompt templates. | bundled | path |

## Compilation

| Variable | Purpose | Default | Type |
|---|---|---|---|
| `SCITEX_WRITER_ENGINE` | LaTeX engine (`pdflatex`, `xelatex`, `lualatex`). | `pdflatex` | string |
| `SCITEX_WRITER_DRAFT_MODE` | Render manuscript in draft mode (faster, no figures). | `false` | bool |
| `SCITEX_WRITER_DARK_MODE` | Render PDF with dark page + light text (preview only; equivalent to the `-dm`/`--dark-mode` flag and `theme: dark` config). Does NOT adapt figures — they stay light, so use light mode for submission. | `false` | bool |
| `SCITEX_WRITER_VERBOSE_PDFLATEX` | Forward full pdflatex output to stderr. | `false` | bool |
| `SCITEX_WRITER_VERBOSE_BIBTEX` | Forward full bibtex output to stderr. | `false` | bool |
| `SCITEX_STYLE` | Citation / style override (shared with scitex-plt). | `default` | string |

## Pre-compile / post-compile checks (severity)

Each check resolves a severity; precedence is the CLI flag > the env var below >
project `./config.yaml` > user `~/.scitex/writer/config.yaml` > the per-check
default. Setting `off` disables a check; `warn` reports but exits 0; `error`
exits non-zero.

| Variable | Purpose | Default | Type |
|---|---|---|---|
| `SCITEX_WRITER_LINT_STRICT` | Tighten `check-limits` + `check-overflow` warnings to errors (the legacy strict toggle). | `false` | bool |
| `SCITEX_WRITER_PAPER_SYMLINK` | Severity for the `paper -> .scitex/writer` symlink check (`off`/`warn`/`error`/`repair`). Private convention — default `warn`. | `warn` | enum |
| `SCITEX_WRITER_MEDIA_PROVENANCE` | Severity for the media-symlink/provenance check on `caption_and_media/` (`off`/`warn`/`error`). Private convention — default `off`. | `off` | enum |

## Branding & naming

| Variable | Purpose | Default | Type |
|---|---|---|---|
| `SCITEX_WRITER_ALIAS` | CLI alias name used in help text. | `scitex writer` | string |
| `SCITEX_WRITER_BRAND` | Branding token injected into templates. | `SciTeX` | string |

## Guidelines / Asta prompts

| Variable | Purpose | Default | Type |
|---|---|---|---|
| `SCITEX_WRITER_GUIDELINE_ABSTRACT` | Override path for the abstract guideline YAML. | bundled | path |
| `SCITEX_WRITER_PROMPT_ASTA_COAUTHORS` | Asta coauthors-prompt override path. | bundled | path |
| `SCITEX_WRITER_PROMPT_ASTA_RELATED` | Asta related-work prompt override path. | bundled | path |

## Cross-package

| Variable | Owner | Purpose |
|---|---|---|
| `SCITEX_UI_STATIC` | scitex-ui | Static-asset path used when embedding figures produced by the UI pipeline. |

## Feature flags

- **opt-in:** `SCITEX_WRITER_DRAFT_MODE=true`, `SCITEX_WRITER_DARK_MODE=true`,
  `SCITEX_WRITER_VERBOSE_PDFLATEX=true`, `SCITEX_WRITER_VERBOSE_BIBTEX=true`
  — all off by default to keep production compilation clean.
- No opt-out flags.

## Audit

```bash
grep -rhoE 'SCITEX_[A-Z0-9_]+' $HOME/proj/scitex-writer/src/ | sort -u
```
