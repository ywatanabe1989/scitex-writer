#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: scripts/python/check_paper_symlink.py
# Purpose: Detect (and optionally repair) drift in the top-level `paper`
#          convenience symlink that should point at the canonical manuscript
#          at `<project>/.scitex/writer`.
#
#          scitex-writer projects keep the canonical manuscript at
#          `<project>/.scitex/writer/` and expose a convenience symlink
#          `paper -> .scitex/writer`. When `paper` silently becomes a REAL
#          directory it diverges into two manuscript copies (this bit the
#          "neurovista" project). This check finds that drift and -- only when
#          explicitly asked -- repairs it WITHOUT ever destroying diverged
#          content.
#
#          `paper -> .scitex/writer` is a PRIVATE convention. It is NOT
#          enforced by default. Severity is a user-level knob with four levels:
#            off    -- check disabled, zero noise (DEFAULT for the public pkg)
#            warn   -- report drift as a warning (exit 0)
#            error  -- report drift as an error (exit 1)
#            repair -- actively fix safe cases; refuse to destroy diverged data
#
#          Severity precedence (highest -> lowest), mirroring the package's
#          documented config precedence:
#            1. --level {off,warn,error,repair} CLI flag
#            2. env SCITEX_WRITER_PAPER_SYMLINK
#            3. project ./config.yaml key paper_symlink.level
#            4. user-wide ~/.scitex/writer/config.yaml key paper_symlink.level
#            5. default off
#
#          SAFETY: on repair, if `paper/` is a real dir whose content is NOT
#          fully present (same path + same SHA-256) under `.scitex/writer/`,
#          conversion is REFUSED -- the directory is preserved, never deleted
#          or overwritten -- unless --force-after-backup is given, which still
#          moves `paper/` to a timestamped backup first. Diverged content is
#          NEVER silently overwritten or deleted.
#
# Usage:
#   python check_paper_symlink.py [project_dir]
#                                 [--level off|warn|error|repair]
#                                 [--force-after-backup]
#
# Self-contained: stdlib + optional PyYAML (only needed to read config files).

import argparse
import datetime
import hashlib
import os
import sys
from pathlib import Path

# ANSI colors (match check_overflow.py / check_limits.py)
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
DIM = "\033[0;90m"
BOLD = "\033[1m"
NC = "\033[0m"

PASS_COUNT = 0
WARN_COUNT = 0
FAIL_COUNT = 0

_LEVELS = ("off", "warn", "error", "repair")
_DEFAULT_LEVEL = "off"
_CANONICAL_REL = ".scitex/writer"

# How many diverged file paths to print before truncating.
_MAX_LIST = 20


def log_pass(msg):
    global PASS_COUNT
    print(f"  {GREEN}[PASS]{NC} {msg}")
    PASS_COUNT += 1


def log_warn(msg):
    global WARN_COUNT
    print(f"  {YELLOW}[WARN]{NC} {msg}")
    WARN_COUNT += 1


def log_fail(msg):
    global FAIL_COUNT
    print(f"  {RED}[FAIL]{NC} {msg}")
    FAIL_COUNT += 1


def log_detail(msg):
    print(f"    {DIM}{msg}{NC}")


def _read_config_level(config_path):
    """Read ``paper_symlink.level`` from a YAML config, or None.

    Returns the level string when present and valid, else None. A missing
    file or missing key is simply None (not an error). PyYAML is optional --
    if it is absent we silently skip config files (env + CLI still work).
    """
    if not config_path.exists():
        return None
    try:
        import yaml
    except ImportError:
        return None
    try:
        data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    block = data.get("paper_symlink")
    if not isinstance(block, dict):
        return None
    level = block.get("level")
    if isinstance(level, str) and level.lower() in _LEVELS:
        return level.lower()
    return None


