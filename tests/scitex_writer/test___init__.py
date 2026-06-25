"""Pins the paper-symlink default severity in scitex_writer.__init__.

Locks the off -> warn flip so a future edit cannot silently revert the
package-level resolver default.
"""

from __future__ import annotations

import os
import tempfile

import pytest

from scitex_writer import _resolve_paper_symlink_level


@pytest.fixture
def clean_paper_env():
    """Isolate env + HOME (real os.environ, restored on teardown) so neither
    SCITEX_WRITER_PAPER_SYMLINK nor a user config.yaml leaks into resolution."""
    saved = {k: os.environ.get(k) for k in ("SCITEX_WRITER_PAPER_SYMLINK", "HOME")}
    os.environ.pop("SCITEX_WRITER_PAPER_SYMLINK", None)
    with tempfile.TemporaryDirectory() as home:
        os.environ["HOME"] = home
        yield home
    for key, val in saved.items():
        if val is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = val


def test_resolve_paper_symlink_level_defaults_to_warn(tmp_path, clean_paper_env):
    """With no env and no user config, the resolved default level is warn."""
    # Arrange
    project_dir = str(tmp_path)
    # Act
    level = _resolve_paper_symlink_level(project_dir)
    # Assert
    assert level == "warn"
