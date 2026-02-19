#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_editor/_templates/_styles.py

"""CSS styles for the Writer GUI."""

from ._styles_claims import CLAIMS_STYLES as _CLAIMS


def build_styles() -> str:
    """Build inline CSS styles.

    Returns
    -------
    str
        Complete <style> block.
    """
    return (
        "<style>\n"
        + _RESET
        + _THEME_VARS
        + _LAYOUT
        + _COMPONENTS
        + _CLAIMS
        + "</style>"
    )


_RESET = """
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body {
    height: 100%; overflow: hidden;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    font-size: 14px;
}
body { background: var(--bg-primary); color: var(--text-primary);
       display: flex; flex-direction: column; }
"""

_THEME_VARS = """
[data-theme="light"] {
    --bg-primary: #fdfcfa; --bg-secondary: #f5f3f0;
    --bg-tertiary: #eae7e2; --bg-editor: #ffffff;
    --text-primary: #1a1a1a; --text-secondary: #555555; --text-muted: #888888;
    --border-color: #d4d0cb; --border-light: #e8e5e0;
    --accent: #2563eb; --accent-hover: #1d4ed8; --accent-bg: #eff6ff;
    --danger: #dc2626; --success: #16a34a; --warning: #d97706;
    --toolbar-bg: #f5f3f0; --sidebar-bg: #f5f3f0;
    --hover-bg: #eae7e2; --active-bg: #ddd9d3;
    --tab-bg: #eae7e2; --tab-active-bg: #ffffff;
    --scrollbar-thumb: #c4c0bb;
    --log-bg: #1e1e1e; --log-text: #d4d4d4;
    --cm-bg: #ffffff; --cm-text: #1a1a1a;
    --cm-gutter-bg: #f5f3f0; --cm-gutter-text: #999999;
    --cm-cursor: #1a1a1a; --cm-selection: #add6ff;
    --cm-keyword: #0000ff; --cm-atom: #219; --cm-number: #164;
    --cm-def: #00f; --cm-variable: #1a1a1a; --cm-string: #a11;
    --cm-comment: #999999; --cm-bracket: #997;
    --cm-tag: #170; --cm-attribute: #00c;
}
[data-theme="dark"] {
    --bg-primary: #1e1e1e; --bg-secondary: #252526;
    --bg-tertiary: #2d2d2d; --bg-editor: #1e1e1e;
    --text-primary: #d4d4d4; --text-secondary: #aaaaaa; --text-muted: #666666;
    --border-color: #3e3e3e; --border-light: #333333;
    --accent: #4a9eff; --accent-hover: #2d8cf0; --accent-bg: #1a3a5c;
    --danger: #f87171; --success: #4ade80; --warning: #fbbf24;
    --toolbar-bg: #252526; --sidebar-bg: #252526;
    --hover-bg: #2d2d2d; --active-bg: #37373d;
    --tab-bg: #2d2d2d; --tab-active-bg: #1e1e1e;
    --scrollbar-thumb: #555555;
    --log-bg: #1a1a1a; --log-text: #d4d4d4;
    --cm-bg: #1e1e1e; --cm-text: #d4d4d4;
    --cm-gutter-bg: #252526; --cm-gutter-text: #858585;
    --cm-cursor: #d4d4d4; --cm-selection: #264f78;
    --cm-keyword: #569cd6; --cm-atom: #b5cea8; --cm-number: #b5cea8;
    --cm-def: #dcdcaa; --cm-variable: #9cdcfe; --cm-string: #ce9178;
    --cm-comment: #6a9955; --cm-bracket: #ffd700;
    --cm-tag: #4ec9b0; --cm-attribute: #9cdcfe;
}
"""

