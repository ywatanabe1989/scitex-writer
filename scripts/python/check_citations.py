#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: scripts/python/check_citations.py
# Purpose: Pre-compile CITATION GATE -- before a research manuscript is
#          compiled, check every \cite key actually used in the document against
#          its bibliography entry and FAIL the build if a cited entry is a
#          scholar STUB (auto-generated placeholder that has not yet been
#          resolved to a real, verified source). A stub reference must never
#          reach a compiled manuscript ("一発アウト"): it is either a
#          hallucinated citation or an unfinished lookup.
#
#          This is the COMPILER-OWNS half of the citation->clew verification
#          contract (neurovista, operator-directed 2026-07-01). It is fully
#          LOCAL -- no clew/scholar dependency -- so it delivers the root-fix
#          immediately and would have failed the neurovista build on the
#          PintoOrellana2023 stub at source. The CLEW-OWNS half (querying clew
#          for per-key scholar verification status) slots in later behind the
#          same report once clew defines its batch lookup; until then this gate
#          catches the stub stamps scholar already writes.
#
#          A STUB is detected by the markers scholar stamps into the entry:
#            * note    contains "Auto-generated stub"   (STUB_NOTE_MARKERS)
#            * journal contains "Pending scitex-scholar metadata lookup"
#                                                        (STUB_JOURNAL_MARKERS)
#          A cited entry matching ANY marker is a stub and gates. "No DOI" is
#          deliberately NOT a sole stub trigger -- many legitimate references
#          (books, arXiv preprints, conference papers) have no DOI, so failing
#          on that alone would be a false positive. Missing-DOI cited entries
#          are surfaced as an informational note only. The marker lists are
#          module constants so scholar's authoritative stamp fields can be
#          extended without touching the logic.
#
#          DEFAULT depends on project type: a *research* project (marked by
#          .scitex/dev/config.yaml `project-type: research`) defaults to
#          `error` (gate ON -> FAIL); any other project defaults to `warn`
#          (loud, non-blocking). CLI/env/config always override the default.
#
# Usage:
#   python check_citations.py [project_dir]
#                             [--tex PATH ...] [--bib PATH]
#                             [--level off|warn|error]
#
# Self-contained: stdlib + optional PyYAML (only to read config files).

import argparse
import glob
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _severity import resolve_level  # noqa: E402

GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
DIM = "\033[0;90m"
BOLD = "\033[1m"
NC = "\033[0m"

PASS_COUNT = 0
WARN_COUNT = 0
FAIL_COUNT = 0

_LEVELS = ("off", "warn", "error")

# Scholar stub stamps (lowercase substring match). Authoritative source is
# scitex-scholar; extend here when scholar adds/renames a stamp field.
STUB_NOTE_MARKERS = ("auto-generated stub",)
STUB_JOURNAL_MARKERS = ("pending scitex-scholar metadata lookup",)

# Citation commands whose {..} argument holds comma-separated cite keys.
_CITE_CMD = (
    r"\\(?:cite|citep|citet|citeauthor|citeyear|citeyearpar|citealt|citealp|"
    r"citenum|Cite|Citep|Citet|Citeauthor|parencite|Parencite|textcite|"
    r"Textcite|autocite|Autocite|footcite|fullcite|smartcite)"
)
# Optional [..] pre/post-notes, then the mandatory {key,key,...}.
_CITE_RE = re.compile(_CITE_CMD + r"\s*(?:\[[^\]]*\]\s*){0,2}\{([^}]*)\}")

_DEFAULT_BIB = "00_shared/bib_files/bibliography.bib"


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


def _strip_tex_comments(tex):
    r"""Drop LaTeX line comments so a commented-out \cite is not counted.

    A percent is a comment start unless escaped (\%). Keep everything before an
    unescaped %.
    """
    out = []
    for line in tex.splitlines():
        idx = 0
        cut = None
        while idx < len(line):
            ch = line[idx]
            if ch == "\\":
                idx += 2  # skip escaped char (covers \%)
                continue
            if ch == "%":
                cut = idx
                break
            idx += 1
        out.append(line if cut is None else line[:cut])
    return "\n".join(out)


