#!/usr/bin/env python3
"""Establish the engine's own version truthfully, or refuse to state one.

A package's version lives in metadata *adjacent* to its code, not in the code.
When an environment holds more than one scitex-writer distribution,
``importlib.metadata.version()`` resolves one of them by scan order and returns
it with no indication that the question was ambiguous -- a confident answer to
an unanswerable question.

That matters here more than it would elsewhere: the compile stamps this version
into the manuscript's PDF provenance metadata. A guessed version becomes a
durable falsehood in a published scientific artifact -- one that survives in the
file long after the environment is repaired, and which no later reader can
detect from the PDF alone.

So when the version cannot be established, we refuse to stamp rather than stamp
a guess. The decision logic is pure: callers pass in the facts, so it can be
tested against real inputs instead of a patched interpreter.
"""

from __future__ import annotations

REMEDY = (
    "Remove the stale distribution so the version is unambiguous:\n"
    "    pip uninstall -y scitex-writer && pip install 'scitex-writer[all]'"
)


def describe_ambiguous_metadata(versions: list[str]) -> str:
    """Explain why no version can be stated, naming every candidate."""
    shown = ", ".join(sorted(versions))
    return (
        f"scitex-writer cannot determine its own version: {len(versions)} "
        f"installed distributions claim the name scitex-writer ({shown}). "
        f"importlib.metadata resolves one of them by directory scan order, so "
        f"any version reported now is a coin-flip.\n\n"
        f"Refusing to stamp a guessed engine version into the PDF's provenance "
        f"metadata: the manuscript would assert it was built by a version that "
        f"did not build it, and would keep asserting it after this environment "
        f"is fixed.\n\n" + REMEDY
    )


def resolve_stamp_version(installed: list[str], declared: str) -> str:
    """Return the version safe to stamp, or raise naming the ambiguity.

    ``installed`` are the versions of every installed distribution claiming the
    scitex-writer name; ``declared`` is what the package reports as its own
    version. This function's job is to *veto* ``declared`` when the metadata it
    came from was ambiguous -- not to re-derive it. An empty ``installed`` is
    not ambiguous: running from a source tree with nothing installed is a
    legitimate state, and ``declared`` falls back to pyproject.toml there.
    """
    distinct = sorted(set(installed))
    if len(distinct) > 1:
        raise RuntimeError(describe_ambiguous_metadata(distinct))
    return declared


def version_stamp_tex(version: str) -> str:
    """Render the LaTeX provenance stamp for a version known to be truthful."""
    return (
        f"\\def\\ScitexWriterVersion{{{version}}}\n"
        f"\\hypersetup{{pdfcreator={{Compiled by SciTeX Writer v{version}}}}}\n"
    )


def installed_versions(name: str = "scitex-writer") -> list[str]:
    """Every version claimed by an installed distribution with this name."""
    import importlib.metadata as md

    want = name.lower().replace("_", "-")
    return [
        d.version
        for d in md.distributions()
        if (d.metadata["Name"] or "").lower().replace("_", "-") == want
    ]
