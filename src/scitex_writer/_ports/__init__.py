"""Writer's optional bridges to sibling SciTeX packages.

Each module in this package detects the presence of an external package
at import time and exposes an ``*_AVAILABLE`` flag. When the sibling is
absent or schema differs, every bridge function returns ``None`` /
``[]`` so UI code degrades without raising.

Pattern lifted from ``scitex`` (`MCP_AVAILABLE`, `TORCH_AVAILABLE`).
"""