def extract_cited_keys(tex):
    r"""Return the set of cite keys referenced by \cite-family commands in tex.

    Commented-out citations are ignored. Whitespace and empty keys are dropped.
    """
    keys = set()
    for group in _CITE_RE.findall(_strip_tex_comments(tex)):
        for raw in group.split(","):
            key = raw.strip()
            if key:
                keys.add(key)
    return keys


def iter_bib_entries(bib_text):
    """Yield (cite_key, fields_dict) for each @type{key, ...} entry.

    A dependency-free scanner: finds each ``@type{key,`` header, then captures
    the entry body by brace balancing. Field values are read for both
    ``field = {value}`` and ``field = "value"`` forms. Keys and field names are
    matched case-insensitively (BibTeX is case-insensitive on both).
    """
    header = re.compile(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", re.IGNORECASE)
    for m in header.finditer(bib_text):
        entry_type = m.group(1).lower()
        if entry_type in ("comment", "string", "preamble"):
            continue
        cite_key = m.group(2).strip()
        # Capture the body by brace balancing from the opening '{'.
        open_brace = bib_text.index("{", m.start())
        depth = 0
        i = open_brace
        while i < len(bib_text):
            c = bib_text[i]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        body = bib_text[open_brace + 1 : i]
        yield cite_key, _parse_fields(body)


def _parse_fields(body):
    """Parse ``name = {value}`` / ``name = "value"`` pairs from an entry body."""
    fields = {}
    field_re = re.compile(
        r"(\w+)\s*=\s*(?:\{(.*?)\}|\"(.*?)\")", re.IGNORECASE | re.DOTALL
    )
    for fm in field_re.finditer(body):
        name = fm.group(1).lower()
        value = fm.group(2) if fm.group(2) is not None else (fm.group(3) or "")
        fields[name] = value.strip()
    return fields


def stub_reason(fields):
    """Return a human reason string if the entry is a scholar stub, else None."""
    note = fields.get("note", "").lower()
    for marker in STUB_NOTE_MARKERS:
        if marker in note:
            return f'note="{fields.get("note", "")}"'
    journal = fields.get("journal", "").lower()
    for marker in STUB_JOURNAL_MARKERS:
        if marker in journal:
            return f'journal="{fields.get("journal", "")}"'
    return None


def _load_text(paths):
    """Concatenate the text of every existing path in ``paths``."""
    chunks = []
    for p in paths:
        try:
            chunks.append(Path(p).read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
    return "\n".join(chunks)


def _resolve_tex_paths(project_dir, tex_args):
    """Resolve the tex sources to scan for citations.

    Precedence: explicit --tex args (globs allowed) > SCITEX_WRITER_COMPILED_TEX
    env > every *.tex under the project (last resort). Returns a sorted list.
    """
    if tex_args:
        found = []
        for pat in tex_args:
            found.extend(sorted(glob.glob(pat)))
        return found
    env_tex = os.environ.get("SCITEX_WRITER_COMPILED_TEX", "").strip()
    if env_tex and Path(env_tex).is_file():
        return [env_tex]
    return sorted(str(p) for p in Path(project_dir).rglob("*.tex"))


def _is_research_project(project_dir):
    """True iff .scitex/dev/config.yaml marks this a ``project-type: research``.

    Mirrors check_clew_verify._is_research_project so both gates share one
    research-mode signal. PyYAML optional; falls back to a textual marker scan.
    """
    cfg = Path(project_dir) / ".scitex" / "dev" / "config.yaml"
    if not cfg.is_file():
        return False
    try:
        text = cfg.read_text(encoding="utf-8")
    except OSError:
        return False
    try:
        import yaml

        data = yaml.safe_load(text) or {}
        if isinstance(data, dict):
            return str(data.get("project-type", "")).strip().lower() == "research"
    except Exception:
        pass
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("project-type:"):
            return stripped.split(":", 1)[1].strip().strip("\"'").lower() == "research"
    return False


def audit_citations(cited_keys, entries):
    """Classify each cited key against the bibliography.

    Returns (stubs, missing, no_doi):
      stubs   -> list of (key, reason) whose entry is a scholar stub
      missing -> sorted list of cited keys with no bibliography entry
      no_doi  -> sorted list of cited keys whose entry has no DOI (info only)
    """
    stubs = []
    missing = []
    no_doi = []
    for key in sorted(cited_keys):
        fields = entries.get(key)
        if fields is None:
            missing.append(key)
            continue
        reason = stub_reason(fields)
        if reason is not None:
            stubs.append((key, reason))
        elif not fields.get("doi", "").strip():
            no_doi.append(key)
    return stubs, missing, no_doi


def main():
    parser = argparse.ArgumentParser(
        description="Pre-compile citation gate: FAIL when a cited reference is a "
        "scholar stub (unresolved/placeholder). Defaults ON (error) for research "
        "projects, warn otherwise."
    )
    parser.add_argument("project_dir", nargs="?", default=".")
    parser.add_argument(
        "--tex",
        action="append",
        default=None,
        help="Tex file(s)/glob(s) to scan for \\cite keys (repeatable). "
        "Defaults to $SCITEX_WRITER_COMPILED_TEX, else all *.tex under project.",
    )
    parser.add_argument(
        "--bib",
        default=None,
        help=f"Bibliography .bib to read entries from (default: {_DEFAULT_BIB}).",
    )
    parser.add_argument(
        "--level",
        choices=list(_LEVELS),
        default=None,
        help="Severity: off, warn, or error. Overrides env and config.",
    )
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    research = _is_research_project(project_dir)
    default = "error" if research else "warn"
    level = resolve_level(
        "citations",
        args.level,
        project_dir,
        default=default,
        env_var="SCITEX_WRITER_CITATIONS",
    )
    kind = "research" if research else "non-research"
    print(f"\n{BOLD}=== Citation Gate (level={level}, {kind}) ==={NC}\n")

    if level == "off":
        print(
            f"  {DIM}[INFO]{NC} citation gate is disabled (level=off). "
            f"Set citations.level or --level to enable."
        )
        _summary()
        return 0

    report = log_fail if level == "error" else log_warn

    bib_path = Path(args.bib) if args.bib else project_dir / _DEFAULT_BIB
    if not bib_path.is_file():
        log_warn(f"bibliography not found: {bib_path} -- nothing to check.")
        _summary()
        return 1 if FAIL_COUNT > 0 else 0

    tex_paths = _resolve_tex_paths(project_dir, args.tex)
    cited_keys = extract_cited_keys(_load_text(tex_paths))
    if not cited_keys:
        log_warn("no \\cite keys found in the scanned tex -- nothing to check.")
        log_detail(f"scanned: {len(tex_paths)} tex file(s)")
        _summary()
        return 1 if FAIL_COUNT > 0 else 0

    entries = dict(iter_bib_entries(bib_path.read_text(encoding="utf-8", errors="replace")))
    stubs, missing, no_doi = audit_citations(cited_keys, entries)

    if stubs:
        report(
            f"{len(stubs)} cited reference(s) are unresolved scholar stubs -- "
            f"replace with a real, verified source before compiling:"
        )
        for key, reason in stubs:
            log_detail(f"\\cite{{{key}}} -> STUB ({reason})")
        log_detail(
            "fix: resolve each key via scitex-scholar (DOI + real metadata), or "
            "remove the citation. Override with citations.level if intended."
        )
    else:
        log_pass(f"all {len(cited_keys)} cited reference(s) are non-stub entries")

    # Missing entries and missing-DOI are informational (bibtex already flags
    # undefined citations; DOI-less entries are often legitimate). Never a FAIL.
    if missing:
        log_warn(f"{len(missing)} cited key(s) have no bibliography entry:")
        for key in missing:
            log_detail(f"\\cite{{{key}}} -> no entry in {bib_path.name}")
    if no_doi:
        log_detail(
            f"note: {len(no_doi)} cited entry(ies) have no DOI (not a failure): "
            + ", ".join(no_doi[:10])
            + (" ..." if len(no_doi) > 10 else "")
        )

    _summary()
    return 1 if FAIL_COUNT > 0 else 0


def _summary():
    print()
    print(
        f"{BOLD}Summary:{NC} {GREEN}{PASS_COUNT} passed{NC}, "
        f"{YELLOW}{WARN_COUNT} warnings{NC}, {RED}{FAIL_COUNT} errors{NC}"
    )


if __name__ == "__main__":
    sys.exit(main())