_LAYOUT = """
/* Toolbar */
.toolbar {
    display: flex; align-items: center; justify-content: space-between;
    height: 40px; padding: 0 12px;
    background: var(--toolbar-bg); border-bottom: 1px solid var(--border-color);
    flex-shrink: 0; gap: 12px;
}
.toolbar-left, .toolbar-center, .toolbar-right {
    display: flex; align-items: center; gap: 8px;
}
.toolbar-center { flex: 1; justify-content: center; }
.logo { font-weight: 700; font-size: 15px; color: var(--accent); white-space: nowrap; }
.current-file {
    font-size: 13px; color: var(--text-secondary);
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 300px;
}
.save-status { font-size: 12px; color: var(--text-muted); }
.save-status.saved { color: var(--success); }
.save-status.saving { color: var(--warning); }
.save-status.error { color: var(--danger); }

/* Workspace */
.workspace { display: flex; flex: 1; overflow: hidden; }

/* Sidebar */
.sidebar {
    width: 250px; min-width: 40px;
    background: var(--sidebar-bg); border-right: 1px solid var(--border-color);
    display: flex; flex-direction: column; overflow: hidden; flex-shrink: 0;
}
.sidebar.collapsed { width: 0; min-width: 0; border-right: none; overflow: hidden; }
.sidebar-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 8px 12px; border-bottom: 1px solid var(--border-light);
}
.sidebar-title {
    font-weight: 600; font-size: 13px; text-transform: uppercase;
    letter-spacing: 0.5px; color: var(--text-secondary);
}

/* Editor Panel */
.editor-panel {
    flex: 1; display: flex; flex-direction: column;
    min-width: 200px; overflow: hidden;
}
.editor-container { flex: 1; overflow: hidden; position: relative; }

/* Preview Panel */
.preview-panel {
    width: 45%; min-width: 200px;
    display: flex; flex-direction: column;
    border-left: 1px solid var(--border-color);
    background: var(--bg-secondary); overflow: hidden; flex-shrink: 0;
}
.preview-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 4px 8px; border-bottom: 1px solid var(--border-color);
    background: var(--bg-tertiary); flex-shrink: 0;
}
.preview-content { flex: 1; overflow: hidden; position: relative; }
.preview-view {
    position: absolute; inset: 0; overflow: auto; display: none;
}
.preview-view.active { display: block; }

/* Resizer */
.resizer {
    width: 4px; background: var(--border-color); cursor: col-resize;
    flex-shrink: 0; transition: background 0.15s;
}
.resizer:hover, .resizer.active { background: var(--accent); }

/* Log Panel */
.log-panel {
    position: fixed; bottom: 0; left: 0; right: 0; height: 200px;
    background: var(--log-bg); border-top: 2px solid var(--accent);
    display: flex; flex-direction: column; z-index: 100;
}
.log-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 4px 12px; background: var(--bg-tertiary);
    border-bottom: 1px solid var(--border-color);
    font-size: 12px; font-weight: 600; color: var(--text-secondary);
}
.log-content {
    flex: 1; overflow: auto; padding: 8px 12px;
    font-family: 'Consolas', 'Monaco', monospace; font-size: 12px;
    color: var(--log-text); white-space: pre-wrap; word-break: break-word;
}
"""

