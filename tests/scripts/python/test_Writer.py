#!/usr/bin/env python3
"""Tests for scitex_writer.writer.Writer."""

import pytest

from scitex_writer.writer import Writer


@pytest.fixture
def valid_project_structure(tmp_path):
    """Create a valid writer project structure.

    git_strategy=None is used at the call sites so Writer attaches to
    this real on-disk directory without initializing git — no network,
    no template clone, fully offline.
    """
    (tmp_path / "00_shared").mkdir()
    (tmp_path / "01_manuscript").mkdir()
    (tmp_path / "02_supplementary").mkdir()
    (tmp_path / "03_revision").mkdir()
    (tmp_path / "scripts").mkdir()
    return tmp_path


class _RecordingRunner:
    """Real callable recording its args; returns a canned result.

    Injected via the runner= seam on Writer.compile_* / Writer.watch so
    the delegation contract is exercised without running pdflatex or
    spawning a watch subprocess.
    """

    def __init__(self, result=None):
        self.calls = []
        self.result = result

    def __call__(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        return self.result


class TestWriterInitialization:
    """Tests for Writer initialization with existing project."""

    def test_project_dir_matches_supplied_directory(self, valid_project_structure):
        # Arrange
        # Act
        writer = Writer(valid_project_structure, git_strategy=None)
        # Assert
        assert writer.project_dir == valid_project_structure

    def test_sets_project_name_from_directory(self, valid_project_structure):
        # Arrange
        # Act
        writer = Writer(valid_project_structure, git_strategy=None)
        # Assert
        assert writer.project_name == valid_project_structure.name

    def test_uses_custom_project_name(self, valid_project_structure):
        # Arrange
        # Act
        writer = Writer(valid_project_structure, name="custom_name", git_strategy=None)
        # Assert
        assert writer.project_name == "custom_name"

    def test_initializes_manuscript_tree(self, valid_project_structure):
        # Arrange
        # Act
        writer = Writer(valid_project_structure, git_strategy=None)
        # Assert
        assert writer.manuscript is not None

    def test_initializes_supplementary_tree(self, valid_project_structure):
        # Arrange
        # Act
        writer = Writer(valid_project_structure, git_strategy=None)
        # Assert
        assert writer.supplementary is not None

    def test_initializes_revision_tree(self, valid_project_structure):
        # Arrange
        # Act
        writer = Writer(valid_project_structure, git_strategy=None)
        # Assert
        assert writer.revision is not None

    def test_initializes_scripts_tree(self, valid_project_structure):
        # Arrange
        # Act
        writer = Writer(valid_project_structure, git_strategy=None)
        # Assert
        assert writer.scripts is not None

    def test_initializes_shared_tree(self, valid_project_structure):
        # Arrange
        # Act
        writer = Writer(valid_project_structure, git_strategy=None)
        # Assert
        assert writer.shared is not None


class TestWriterProjectVerification:
    """Tests for Writer project structure verification."""

    def test_raises_when_manuscript_missing(self, tmp_path):
        # Arrange
        (tmp_path / "00_shared").mkdir()
        (tmp_path / "02_supplementary").mkdir()
        (tmp_path / "03_revision").mkdir()
        (tmp_path / "scripts").mkdir()
        # Act
        # Assert
        with pytest.raises(RuntimeError, match="01_manuscript"):
            Writer(tmp_path, git_strategy=None)

    def test_raises_when_supplementary_missing(self, tmp_path):
        # Arrange
        (tmp_path / "00_shared").mkdir()
        (tmp_path / "01_manuscript").mkdir()
        (tmp_path / "03_revision").mkdir()
        (tmp_path / "scripts").mkdir()
        # Act
        # Assert
        with pytest.raises(RuntimeError, match="02_supplementary"):
            Writer(tmp_path, git_strategy=None)

    def test_raises_when_revision_missing(self, tmp_path):
        # Arrange
        (tmp_path / "00_shared").mkdir()
        (tmp_path / "01_manuscript").mkdir()
        (tmp_path / "02_supplementary").mkdir()
        (tmp_path / "scripts").mkdir()
        # Act
        # Assert
        with pytest.raises(RuntimeError, match="03_revision"):
            Writer(tmp_path, git_strategy=None)


class TestWriterGetPdf:
    """Tests for Writer.get_pdf method."""

    def test_returns_none_when_pdf_missing(self, valid_project_structure):
        # Arrange
        writer = Writer(valid_project_structure, git_strategy=None)
        # Act
        result = writer.get_pdf("manuscript")
        # Assert
        assert result is None

    def test_returns_path_when_manuscript_pdf_exists(self, valid_project_structure):
        # Arrange
        pdf_path = valid_project_structure / "01_manuscript" / "manuscript.pdf"
        pdf_path.write_bytes(b"%PDF-1.4")
        writer = Writer(valid_project_structure, git_strategy=None)
        # Act
        result = writer.get_pdf("manuscript")
        # Assert
        assert result == pdf_path

    def test_returns_path_when_supplementary_pdf_exists(self, valid_project_structure):
        # Arrange
        pdf_path = valid_project_structure / "02_supplementary" / "supplementary.pdf"
        pdf_path.write_bytes(b"%PDF-1.4")
        writer = Writer(valid_project_structure, git_strategy=None)
        # Act
        result = writer.get_pdf("supplementary")
        # Assert
        assert result == pdf_path


class TestWriterDelete:
    """Tests for Writer.delete method."""

    def test_delete_returns_true_on_success(self, valid_project_structure):
        # Arrange
        writer = Writer(valid_project_structure, git_strategy=None)
        # Act
        result = writer.delete()
        # Assert
        assert result is True

    def test_delete_removes_project_directory(self, valid_project_structure):
        # Arrange
        writer = Writer(valid_project_structure, git_strategy=None)
        # Act
        writer.delete()
        # Assert
        assert not valid_project_structure.exists()

    def test_delete_returns_false_when_directory_already_gone(
        self, valid_project_structure
    ):
        # Arrange
        writer = Writer(valid_project_structure, git_strategy=None)
        writer.delete()  # first delete succeeds and removes the directory
        # Act
        result = writer.delete()  # second delete hits a real FileNotFoundError
        # Assert
        assert result is False


class TestWriterCompileMethods:
    """Tests for Writer compilation methods (delegation contract)."""

    def test_compile_manuscript_returns_runner_result(self, valid_project_structure):
        # Arrange
        writer = Writer(valid_project_structure, git_strategy=None)
        sentinel = object()
        runner = _RecordingRunner(result=sentinel)
        # Act
        result = writer.compile_manuscript(runner=runner)
        # Assert
        assert result is sentinel

    def test_compile_manuscript_passes_project_dir_to_runner(
        self, valid_project_structure
    ):
        # Arrange
        writer = Writer(valid_project_structure, git_strategy=None)
        runner = _RecordingRunner()
        # Act
        writer.compile_manuscript(timeout=300, runner=runner)
        # Assert
        assert runner.calls[0][0] == (valid_project_structure,)

    def test_compile_supplementary_returns_runner_result(self, valid_project_structure):
        # Arrange
        writer = Writer(valid_project_structure, git_strategy=None)
        sentinel = object()
        runner = _RecordingRunner(result=sentinel)
        # Act
        result = writer.compile_supplementary(runner=runner)
        # Assert
        assert result is sentinel

    def test_compile_revision_forwards_track_changes_flag(
        self, valid_project_structure
    ):
        # Arrange
        writer = Writer(valid_project_structure, git_strategy=None)
        runner = _RecordingRunner()
        # Act
        writer.compile_revision(track_changes=True, runner=runner)
        # Assert
        assert runner.calls[0][1]["track_changes"] is True


class TestWriterWatch:
    """Tests for Writer.watch method."""

    def test_watch_passes_project_dir_to_runner(self, valid_project_structure):
        # Arrange
        writer = Writer(valid_project_structure, git_strategy=None)
        runner = _RecordingRunner()
        # Act
        writer.watch(runner=runner)
        # Assert
        assert runner.calls[0][0] == (valid_project_structure,)

    def test_watch_forwards_on_compile_callback(self, valid_project_structure):
        # Arrange
        writer = Writer(valid_project_structure, git_strategy=None)
        runner = _RecordingRunner()

        def _callback():
            return None

        # Act
        writer.watch(on_compile=_callback, runner=runner)
        # Assert
        assert runner.calls[0][1]["on_compile"] is _callback


class TestWriterGitStrategy:
    """Tests for Writer git_strategy parameter."""

    def test_default_git_strategy_is_child(self, valid_project_structure):
        # Arrange
        # Act
        writer = Writer(valid_project_structure)
        # Assert
        assert writer.git_strategy == "child"

    def test_custom_git_strategy(self, valid_project_structure):
        # Arrange
        # Act
        writer = Writer(valid_project_structure, git_strategy="parent")
        # Assert
        assert writer.git_strategy == "parent"

    def test_git_strategy_none(self, valid_project_structure):
        # Arrange
        # Act
        writer = Writer(valid_project_structure, git_strategy=None)
        # Assert
        assert writer.git_strategy is None


class TestWriterBranchTag:
    """Tests for Writer branch and tag parameters."""

    def test_branch_parameter_smoke_case(self, valid_project_structure):
        # Arrange
        # Act
        writer = Writer(valid_project_structure, branch="develop", git_strategy=None)
        # Assert
        assert writer.branch == "develop"

    def test_tag_parameter_smoke_case(self, valid_project_structure):
        # Arrange
        # Act
        writer = Writer(valid_project_structure, tag="v1.0.0", git_strategy=None)
        # Assert
        assert writer.tag == "v1.0.0"


if __name__ == "__main__":
    import os

    pytest.main([os.path.abspath(__file__)])
