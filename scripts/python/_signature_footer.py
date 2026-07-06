#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: scripts/python/_signature_footer.py
# Purpose: Resolve + render the OPT-IN, DEFAULT-OFF, VISIBLE on-page footer
#          "Compiled by scitex-writer v<version>". This is DISTINCT from the
#          invisible PDF metadata signature (pdfcreator={Compiled by
#          scitex-writer vX}, emitted via 00_shared/scitex_writer_version.tex,
#          which is always present) -- this module adds a visible page footer
#          the operator can enable to advertise SciTeX across their papers.
#
#          Feature TOGGLE (boolean on/off), NOT a severity level. Precedence
#          ladder (first decisive tier wins), mirroring _resolve_dark_mode and
#          the _severity resolver:
#            1. CLI flag                                   (opt-in; forces ON)
#            2. env SCITEX_WRITER_SIGNATURE_FOOTER         (set & non-empty)
#            3. project ./config.yaml   signature_footer:  <bool>
#            4. user ~/.scitex/writer/config.yaml  signature_footer: <bool>
#            5. default OFF
#          The project/user config tiers reuse the shared config-reading
#          machinery in _severity.read_config_bool (same optional-PyYAML load +
#          YAML-bool coercion + path resolution) rather than reinventing it.
#
# Self-contained: stdlib + optional PyYAML (via _severity). No public-API
# change to the compile flow beyond the flattener wiring.

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _severity import read_config_bool  # noqa: E402

# ---------------------------------------------------------------------------
# SINGLE SOURCE OF TRUTH for the feature-flag name.
#
# PROVISIONAL: the operator is coordinating the shared opt-in-knob naming with
# scitex-dev. Keep the env-var / config-key spelling in THIS ONE PLACE so a
# later rename to match scitex-dev's shared feature-flag contract is a one-line
# change (do NOT hard-code the string anywhere else).
# ---------------------------------------------------------------------------
SIGNATURE_FOOTER_ENV = "SCITEX_WRITER_SIGNATURE_FOOTER"
SIGNATURE_FOOTER_CONFIG_KEY = "signature_footer"

# Unique marker prepended to the inlined footer block; also the idempotency
# sentinel so a repeated flatten does not stack a second copy (mirrors
# DARK_MODE_SENTINEL in compile_tex_structure.py).
SIGNATURE_FOOTER_SENTINEL = "% SciTeX signature footer (inlined at compile time)"

# Token in 00_shared/latex_styles/signature_footer.tex replaced with the
# resolved writer version just before injection.
VERSION_PLACEHOLDER = "__SCITEX_WRITER_VERSION__"

_TRUTHY = ("1", "true", "yes", "on")


def _env_bool(value):
    """True iff ``value`` is a truthy token (1/true/yes/on)."""
    return value.strip().lower() in _TRUTHY


def resolve_signature_footer_enabled(cli_flag, project_dir, *, environ=None):
    """Resolve whether the visible signature footer is enabled.

    Parameters
    ----------
    cli_flag : bool
        The ``--signature-footer`` store_true flag. Opt-in only: True forces
        ON; False is a no-op that falls through (it never forces OFF), exactly
        like ``_resolve_dark_mode``'s ``explicit_flag``.
    project_dir : str or Path
        Project root holding ``./config.yaml``.
    environ : mapping or None
        Environment mapping to read (defaults to ``os.environ``; injectable
        for tests without monkeypatch).

    Returns
    -------
    bool
        True when any tier turns the footer ON; default False.
    """
    if cli_flag:
        return True
    env = os.environ if environ is None else environ
    raw = env.get(SIGNATURE_FOOTER_ENV)
    if raw is not None and raw.strip() != "":
        return _env_bool(raw)
    project = read_config_bool(
        Path(project_dir) / "config.yaml", SIGNATURE_FOOTER_CONFIG_KEY
    )
    if project is not None:
        return project
    # Path.home() is resolved at call time (honors a changed $HOME) -- matches
    # the sibling _severity user-config tier.
    user = read_config_bool(
        Path.home() / ".scitex" / "writer" / "config.yaml",
        SIGNATURE_FOOTER_CONFIG_KEY,
    )
    if user is not None:
        return user
    return False


def resolve_writer_version(*, environ=None, repo_root=None):
    """Resolve the scitex-writer version string for the footer.

    Mirrors the codebase's existing resolution for the pdfcreator metadata: the
    shell ``config/load_config.sh`` exports ``SCITEX_WRITER_VERSION`` (read from
    a ``VERSION`` file), and ``_tex_signature.generate_signature`` falls back to
    ``pyproject.toml``. Order:
        env SCITEX_WRITER_VERSION (set by load_config.sh, if not "unknown")
        -> repo-root VERSION file
        -> pyproject.toml [project] version
        -> "unknown"
    """
    env = os.environ if environ is None else environ
    val = env.get("SCITEX_WRITER_VERSION", "").strip()
    if val and val.lower() != "unknown":
        return val
    # scripts/python/_signature_footer.py -> repo root is parent.parent.parent
    root = (
        Path(repo_root)
        if repo_root is not None
        else Path(__file__).resolve().parent.parent.parent
    )
    vfile = root / "VERSION"
    try:
        if vfile.exists():
            text = vfile.read_text(encoding="utf-8").strip()
            if text:
                return text
    except OSError:
        pass
    pyproject = root / "pyproject.toml"
    try:
        with open(pyproject, "r", encoding="utf-8") as handle:
            for line in handle:
                if line.startswith("version"):
                    return line.split("=")[1].strip().strip('"').strip("'")
    except Exception:
        pass
    return "unknown"


def build_footer_injection(styles_dir, version):
    """Build the LaTeX block to inline for the footer, or ''.

    Reads ``00_shared/latex_styles/signature_footer.tex``, substitutes the
    version placeholder, and prepends the idempotency sentinel. Returns '' when
    the style file is missing -- an advertising footer must never abort a
    compile (fail-safe), and '' also lets the caller skip injection cleanly.
    """
    style_file = Path(styles_dir) / "signature_footer.tex"
    if not style_file.exists():
        return ""
    content = style_file.read_text(encoding="utf-8").replace(
        VERSION_PLACEHOLDER, version
    )
    return "\n" + SIGNATURE_FOOTER_SENTINEL + "\n" + content + "\n"


__all__ = [
    "SIGNATURE_FOOTER_ENV",
    "SIGNATURE_FOOTER_CONFIG_KEY",
    "SIGNATURE_FOOTER_SENTINEL",
    "VERSION_PLACEHOLDER",
    "resolve_signature_footer_enabled",
    "resolve_writer_version",
    "build_footer_injection",
]

# EOF