_COMPONENTS = """
/* Buttons */
.btn {
    display: inline-flex; align-items: center; justify-content: center;
    padding: 4px 12px; border-radius: 4px; border: 1px solid var(--border-color);
    background: var(--bg-secondary); color: var(--text-primary);
    cursor: pointer; font-size: 13px; white-space: nowrap;
    transition: background 0.15s, border-color 0.15s;
}
.btn:hover { background: var(--hover-bg); border-color: var(--text-muted); }
.btn-primary { background: var(--accent); color: #fff; border-color: var(--accent); }
.btn-primary:hover { background: var(--accent-hover); border-color: var(--accent-hover); }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-secondary { background: var(--bg-tertiary); }
.btn-icon {
    padding: 4px 8px; background: transparent; border: none;
    font-size: 16px; color: var(--text-secondary);
}
.btn-icon:hover {
    color: var(--text-primary); background: var(--hover-bg); border-radius: 4px;
}
.btn-sm { padding: 2px 8px; font-size: 12px; }
select {
    padding: 4px 8px; border-radius: 4px; border: 1px solid var(--border-color);
    background: var(--bg-secondary); color: var(--text-primary);
    font-size: 13px; cursor: pointer;
}
select:focus { outline: 2px solid var(--accent); outline-offset: -1px; }

/* File Tree */
.file-tree { flex: 1; overflow-y: auto; padding: 4px 0; }
.file-tree .loading { padding: 20px; text-align: center; color: var(--text-muted); }
.tree-item {
    display: flex; align-items: center; padding: 3px 8px; cursor: pointer;
    font-size: 13px; color: var(--text-primary); user-select: none;
    border-left: 2px solid transparent;
}
.tree-item:hover { background: var(--hover-bg); }
.tree-item.active { background: var(--active-bg); border-left-color: var(--accent); }
.tree-item .icon {
    width: 18px; text-align: center; flex-shrink: 0;
    font-size: 12px; color: var(--text-muted); margin-right: 4px;
}
.tree-item .name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.tree-children { display: none; }
.tree-children.open { display: block; }
.tree-item[data-depth="1"] { padding-left: 20px; }
.tree-item[data-depth="2"] { padding-left: 36px; }
.tree-item[data-depth="3"] { padding-left: 52px; }
.tree-item[data-depth="4"] { padding-left: 68px; }
.tree-item[data-depth="5"] { padding-left: 84px; }

/* File Tabs */
.file-tabs {
    display: flex; align-items: center; gap: 0;
    background: var(--bg-tertiary); border-bottom: 1px solid var(--border-color);
    overflow-x: auto; flex-shrink: 0; min-height: 32px;
}
.file-tabs:empty { display: none; }
.file-tab {
    display: flex; align-items: center; gap: 6px;
    padding: 6px 12px; font-size: 13px; cursor: pointer;
    background: var(--tab-bg); border-right: 1px solid var(--border-color);
    color: var(--text-secondary); white-space: nowrap;
    border-bottom: 2px solid transparent;
}
.file-tab:hover { background: var(--hover-bg); }
.file-tab.active {
    background: var(--tab-active-bg); color: var(--text-primary);
    border-bottom-color: var(--accent);
}
.file-tab .tab-close {
    font-size: 14px; color: var(--text-muted);
    padding: 0 2px; border-radius: 2px; line-height: 1;
}
.file-tab .tab-close:hover { color: var(--danger); background: var(--hover-bg); }
.file-tab.modified .tab-name::after { content: ' \\25CF'; color: var(--warning); }

/* Welcome */
.welcome-message {
    display: flex; flex-direction: column; align-items: center;
    justify-content: center; height: 100%; color: var(--text-muted);
    text-align: center; padding: 40px;
}
.welcome-message h2 {
    font-size: 24px; font-weight: 300; margin-bottom: 12px;
    color: var(--text-secondary);
}
.welcome-message p { font-size: 14px; margin-bottom: 8px; }
.welcome-message .hint { font-size: 12px; color: var(--text-muted); }

/* Preview Tabs */
.preview-tabs { display: flex; gap: 4px; }
.preview-tab {
    padding: 4px 12px; font-size: 12px; border: none;
    background: transparent; color: var(--text-secondary);
    cursor: pointer; border-radius: 4px;
}
.preview-tab:hover { background: var(--hover-bg); }
.preview-tab.active {
    background: var(--accent-bg); color: var(--accent); font-weight: 600;
}

/* PDF */
.pdf-container {
    height: 100%; display: flex; flex-direction: column;
    align-items: center; overflow: auto; background: var(--bg-tertiary);
}
.pdf-placeholder {
    display: flex; flex-direction: column; align-items: center;
    justify-content: center; height: 100%; color: var(--text-muted);
    text-align: center;
}
.pdf-placeholder .hint { font-size: 12px; margin-top: 8px; }
#pdf-canvas {
    max-width: 100%; margin: 8px auto;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15); background: white;
}
.pdf-controls {
    display: flex; align-items: center; gap: 8px; padding: 6px 12px;
    background: var(--toolbar-bg); border-top: 1px solid var(--border-color);
    width: 100%; justify-content: center; flex-shrink: 0;
}
#pdf-page-info, #pdf-zoom-level {
    font-size: 12px; color: var(--text-secondary);
    min-width: 50px; text-align: center;
}

/* Bibliography */
.bib-list { padding: 12px; overflow-y: auto; height: 100%; }
.bib-entry {
    padding: 8px 12px; margin-bottom: 4px; border-radius: 4px;
    background: var(--bg-primary); border: 1px solid var(--border-light);
    font-size: 13px; cursor: pointer;
}
.bib-entry:hover { border-color: var(--accent); background: var(--accent-bg); }
.bib-entry .bib-key {
    font-weight: 600; font-family: monospace; color: var(--accent);
}
.bib-entry .bib-type {
    font-size: 11px; color: var(--text-muted); margin-left: 8px;
    text-transform: uppercase;
}
.bib-entry .bib-file { font-size: 11px; color: var(--text-muted); float: right; }

/* CodeMirror overrides */
.CodeMirror {
    height: 100% !important; font-size: 14px; line-height: 1.6;
    font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
    background: var(--cm-bg) !important; color: var(--cm-text) !important;
}
.CodeMirror-gutters {
    background: var(--cm-gutter-bg) !important;
    border-right: 1px solid var(--border-light) !important;
}
.CodeMirror-linenumber { color: var(--cm-gutter-text) !important; }
.CodeMirror-cursor { border-left-color: var(--cm-cursor) !important; }
.CodeMirror-selected { background: var(--cm-selection) !important; }
.cm-s-default .cm-keyword { color: var(--cm-keyword) !important; }
.cm-s-default .cm-atom { color: var(--cm-atom) !important; }
.cm-s-default .cm-number { color: var(--cm-number) !important; }
.cm-s-default .cm-def { color: var(--cm-def) !important; }
.cm-s-default .cm-variable { color: var(--cm-variable) !important; }
.cm-s-default .cm-string { color: var(--cm-string) !important; }
.cm-s-default .cm-comment { color: var(--cm-comment) !important; }
.cm-s-default .cm-bracket { color: var(--cm-bracket) !important; }
.cm-s-default .cm-tag { color: var(--cm-tag) !important; }
.cm-s-default .cm-attribute { color: var(--cm-attribute) !important; }
.CodeMirror-dialog {
    background: var(--bg-secondary) !important;
    color: var(--text-primary) !important;
    border-bottom: 1px solid var(--border-color) !important;
}
.CodeMirror-dialog input {
    color: var(--text-primary) !important;
    background: var(--bg-primary) !important;
    border: 1px solid var(--border-color) !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--scrollbar-thumb); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

/* Compilation spinner */
@keyframes spin { to { transform: rotate(360deg); } }
.compiling .btn-primary::after {
    content: ''; display: inline-block; width: 12px; height: 12px;
    border: 2px solid #fff; border-top-color: transparent;
    border-radius: 50%; animation: spin 0.8s linear infinite;
    margin-left: 6px;
}
"""


# EOF
