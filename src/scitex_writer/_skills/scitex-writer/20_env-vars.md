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
| `SCITEX_WRITER_LINT_STRICT` | Tighten `check-limits` + `check-overflow` warnings to errors (the legacy strict toggle). Scoped to those two checks only. | `false` | bool |
| `SCITEX_WRITER_LIMITS` | Severity for the word/reference-limit check (`off`/`warn`/`error`). Default `warn`; `--strict`/`limits.strict` tighten to `error`. | `warn` | enum |
| `SCITEX_WRITER_OVERFLOW` | Severity for the off-page overflow check (`off`/`warn`/`error`). Default `warn`; `--strict`/`overflow.strict` tighten to `error`. | `warn` | enum |
| `SCITEX_WRITER_PAPER_SYMLINK` | Severity for the `paper -> .scitex/writer` symlink check (`off`/`warn`/`error`/`repair`). Private convention — default `warn`. | `warn` | enum |
| `SCITEX_WRITER_MEDIA_PROVENANCE` | Severity for the media-symlink/provenance check on `caption_and_media/` (`off`/`warn`/`error`). Private convention — default `off`. | `off` | enum |
| `SCITEX_WRITER_REFERENCES` | Severity for the cross-reference/citation/label check (`off`/`warn`/`error`). Default `error` (a broken `\ref`/`\cite` is a real defect); `warn` reports but exits 0; `off` disables. | `error` | enum |
| `SCITEX_WRITER_FLOAT_ORDER` | Severity for the figure/table reference-order check (`off`/`warn`/`error`). Default `error`. `--level` governs only the gating exit; `--fix`/`--dry-run` always run regardless of level. | `error` | enum |
| `SCITEX_WRITER_CAPTION_FOOTNOTE` | Severity for the `\footnote`-in-`\caption{}` lint (`off`/`warn`/`error`). Default `error`. | `error` | enum |
| `SCITEX_WRITER_REF_INTEGRITY` | Severity for the pre-compile reference-integrity gate (`off`/`warn`/`error`). Default `error`. | `error` | enum |
| `SCITEX_WRITER_COMPILE_ARTIFACTS` | Severity for the POST-compile verification gate (`off`/`warn`/`error`). Default `error`. Fails loud when the compiled `.tex` references `\includegraphics` (N>0) but the PDF embeds 0 images (silent figure miss), plus secondary log deficiency signals. PDF embedding check needs poppler (`pdfimages`); skipped-with-warning when absent. | `error` | enum |

> **`references` vs `ref_integrity` are separate knobs.** `references` is the
> advisory cross-reference/citation/label *report*; `ref_integrity` is the
> *pre-compile integrity gate*. Downgrading `references` (e.g. to `off`) does
> **not** disable `ref_integrity`, so a broken `\ref` can still block a compile
> via the gate — defense in depth by design.

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
