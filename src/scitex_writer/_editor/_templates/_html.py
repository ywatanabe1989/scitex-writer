#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_editor/_templates/_html.py

"""HTML body structure for the Writer GUI."""


def build_html_body(project_dir: str = "") -> str:
    """Build the HTML body content.

    Parameters
    ----------
    project_dir : str
        Project directory path for display.

    Returns
    -------
    str
        HTML body content string.
    """
    return f"""
<!-- Toolbar -->
<header class="toolbar">
    <div class="toolbar-left">
        <span class="logo">SciTeX Writer</span>
        <select id="doc-type-select" title="Document type">
            <option value="manuscript">Manuscript</option>
            <option value="supplementary">Supplementary</option>
            <option value="revision">Revision</option>
        </select>
    </div>
    <div class="toolbar-center">
        <span id="current-file" class="current-file">No file open</span>
        <span id="save-status" class="save-status"></span>
    </div>
    <div class="toolbar-right">
        <button id="btn-compile" class="btn btn-primary"
                title="Compile (Ctrl+Shift+B)">Compile</button>
        <button id="btn-toggle-log" class="btn btn-secondary"
                title="Toggle compilation log">Log</button>
        <button id="btn-toggle-theme" class="btn btn-icon" title="Toggle dark/light mode">
            <span id="theme-icon">&#9789;</span>
        </button>
    </div>
</header>

<!-- Main workspace -->
<div class="workspace">
    <!-- Sidebar: File tree -->
    <aside class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <span class="sidebar-title">Files</span>
            <button id="btn-collapse-sidebar" class="btn btn-icon btn-sm"
                    title="Collapse sidebar">&#9664;</button>
        </div>
        <div class="file-tree" id="file-tree">
            <div class="loading">Loading...</div>
        </div>
    </aside>

    <!-- Sidebar resizer -->
    <div class="resizer" id="sidebar-resizer"
         data-target="sidebar" data-direction="left"></div>

    <!-- Editor panel -->
    <div class="editor-panel" id="editor-panel">
        <div class="file-tabs" id="file-tabs"></div>
        <div class="editor-container" id="editor-container">
            <div class="welcome-message" id="welcome-message">
                <h2>SciTeX Writer</h2>
                <p>Select a file from the sidebar to begin editing.</p>
                <p class="hint">Project: {project_dir}</p>
            </div>
        </div>
    </div>

    <!-- Editor-preview resizer -->
    <div class="resizer" id="preview-resizer"
         data-target="preview-panel" data-direction="right"></div>

    <!-- Preview panel -->
    <div class="preview-panel" id="preview-panel">
        <div class="preview-header">
            <div class="preview-tabs">
                <button class="preview-tab active" data-view="pdf">PDF</button>
                <button class="preview-tab" data-view="bib">Bibliography</button>
            </div>
            <div class="preview-actions">
                <button id="btn-refresh-pdf" class="btn btn-icon btn-sm"
                        title="Refresh PDF">&#8635;</button>
            </div>
        </div>
        <div class="preview-content" id="preview-content">
            <!-- PDF view -->
            <div class="preview-view active" id="pdf-view">
                <div class="pdf-container" id="pdf-container">
                    <div class="pdf-placeholder" id="pdf-placeholder">
                        <p>No PDF available.</p>
                        <p class="hint">Click Compile to generate.</p>
                    </div>
                    <canvas id="pdf-canvas" style="display:none;"></canvas>
                    <div class="pdf-controls" id="pdf-controls" style="display:none;">
                        <button id="btn-pdf-prev" class="btn btn-sm">&larr; Prev</button>
                        <span id="pdf-page-info">1 / 1</span>
                        <button id="btn-pdf-next" class="btn btn-sm">Next &rarr;</button>
                        <button id="btn-pdf-zoom-out" class="btn btn-sm">-</button>
                        <span id="pdf-zoom-level">100%</span>
                        <button id="btn-pdf-zoom-in" class="btn btn-sm">+</button>
                        <button id="btn-pdf-fit" class="btn btn-sm">Fit</button>
                    </div>
                </div>
            </div>
            <!-- Bibliography view -->
            <div class="preview-view" id="bib-view">
                <div class="bib-list" id="bib-list">
                    <div class="loading">Loading bibliography...</div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Compilation log panel -->
<div class="log-panel" id="log-panel" style="display:none;">
    <div class="log-header">
        <span>Compilation Log</span>
        <button id="btn-close-log" class="btn btn-icon btn-sm">&times;</button>
    </div>
    <pre class="log-content" id="log-content"></pre>
</div>
"""


# EOF