def resolve_level(cli_level, project_dir):
    """Resolve the effective severity level via the documented precedence.

    1. CLI --level
    2. env SCITEX_WRITER_PAPER_SYMLINK
    3. project ./config.yaml -> paper_symlink.level
    4. user ~/.scitex/writer/config.yaml -> paper_symlink.level
    5. default off
    """
    if cli_level:
        return cli_level.lower()

    env = os.environ.get("SCITEX_WRITER_PAPER_SYMLINK", "").strip().lower()
    if env in _LEVELS:
        return env

    proj_level = _read_config_level(Path(project_dir) / "config.yaml")
    if proj_level:
        return proj_level

    user_level = _read_config_level(
        Path.home() / ".scitex" / "writer" / "config.yaml"
    )
    if user_level:
        return user_level

    return _DEFAULT_LEVEL


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def compute_divergence(link, canonical):
    """Return the list of files under ``link`` that are missing from or differ
    in content against ``canonical``.

    A file is "diverged" when no file with the same relative path AND the same
    SHA-256 exists under ``canonical``. ``.git`` directories are skipped. The
    returned paths are relative to ``link`` (sorted).
    """
    diverged = []
    for root, dirs, files in os.walk(link):
        if ".git" in dirs:
            dirs.remove(".git")
        for name in files:
            src = Path(root) / name
            rel = src.relative_to(link)
            dst = canonical / rel
            if not dst.is_file():
                diverged.append(str(rel))
                continue
            try:
                if _sha256(src) != _sha256(dst):
                    diverged.append(str(rel))
            except OSError:
                diverged.append(str(rel))
    return sorted(diverged)


def _make_relative_symlink(link):
    """Create the relative symlink ``paper -> .scitex/writer`` at ``link``."""
    os.symlink(_CANONICAL_REL, link, target_is_directory=True)


def _backup_dir(project_dir):
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return Path(project_dir) / ".scitex" / f"writer-paper-backup-{stamp}"


def _backup_and_link(link, project_dir):
    """Move ``link`` (a real dir) to a timestamped backup, then symlink.

    Returns the backup path. Uses ``shutil.move`` -- the directory is
    preserved, never deleted.
    """
    import shutil

    backup = _backup_dir(project_dir)
    backup.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(link), str(backup))
    _make_relative_symlink(link)
    return backup


