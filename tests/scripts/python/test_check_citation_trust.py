#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: scripts/python/check_citation_trust.py
#
# NO mocks / NO monkeypatch (PA-306). The check exposes a real dependency-
# injection seam -- ``run_check(..., verifier=...)`` -- whose default is
# ``default_verifier`` (scitex-scholar). Tests pass real callables through that
# seam plus real tmp_path projects with real .tex/.bib files, so every path
# (verified / hallucinated / scholar-absent / cache) is exercised without a
# network and without patching internals.
#
# The end-to-end CLI runs use --offline, which is deterministic: scholar's
# offline resolver never resolves, so nothing can be reported trustworthy.

import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts" / "python"))

from _citation_trust_cache import cache_path  # noqa: E402
from check_citation_trust import (  # noqa: E402
    STATUS_SEVERITY,
    VerificationUnavailable,
    effective_severity,
    run_check,
)

_SCRIPT = ROOT_DIR / "scripts" / "python" / "check_citation_trust.py"

_TEX = r"""
\documentclass{article}
\begin{document}
Real \cite{Real2020}, bogus \cite{Bogus2099}, and bare \cite{NoIdent2021}.
\bibliography{bibliography}
\end{document}
"""

_BIB = """
@article{Real2020,
  title = {Attention is all you need},
  author = {Vaswani, Ashish},
  journal = {NeurIPS},
  year = {2017},
  doi = {10.48550/arXiv.1706.03762}
}
@article{Bogus2099,
  title = {Quantum telepathic gradient descent in fungal networks},
  author = {Nobody, A.},
  journal = {Journal of Things That Do Not Exist},
  year = {2099}
}
@book{NoIdent2021,
  title = {A book with no identifier at all},
  author = {Anon, B.},
  year = {2021}
}
"""


class _StubVerifier:
    """Real callable injected through the verifier seam (not a mock).

    Records how many times it was called and returns canned verdicts, so the
    caching behaviour is observable without a network.
    """

    def __init__(self, verdicts=None, raises=None):
        self.calls = 0
        self.verdicts = verdicts or []
        self.raises = raises

    def __call__(self, project_dir, bib=None, offline=False, min_confidence=0.8):
        self.calls += 1
        if self.raises is not None:
            raise self.raises
        return [dict(v) for v in self.verdicts]


def _project(tmp_path, bib_text=_BIB):
    contents = tmp_path / "01_manuscript" / "contents"
    contents.mkdir(parents=True)
    (contents / "main.tex").write_text(_TEX, encoding="utf-8")
    (contents / "bibliography.bib").write_text(bib_text, encoding="utf-8")
    return tmp_path


def _verdicts(real="verified", bogus="hallucinated", noident="unverified"):
    return [
        {"key": "Real2020", "status": real, "detail": "crossref", "confidence": 0.98},
        {"key": "Bogus2099", "status": bogus, "detail": "no index hit"},
        {"key": "NoIdent2021", "status": noident, "detail": "no identifier"},
    ]


# ----------------------------------------------------------- severity mapping


def test_status_severity_mapping_matches_agreed_contract():
    # Arrange
    # Act
    mapping = STATUS_SEVERITY
    # Assert
    assert mapping == {
        "verified": "info",
        "unverified": "warning",
        "stub": "warning",
        "unlinked": "warning",
        "hallucinated": "error",
    }


def test_hallucinated_is_error_at_error_level():
    # Arrange
    # Act
    severity = effective_severity("hallucinated", "error")
    # Assert
    assert severity == "error"


def test_hallucinated_clamps_to_warning_at_warn_level():
    # Arrange
    # Act
    severity = effective_severity("hallucinated", "warn")
    # Assert
    assert severity == "warning"


def test_unverified_stays_warning_at_error_level():
    # Arrange
    # Act
    severity = effective_severity("unverified", "error")
    # Assert
    assert severity == "warning"


