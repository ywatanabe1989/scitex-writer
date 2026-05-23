"""Auto-generated smoke test for scitex_writer._dataclasses.results._CompilationResult.

Replaces the prior placeholder-only stub (audit-project PS206). The
test imports the target module — if the import fails, the test
fails. Renames, broken peer deps, or missing optional deps all
surface here as red, not as a silent skip.

If a module legitimately requires an optional dep, that dep should
be lazy-imported inside the function bodies — not at module top.
"""

import importlib


def test_module_exposes_compilation_result():
    # Arrange
    # Act
    module = importlib.import_module("scitex_writer._dataclasses.results._CompilationResult")
    # Assert
    assert hasattr(module, "CompilationResult")