def main():
    parser = argparse.ArgumentParser(
        description="Detect/repair drift in the top-level `paper` symlink that "
        "should point at `.scitex/writer`. Private convention -- disabled "
        "(off) by default; severity is a user-level knob."
    )
    parser.add_argument("project_dir", nargs="?", default=".")
    parser.add_argument(
        "--level",
        choices=list(_LEVELS),
        default=None,
        help="Severity: off (default), warn, error, or repair. Overrides env "
        "and config.",
    )
    parser.add_argument(
        "--force-after-backup",
        action="store_true",
        help="On repair, convert even diverged `paper/` -- but always back it "
        "up first (move to a timestamped dir). Never deletes content.",
    )
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    link = project_dir / "paper"
    canonical = project_dir / _CANONICAL_REL

    level = resolve_level(args.level, project_dir)

    print(f"\n{BOLD}=== Paper Symlink Check (level={level}) ==={NC}\n")

    if level == "off":
        print(
            f"  {DIM}[INFO]{NC} paper-symlink check is disabled (level=off). "
            f"Set paper_symlink.level or --level to enable."
        )
        print(
            f"\n{BOLD}Summary:{NC} {GREEN}0 passed{NC}, "
            f"{YELLOW}0 warnings{NC}, {RED}0 errors{NC}"
        )
        return 0

    # --- Case: link is a symlink -------------------------------------------
    if link.is_symlink():
        try:
            resolved = link.resolve()
        except OSError:
            resolved = None
        if resolved is not None and resolved == canonical.resolve():
            log_pass("`paper` is a symlink -> .scitex/writer (canonical)")
        else:
            # Wrong-target symlink. Repointing is data-safe.
            target = os.readlink(link)
            if level == "repair":
                link.unlink()
                _make_relative_symlink(link)
                log_pass(
                    f"repaired `paper` symlink: was -> {target}, now "
                    f"-> .scitex/writer"
                )
            else:
                report = log_fail if level == "error" else log_warn
                report(f"`paper` symlink points elsewhere (-> {target})")
                log_detail(
                    "hint: re-run with --level repair to repoint it to "
                    ".scitex/writer (data-safe)."
                )

    # --- Case: link is a real directory (the drift case) -------------------
    elif link.is_dir():
        if not canonical.exists():
            # Cannot safely convert: no canonical target exists. Never delete.
            report = log_fail if level in ("error", "repair") else log_warn
            report(
                "`paper/` is a REAL directory but .scitex/writer does not "
                "exist -- cannot safely convert."
            )
            log_detail(
                "hint: inspect `paper/` manually; it may be the only copy of "
                "your manuscript. Do NOT delete it."
            )
        else:
            diverged = compute_divergence(link, canonical)
            if not diverged:
                # Safe to convert: everything in paper/ already in canonical.
                if level == "repair" or args.force_after_backup:
                    backup = _backup_and_link(link, project_dir)
                    log_pass(
                        "converted real `paper/` dir to a symlink "
                        "-> .scitex/writer (no divergence)"
                    )
                    log_detail(f"backup of former paper/: {backup}")
                else:
                    report = log_fail if level == "error" else log_warn
                    report(
                        "`paper/` is a REAL directory (not a symlink), though "
                        "its content matches .scitex/writer."
                    )
                    log_detail(
                        "hint: re-run with --level repair to back it up and "
                        "replace it with a symlink."
                    )
            elif args.force_after_backup:
                # Explicitly forced: move diverged paper/ to a backup (NEVER
                # delete), then symlink. This is the sanctioned safe escape.
                shown = diverged[:_MAX_LIST]
                backup = _backup_and_link(link, project_dir)
                log_pass(
                    f"moved DIVERGED `paper/` ({len(diverged)} unique/differing "
                    f"file(s)) to a timestamped backup and created the symlink "
                    f"-> .scitex/writer (no data lost)"
                )
                log_detail(f"backup of diverged paper/: {backup}")
                for rel in shown:
                    log_detail(f"preserved: {rel}")
                if len(diverged) > len(shown):
                    log_detail(f"... and {len(diverged) - len(shown)} more")
            else:
                # Diverged, not forced -- always loud, always preserve. This is
                # dangerous, so it is an error regardless of warn/error/repair.
                log_fail(
                    f"`paper/` is a REAL directory and has DIVERGED from "
                    f".scitex/writer ({len(diverged)} file(s) missing or "
                    f"differing). Refusing to auto-convert."
                )
                shown = diverged[:_MAX_LIST]
                for rel in shown:
                    log_detail(f"diverged: paper/{rel}")
                if len(diverged) > len(shown):
                    log_detail(f"... and {len(diverged) - len(shown)} more")
                if level == "repair":
                    log_detail(
                        "hint: this content is NOT in .scitex/writer. Back it "
                        "up and inspect, or re-run with --force-after-backup "
                        "to move paper/ to a timestamped backup then symlink."
                    )
                else:
                    log_detail(
                        "hint: re-run with --level repair --force-after-backup "
                        "to back up paper/ then replace it with a symlink."
                    )

    # --- Case: link is some other non-symlink file -------------------------
    elif link.exists():
        report = log_fail if level in ("error", "repair") else log_warn
        report("`paper` exists but is neither a symlink nor a directory.")
        log_detail("hint: inspect it manually; not touching it.")

    # --- Case: link is missing ---------------------------------------------
    else:
        if level == "repair" and canonical.exists():
            _make_relative_symlink(link)
            log_pass("created `paper` symlink -> .scitex/writer")
        else:
            # Missing link is not drift -- nothing to enforce. Non-intrusive.
            log_pass("no `paper` symlink present; nothing to enforce")

    print()
    print(
        f"{BOLD}Summary:{NC} {GREEN}{PASS_COUNT} passed{NC}, "
        f"{YELLOW}{WARN_COUNT} warnings{NC}, {RED}{FAIL_COUNT} errors{NC}"
    )
    if FAIL_COUNT > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