def test_unknown_status_is_treated_as_error_never_pass():
    # Arrange
    # Act
    severity = effective_severity("some-future-status", "error")
    # Assert
    assert severity == "error"


# ------------------------------------------------------------- classification


def test_hallucinated_citation_fails_the_check_at_error_level(tmp_path):
    # Arrange
    project = _project(tmp_path)
    # Act
    code = run_check(
        project, level="error", offline=True, verifier=_StubVerifier(_verdicts())
    )
    # Assert
    assert code == 1


def test_hallucinated_citation_does_not_block_at_warn_level(tmp_path):
    # Arrange
    project = _project(tmp_path)
    # Act
    code = run_check(
        project, level="warn", offline=True, verifier=_StubVerifier(_verdicts())
    )
    # Assert
    assert code == 0


def test_all_verified_citations_pass_at_error_level(tmp_path):
    # Arrange
    project = _project(tmp_path)
    verifier = _StubVerifier(_verdicts(bogus="verified", noident="verified"))
    # Act
    code = run_check(project, level="error", verifier=verifier)
    # Assert
    assert code == 0


def test_hallucinated_key_is_named_in_the_report(tmp_path, capsys):
    # Arrange
    project = _project(tmp_path)
    run_check(project, level="error", offline=True, verifier=_StubVerifier(_verdicts()))
    # Act
    out = capsys.readouterr().out
    # Assert
    assert "Bogus2099" in out


def test_verified_citation_is_reported_as_a_pass(tmp_path, capsys):
    # Arrange
    project = _project(tmp_path)
    run_check(project, level="warn", offline=True, verifier=_StubVerifier(_verdicts()))
    # Act
    out = capsys.readouterr().out
    # Assert
    assert "[PASS]" in out


def test_level_off_disables_the_check(tmp_path, capsys):
    # Arrange
    project = _project(tmp_path)
    verifier = _StubVerifier(_verdicts())
    run_check(project, level="off", verifier=verifier)
    # Act
    calls = verifier.calls
    # Assert
    assert calls == 0


# ------------------------------------------------------------------ fail-loud


def test_absent_scholar_never_reports_citations_as_verified(tmp_path, capsys):
    # Arrange
    project = _project(tmp_path)
    unavailable = VerificationUnavailable("scitex_scholar.verify_cites is unavailable")
    run_check(project, level="warn", verifier=_StubVerifier(raises=unavailable))
    # Act
    out = capsys.readouterr().out
    # Assert
    assert "[PASS]" not in out


def test_absent_scholar_warns_loudly_at_warn_level(tmp_path, capsys):
    # Arrange
    project = _project(tmp_path)
    unavailable = VerificationUnavailable("scitex_scholar.verify_cites is unavailable")
    run_check(project, level="warn", verifier=_StubVerifier(raises=unavailable))
    # Act
    out = capsys.readouterr().out
    # Assert
    assert "could NOT be verified" in out


def test_absent_scholar_does_not_block_at_warn_level(tmp_path):
    # Arrange
    project = _project(tmp_path)
    unavailable = VerificationUnavailable("scitex_scholar.verify_cites is unavailable")
    # Act
    code = run_check(project, level="warn", verifier=_StubVerifier(raises=unavailable))
    # Assert
    assert code == 0


def test_absent_scholar_fails_the_build_at_error_level(tmp_path):
    # Arrange
    project = _project(tmp_path)
    unavailable = VerificationUnavailable("scitex_scholar.verify_cites is unavailable")
    # Act
    code = run_check(project, level="error", verifier=_StubVerifier(raises=unavailable))
    # Assert
    assert code == 1


def test_verifier_crash_is_reported_as_unrunnable_not_pass(tmp_path):
    # Arrange
    project = _project(tmp_path)
    boom = VerificationUnavailable("verify_cites() failed: ConnectionError: no network")
    # Act
    code = run_check(project, level="error", verifier=_StubVerifier(raises=boom))
    # Assert
    assert code == 1


