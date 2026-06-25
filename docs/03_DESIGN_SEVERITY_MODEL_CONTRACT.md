# Shared Severity Model — Design Contract (checker redesign, Part D)

> **STATUS: PROPOSAL — awaiting operator sign-off. NO implementation code lands
> until this contract is approved.** This document defines the target contract
> and the migration; it changes no behavior on its own.

## 1. Motivation

The check subsystem currently has **two divergent severity mechanisms**:

- **boolean `strict`** — `check_limits` / `check_overflow`: a finding is a
  *warning* by default; `strict=True` (or `<check>.strict` config, or
  `SCITEX_WRITER_LINT_STRICT=1`) promotes it to an *error* (non-zero exit).
- **`level` enum** — `check_paper_symlink` (`off|warn|error|repair`) and
  `check_media_provenance` (`off|warn|error`): a per-check env var + config key
  resolve the level.

`check_references` / `check_float_order` have ad-hoc severity (broken refs are
just errors). The knobs, env-var names, and hint styles differ per check. This
contract unifies them into **one** `off|warn|error(+repair)` model with **one**
precedence ladder, **without breaking any current caller, config, or env var**.

## 2. The model

Every check resolves a single `level`:

| level    | meaning                                                                 | exit |
|----------|-------------------------------------------------------------------------|------|
| `off`    | check is a no-op; prints a one-line "disabled" note only                | 0    |
| `warn`   | findings reported as `[WARN]` (non-fatal)                               | 0    |
| `error`  | findings reported as `[FAIL]`; exit 1 if **any** finding                | 1    |
| `repair` | **only** where a check can safely self-fix (`paper_symlink`): `error` semantics + fix safe cases | 0/1 |

`repair` is **not** added to checks that cannot safely auto-fix (see §7 Q2).

## 3. Per-check default levels (defaults differ by check — by design)

| check              | default level | rationale                                              |
|--------------------|---------------|--------------------------------------------------------|
| `references`       | **error**     | a broken `\ref`/`\cite`/label is a real defect         |
| `float_order`      | **error**     | out-of-order floats are a real defect                  |
| `limits`           | **warn**      | today's default (over-limit is advisory)               |
| `overflow`         | **warn**      | today's default (overfull box is advisory)             |
| `paper_symlink`    | **warn**      | private convention; surfaced but non-fatal (PR #158)   |
| `media_provenance` | **off**       | private convention; opt-in (PR #157)                   |

These defaults **preserve current behavior** (see §6).

## 4. Precedence ladder (identical for every check)

Resolved top-down; first match wins:

1. **CLI flag** — `--level {off,warn,error}` (or the legacy `--strict` alias, §5)
2. **per-check env** — `SCITEX_WRITER_<CHECK>` (existing:
   `SCITEX_WRITER_PAPER_SYMLINK`, `SCITEX_WRITER_MEDIA_PROVENANCE`; new, additive:
   `SCITEX_WRITER_LIMITS`, `SCITEX_WRITER_OVERFLOW`, `SCITEX_WRITER_REFERENCES`,
   `SCITEX_WRITER_FLOAT_ORDER`)
3. **project config** — `./config.yaml` → `<check>.level`
4. **user config** — `~/.scitex/writer/config.yaml` → `<check>.level`
5. **per-check default** (§3)

**Global `SCITEX_WRITER_LINT_STRICT`** is a **tightening-only overlay applied
AFTER resolution**: if truthy, it raises a resolved `warn` to `error` (never
loosens, never touches `off`). Its scope is the open question in §7 Q1.

## 5. Back-compat — NON-NEGOTIABLE

Everything below keeps working **identically to today**:

- **`strict=True`** param on `checks.limits` / `checks.overflow` and their
  handlers → alias for `level=error`. **Tightening-only**: `strict=True` raises
  to `error`; `strict=False` is a no-op (never loosens a config/env-set level).
- **`limits.strict` / `overflow.strict`** config booleans → same `→ error`
  tightening-only alias.
- **`SCITEX_WRITER_LINT_STRICT=1`** → the global overlay in §4 (`warn→error`).
- Public API signatures (`checks.limits(..., strict=...)`, etc.) are **unchanged**;
  `strict` simply becomes sugar over the level model. Existing callers and CI
  paths are unaffected.

## 6. Output contract (unchanged surface)

- Every check **keeps emitting the exact line**
  `Summary: N passed, N warnings, N errors`. The MCP handler
  (`_extract_summary`, `_checks.py`) parses this with a fixed regex — the format
  **must not change**.
- Uniform **fail-loud-with-hints**: each finding prints `[WARN]`/`[FAIL]` plus a
  one-line actionable hint (today's `log_warn`/`log_fail`/`log_detail` pattern).
- Exit code is `1` iff `FAIL_COUNT > 0` (i.e. `level=error` with ≥1 finding),
  else `0`. `off` is always `0`.

## 7. Implementation sketch (for AFTER sign-off)

- A tiny **stdlib-only** helper `scripts/python/_severity.py` (the check scripts
  are self-contained stdlib + optional PyYAML, so the helper must be too),
  exposing one resolver:
  `resolve_level(check, cli_level, project_dir, *, default, env_var, legacy_strict=None)`
  → `level`, plus the `LINT_STRICT` overlay. Each `check_*.py` imports it; the
  current per-check `resolve_level`/`_read_config_level` bodies collapse into it.
- Public API (`checks.*`) and MCP handlers keep their signatures; `strict` bools
  stay as aliases.

## 8. Migration & risk (for the operator to assess)

| check              | behavior change?                          | risk |
|--------------------|-------------------------------------------|------|
| `references`       | none — default `error` formalizes today   | low  |
| `float_order`      | none — default `error` formalizes today   | low  |
| `limits`           | none — `warn` default + `strict→error` kept; gains `--level` + env (additive) | low |
| `overflow`         | none — as `limits`                        | low  |
| `paper_symlink`    | none beyond PR #158 (`warn`); adopts shared resolver | low |
| `media_provenance` | none — `off` (PR #157); adopts shared resolver | none |

**Rollout — multiple small, independently CI-gated PRs:**
1. **D1**: add `_severity.py`; adopt in `limits` + `overflow` (proves back-compat
   for `strict` / `LINT_STRICT`).
2. **D2**: adopt in `paper_symlink` + `media_provenance` (level-native already).
3. **D3**: adopt in `references` + `float_order` (formalize `error` default + add
   `--level`/env).

No check changes its *effective* default behavior; the value is one consistent
knob, env, config key, and hint style across all six.

## 9. Open questions for sign-off

1. **`SCITEX_WRITER_LINT_STRICT` scope** — keep it scoped to `limits` + `overflow`
   (exact back-compat; **recommended**), or make it a global "tighten every
   check to error"? The latter would change behavior for `references`/`float_order`
   (already error) and could surprise on `paper_symlink`/`media_provenance`.
2. **`repair` for `media_provenance`?** Proposed **no** — it cannot safely
   auto-generate a missing artifact from a script; surfacing is the right action.
3. **New per-check env var names** (`SCITEX_WRITER_LIMITS`, `…_OVERFLOW`,
   `…_REFERENCES`, `…_FLOAT_ORDER`) — acceptable, or prefer a different scheme?
