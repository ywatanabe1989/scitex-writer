# Shared Severity Model — Design Contract (checker redesign, Part D)

> **STATUS: RATIFIED — operator signed off §9 on 2026-06-27.** The locked
> resolver `resolve_level(...)` ships in `scripts/python/_severity.py` and is
> adopted incrementally (D1: `limits` + `overflow`; D2/D3 follow). No check
> changes its effective default behavior; the contract unifies the knob.

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
| `caption_footnote` | **error**     | `\footnote` in a `\caption{}` is fatal mid-compile (PR #173) |
| `ref_integrity`    | **error**     | an unresolved `\ref`/`\cite`/supple- xref is a real defect (PR #174) |

These defaults **preserve current behavior** (see §6). `repair` is valid
**only** for `paper_symlink` (the sole check with a safe deterministic
self-fix); every other check tops out at `error`.

## 4. Precedence ladder (identical for every check)

Resolved top-down; first match wins:

1. **CLI flag** — `--level {off,warn,error}` (or the legacy `--strict` alias, §5)
2. **per-check env** — `SCITEX_WRITER_<CHECK>`, one per check:
   `SCITEX_WRITER_PAPER_SYMLINK`, `SCITEX_WRITER_MEDIA_PROVENANCE`,
   `SCITEX_WRITER_LIMITS`, `SCITEX_WRITER_OVERFLOW`, `SCITEX_WRITER_REFERENCES`,
   `SCITEX_WRITER_FLOAT_ORDER`, `SCITEX_WRITER_CAPTION_FOOTNOTE`,
   `SCITEX_WRITER_REF_INTEGRITY`
3. **project config** — `./config.yaml` → `<check>.level`
4. **user config** — `~/.scitex/writer/config.yaml` → `<check>.level`
5. **per-check default** (§3)

**`SCITEX_WRITER_LINT_STRICT`** is a **tightening-only overlay applied AFTER
resolution**: if truthy, it raises a resolved `warn` to `error` (never loosens,
never touches `off`). Per the §9 sign-off it is **scoped to `limits` + `overflow`
only** (exact back-compat) — it is NOT a global tighten-all.

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

## 7. Implementation (locked — §9 sign-off 2026-06-27)

- A tiny **stdlib-only** helper `scripts/python/_severity.py` (the check scripts
  are self-contained stdlib + optional PyYAML, so the helper is too), exposing
  the locked resolver:
  `resolve_level(check, cli_level, project_dir, *, default, env_var, legacy_strict=None)`
  → `{off,warn,error,repair}`, plus the scoped `LINT_STRICT` overlay. Each
  `check_*.py` imports it; the per-check `resolve_level`/`_read_config_level`
  bodies collapse into it.
- Public API (`checks.*`) and MCP handlers keep their signatures; `strict` bools
  stay as aliases (passed in via `legacy_strict`).
- **Config `level` YAML-bool coercion (D2):** PyYAML (YAML 1.1) coerces a bare
  `off`/`no`/`false` to `False`, so `level: off` arrives as a bool. Per §2 ("off
  disables") the shared `_read_config_level` maps `False` → `"off"`. A genuinely
  invalid value (`True` from `on`/`yes`, or a typo) is **not** silently dropped:
  one precise `[WARN]` hint is printed and the value is treated as unset (falls
  through to the default) — never crashing the build over a config typo. A
  missing key stays a silent no-op.

## 8. Migration & risk (for the operator to assess)

| check              | behavior change?                          | risk |
|--------------------|-------------------------------------------|------|
| `references`       | none — default `error` formalizes today   | low  |
| `float_order`      | none — default `error` formalizes today   | low  |
| `limits`           | none — `warn` default + `strict→error` kept; gains `--level` + env (additive) | low |
| `overflow`         | none — as `limits`                        | low  |
| `paper_symlink`    | none beyond PR #158 (`warn`); adopts shared resolver | low |
| `media_provenance` | none — `off` (PR #157); adopts shared resolver | none |
| `caption_footnote` | none — `error` (PR #173); adopts shared resolver | low |
| `ref_integrity`    | none — `error` (PR #174); adopts shared resolver | low |

**Rollout — multiple small, independently CI-gated PRs:**
1. **D1**: add `_severity.py`; adopt in `limits` + `overflow` (proves back-compat
   for `strict` / `LINT_STRICT`).
2. **D2**: adopt in `paper_symlink` + `media_provenance` (level-native already).
3. **D3**: adopt in `references` + `float_order` (formalize `error` default + add
   `--level`/env).

No check changes its *effective* default behavior; the value is one consistent
knob, env, config key, and hint style across all eight.

## 9. Sign-off — RESOLVED (operator, 2026-06-27)

All three questions ratified by the operator (relayed via scitex-dev). The
resolver `resolve_level(...)` in `scripts/python/_severity.py` is locked to:

1. **`SCITEX_WRITER_LINT_STRICT` scope** — **scoped to `limits` + `overflow`
   only** (exact back-compat). It does NOT tighten the other checks;
   `references`/`float_order` keep their `error` default and
   `paper_symlink`/`media_provenance`/`caption_footnote`/`ref_integrity` keep
   their own per-check defaults regardless of `LINT_STRICT`.
2. **`repair` level** — **`paper_symlink` only.** `media_provenance` gets **no
   `repair`** (no safe deterministic auto-fix) and its default **stays `off`**
   (the PR #157 opt-in back-compat is non-negotiable, §5); when enabled its max
   severity is `error`.
3. **Per-check env vars** — `SCITEX_WRITER_<CHECK>` **approved for all eight**
   (`…_REFERENCES`, `…_FLOAT_ORDER`, `…_LIMITS`, `…_OVERFLOW`, `…_PAPER_SYMLINK`,
   `…_MEDIA_PROVENANCE`, `…_CAPTION_FOOTNOTE`, `…_REF_INTEGRITY`), each mapping to
   the `<check>.level` config key, with precedence CLI > per-check env > project
   config > user config > per-check default.

`ref_integrity` (#174, added after this doc's first draft) folds in under the
same scheme: env `SCITEX_WRITER_REF_INTEGRITY`, key `ref_integrity.level`,
default `error`, and is **outside** the `LINT_STRICT` scope.