def test_cite_key_without_a_verdict_is_reported_as_unverified(tmp_path, capsys):
    # Arrange
    project = _project(tmp_path)
    partial = _StubVerifier([_verdicts()[0]])  # only Real2020 comes back
    run_check(project, level="warn", offline=True, verifier=partial)
    # Act
    out = capsys.readouterr().out
    # Assert
    assert "NO verdict from scitex-scholar" in out


# --------------------------------------------------------------------- cache


def test_online_verdicts_are_written_to_the_cache(tmp_path):
    # Arrange
    project = _project(tmp_path)
    run_check(project, level="warn", verifier=_StubVerifier(_verdicts()))
    # Act
    exists = cache_path(project).is_file()
    # Assert
    assert exists is True


def test_offline_verdicts_are_never_cached(tmp_path):
    # Arrange
    project = _project(tmp_path)
    run_check(project, level="warn", offline=True, verifier=_StubVerifier(_verdicts()))
    # Act
    exists = cache_path(project).exists()
    # Assert
    assert exists is False


def test_second_run_serves_verdicts_from_the_cache(tmp_path):
    # Arrange
    project = _project(tmp_path)
    verifier = _StubVerifier(_verdicts())
    run_check(project, level="warn", verifier=verifier)
    # Act
    run_check(project, level="warn", verifier=verifier)
    # Assert
    assert verifier.calls == 1


def test_editing_a_bib_entry_reverifies_that_citation(tmp_path):
    # Arrange
    project = _project(tmp_path)
    verifier = _StubVerifier(_verdicts())
    run_check(project, level="warn", verifier=verifier)
    edited = _BIB.replace("Attention is all you need", "Attention is not all you need")
    (project / "01_manuscript" / "contents" / "bibliography.bib").write_text(
        edited, encoding="utf-8"
    )
    # Act
    run_check(project, level="warn", verifier=verifier)
    # Assert
    assert verifier.calls == 2


def test_no_cache_flag_forces_reverification(tmp_path):
    # Arrange
    project = _project(tmp_path)
    verifier = _StubVerifier(_verdicts())
    run_check(project, level="warn", verifier=verifier)
    # Act
    run_check(project, level="warn", use_cache=False, verifier=verifier)
    # Assert
    assert verifier.calls == 2


def test_cached_hallucination_still_fails_at_error_level(tmp_path):
    # Arrange
    project = _project(tmp_path)
    verifier = _StubVerifier(_verdicts())
    run_check(project, level="warn", verifier=verifier)
    # Act
    code = run_check(project, level="error", verifier=verifier)
    # Assert
    assert code == 1


# ----------------------------------------------------------------- end-to-end


def _run_cli(project, *extra):
    env = {
        "PATH": "/usr/bin:/bin",
        "HOME": str(Path(project) / "_home"),
    }
    return subprocess.run(
        [sys.executable, str(_SCRIPT), str(project), *extra],
        capture_output=True,
        text=True,
        env=env,
    )


def test_cli_offline_run_exits_zero_at_default_warn_level(tmp_path):
    # Arrange
    project = _project(tmp_path)
    # Act
    proc = _run_cli(project, "--offline")
    # Assert
    assert proc.returncode == 0


def test_cli_offline_run_exits_one_at_error_level(tmp_path):
    # Arrange
    project = _project(tmp_path)
    # Act
    proc = _run_cli(project, "--offline", "--level", "error")
    # Assert
    assert proc.returncode == 1


def test_cli_offline_run_never_reports_a_pass(tmp_path):
    # Arrange
    project = _project(tmp_path)
    # Act
    proc = _run_cli(project, "--offline", "--level", "warn")
    # Assert
    assert "[PASS]" not in proc.stdout


def test_cli_level_off_exits_zero_and_says_disabled(tmp_path):
    # Arrange
    project = _project(tmp_path)
    # Act
    proc = _run_cli(project, "--level", "off")
    # Assert
    assert "disabled (level=off)" in proc.stdout


# EOF
