#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: scripts/python/render_clew_toggles.py
# Purpose: Pre-compile step -- resolve the WRITER-side clew presentation opt-in
#          from config/env and emit 00_shared/clew_presentation_toggles.tex,
#          which flips the \clewpres* LaTeX \newif toggles. This is the ONE knob
#          the operator asked for: `clew_presentation: on` turns the WHOLE
#          page-1 provenance set on (markers + badge + legend + explainer +
#          signature) in one place. The toggles are WRITER presentation config,
#          NOT clew data (clew owns claims.json; writer owns whether/how to show
#          the marks). packages.tex \input's the emitted file AFTER
#          clew_presentation.tex (which defines the \newif's), so it overrides
#          the default-off toggles.
#
#          Precedence (highest -> lowest):
#            1. env SCITEX_WRITER_CLEW_PRESENTATION  (on/off master)
#            2. project .scitex/writer/config.yaml   clew_presentation
#            3. off (all toggles false -> no marks; the file is removed)
#
#          `clew_presentation` may be a scalar master switch (on/true/yes ->
#          the full set) or a mapping of individual toggles
#          (markers/badge/legend/explainer/signature/attest). A mapping is
#          explicit per-key (absent key = off).
#
#          FAIL LOUD on a malformed config value; no-op (remove any stale file)
#          when off so a disabled run never re-injects toggles.
#
# Usage: python render_clew_toggles.py [project_dir]

import os
import sys
from pathlib import Path

CONFIG_YAML = ".scitex/writer/config.yaml"
OUTPUT_TEX = "00_shared/clew_presentation_toggles.tex"
ENV_VAR = "SCITEX_WRITER_CLEW_PRESENTATION"

# The \newif toggles defined in clew_presentation.tex (do NOT emit one whose
# \newif is undefined or LaTeX errors).
_KNOWN = (
    "markers",
    "badge",
    "legend",
    "explainer",
    "signature",
    "attest",
    "legend_first",
)
# The co-author-facing "full set" a master ON enables. `legend_first` is
# DELIBERATELY excluded: master-on already enables end-of-doc `legend`, so
# adding `legend_first` too would render the legend twice (page-1 top AND
# end-of-doc). It is opt-in ONLY (a mapping key or the env master cannot turn
# it on) so an author enables it knowingly.
_MASTER_SET = ("markers", "badge", "legend", "explainer", "signature")


# Config key -> LaTeX \newif stem. A \newif control sequence cannot contain an
# underscore, so `legend_first` maps to `\clewpreslegendfirst`. Keys without an
# underscore map to themselves.
def _macro_stem(name):
    return name.replace("_", "")


_TRUTHY = ("1", "true", "yes", "on")
_FALSY = ("0", "false", "no", "off")


def _read_config_value(project_dir):
    """Return the raw `clew_presentation` value from the project config, or None
    (PyYAML optional -- absent it, only env resolves)."""
    cfg = Path(project_dir) / CONFIG_YAML
    if not cfg.is_file():
        return None
    try:
        import yaml
    except ImportError:
        return None
    try:
        data = yaml.safe_load(cfg.read_text(encoding="utf-8")) or {}
    except Exception:
        return None
    return data.get("clew_presentation") if isinstance(data, dict) else None


def _scalar_bool(value):
    """True/False for a scalar switch, or None if it is not a scalar switch."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        low = value.strip().lower()
        if low in _TRUTHY:
            return True
        if low in _FALSY:
            return False
    return None


def resolve_toggles(config_value, env_value):
    """Resolve {toggle_name: bool} from the config value + env override.

    env (a scalar master switch) wins. A mapping config is explicit per-key.
    Raises ValueError on a malformed value (fail-loud).
    """
    # env master override (highest precedence)
    env_bool = _scalar_bool(env_value) if env_value not in (None, "") else None
    if env_bool is True:
        return {t: (t in _MASTER_SET) for t in _KNOWN}
    if env_bool is False:
        return {t: False for t in _KNOWN}
    if env_value not in (None, ""):
        raise ValueError(f"{ENV_VAR}={env_value!r} is not on/off")

    if config_value is None:
        return {t: False for t in _KNOWN}

    master = _scalar_bool(config_value)
    if master is True:
        return {t: (t in _MASTER_SET) for t in _KNOWN}
    if master is False:
        return {t: False for t in _KNOWN}

    if isinstance(config_value, dict):
        toggles = {t: False for t in _KNOWN}
        for key, val in config_value.items():
            name = str(key).strip().lower()
            if name not in _KNOWN:
                continue  # ignore unknown/future keys (no defined \newif)
            b = _scalar_bool(val)
            if b is None:
                raise ValueError(f"clew_presentation.{name}={val!r} is not true/false")
            toggles[name] = b
        return toggles

    raise ValueError(f"clew_presentation={config_value!r} must be on/off or a mapping")


def render_toggles_tex(toggles):
    r"""Emit \clewpres<name>true for each enabled toggle (default is false, so
    disabled ones need no line)."""
    lines = [
        "%% Auto-generated by render_clew_toggles.py from "
        ".scitex/writer/config.yaml (clew_presentation).",
        "%% Do not edit. Sets the clew presentation \\newif toggles; \\input "
        "AFTER clew_presentation.tex.",
    ]
    for name in _KNOWN:
        if toggles.get(name):
            lines.append(f"\\clewpres{_macro_stem(name)}true")
    return "\n".join(lines) + "\n"


def main(argv):
    project_dir = Path(argv[1] if len(argv) > 1 else ".").resolve()
    out = project_dir / OUTPUT_TEX

    try:
        toggles = resolve_toggles(
            _read_config_value(project_dir), os.environ.get(ENV_VAR)
        )
    except ValueError as exc:
        print(f"ERRO:     Invalid clew_presentation config: {exc}", file=sys.stderr)
        return 1

    # Always clear a stale toggles file first so a now-OFF run never re-injects.
    try:
        out.unlink()
    except OSError:
        pass

    if not any(toggles.values()):
        print("INFO:     Clew presentation OFF (no toggles emitted).")
        return 0

    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_toggles_tex(toggles), encoding="utf-8")
    except OSError as exc:
        print(f"ERRO:     Cannot write {out}: {exc}", file=sys.stderr)
        return 1

    enabled = ", ".join(t for t in _KNOWN if toggles[t])
    print(f"INFO:     Clew presentation toggles: {enabled}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

# EOF
