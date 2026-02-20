#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_editor/_templates/_scripts_editor.py

"""JavaScript for file tree, editor, and file operations."""

EDITOR_SCRIPTS = """
// ===== State =====
const state = {
    editor: null,
    openTabs: [],
    activeTab: null,
    pdfDoc: null,
    pdfPage: 1,
    pdfScale: 0,
    compiling: false,
    pollTimer: null
};

// ===== Init =====
document.addEventListener('DOMContentLoaded', function() {
    loadFileTree();
    loadBibEntries();
    setupResizers();
    setupToolbar();
    setupKeyboard();
    setupPreviewTabs();
    loadClaims();
    initClaims();
});

// ===== File Tree =====
function loadFileTree() {
    fetch('/api/files')
        .then(function(r) { return r.json(); })
        .then(function(data) {
            renderFileTree(data.tree, document.getElementById('file-tree'), 0);
        })
        .catch(function() {
            document.getElementById('file-tree').innerHTML =
                '<div class="loading">Error loading files</div>';
        });
}

function renderFileTree(items, container, depth) {
    container.innerHTML = '';
    items.forEach(function(item) {
        if (item.type === 'directory') {
            var dirEl = document.createElement('div');
            dirEl.className = 'tree-dir';

            var toggle = document.createElement('div');
            toggle.className = 'tree-item';
            toggle.setAttribute('data-depth', depth);
            toggle.innerHTML = '<span class="icon">&#9654;</span>' +
                '<span class="name">' + escapeHtml(item.name) + '</span>';

            var children = document.createElement('div');
            children.className = 'tree-children';

            toggle.addEventListener('click', (function(ch, tg) {
                return function() {
                    var isOpen = ch.classList.toggle('open');
                    tg.querySelector('.icon').innerHTML = isOpen ? '&#9660;' : '&#9654;';
                };
            })(children, toggle));

            if (depth === 0) {
                children.classList.add('open');
                toggle.querySelector('.icon').innerHTML = '&#9660;';
            }

            dirEl.appendChild(toggle);
            dirEl.appendChild(children);
            container.appendChild(dirEl);
            renderFileTree(item.children || [], children, depth + 1);
        } else {
            var fileEl = document.createElement('div');
            fileEl.className = 'tree-item';
            fileEl.setAttribute('data-depth', depth);
            fileEl.setAttribute('data-path', item.path);
            fileEl.innerHTML = '<span class="icon">' + getFileIcon(item.extension) +
                '</span><span class="name">' + escapeHtml(item.name) + '</span>';
            fileEl.addEventListener('click', (function(p, n) {
                return function() { openFile(p, n); };
            })(item.path, item.name));
            container.appendChild(fileEl);
        }
    });
}

function getFileIcon(ext) {
    var icons = {
        '.tex': '&#120029;', '.bib': '&#128218;', '.sty': '&#9881;',
        '.cls': '&#9881;', '.pdf': '&#128196;', '.png': '&#128247;',
        '.jpg': '&#128247;', '.svg': '&#128247;', '.csv': '&#128202;',
        '.yaml': '&#9881;', '.yml': '&#9881;', '.md': '&#128221;',
        '.txt': '&#128196;', '.py': '&#128013;', '.sh': '&#9881;'
    };
    return icons[ext] || '&#128196;';
}

// ===== File Open/Save =====
function openFile(path, name) {
    var existingIdx = -1;
    for (var i = 0; i < state.openTabs.length; i++) {
        if (state.openTabs[i].path === path) { existingIdx = i; break; }
    }
    if (existingIdx >= 0) { switchTab(existingIdx); return; }

    fetch('/api/file?path=' + encodeURIComponent(path))
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.error) { alert(data.error); return; }
            state.openTabs.push({
                path: data.path, name: data.name,
                content: data.content, original: data.content, modified: false
            });
            switchTab(state.openTabs.length - 1);
            renderTabs();
        });
}

function switchTab(idx) {
    if (idx < 0 || idx >= state.openTabs.length) return;

    if (state.activeTab !== null && state.editor && state.openTabs[state.activeTab]) {
        state.openTabs[state.activeTab].content = state.editor.getValue();
    }

    state.activeTab = idx;
    var tab = state.openTabs[idx];

    document.querySelectorAll('.tree-item.active').forEach(function(el) {
        el.classList.remove('active');
    });
    var treeItem = document.querySelector('.tree-item[data-path="' + tab.path + '"]');
    if (treeItem) treeItem.classList.add('active');

    document.getElementById('current-file').textContent = tab.path;

    var welcomeMsg = document.getElementById('welcome-message');
    if (welcomeMsg) welcomeMsg.style.display = 'none';

    if (!state.editor) {
        state.editor = CodeMirror(document.getElementById('editor-container'), {
            value: tab.content,
            mode: getMode(tab.name),
            lineNumbers: true,
            lineWrapping: true,
            matchBrackets: true,
            autoCloseBrackets: true,
            foldGutter: true,
            gutters: ['CodeMirror-linenumbers', 'CodeMirror-foldgutter'],
            indentUnit: 4, tabSize: 4, indentWithTabs: false,
            extraKeys: {
                'Ctrl-S': function() { saveCurrentFile(); },
                'Cmd-S': function() { saveCurrentFile(); },
                'Tab': function(cm) {
                    if (cm.somethingSelected()) cm.indentSelection('add');
                    else cm.replaceSelection('    ', 'end');
                }
            }
        });
        state.editor.on('change', function() {
            if (state.activeTab !== null) {
                var t = state.openTabs[state.activeTab];
                t.content = state.editor.getValue();
                var wasModified = t.modified;
                t.modified = (t.content !== t.original);
                if (wasModified !== t.modified) renderTabs();
            }
        });
    } else {
        state.editor.setValue(tab.content);
        state.editor.setOption('mode', getMode(tab.name));
        state.editor.clearHistory();
    }
    state.editor.refresh();
    renderTabs();
}

function getMode(filename) {
    if (/\\.(tex|sty|cls|bib)$/.test(filename)) return 'stex';
    return 'text/plain';
}

function closeTab(idx, event) {
    if (event) { event.stopPropagation(); event.preventDefault(); }
    var tab = state.openTabs[idx];
    if (tab.modified && !confirm('Unsaved changes in ' + tab.name + '. Discard?')) return;

    state.openTabs.splice(idx, 1);

    if (state.openTabs.length === 0) {
        state.activeTab = null;
        if (state.editor) {
            state.editor.toTextArea();
            state.editor = null;
            var ta = document.querySelector('#editor-container textarea');
            if (ta) ta.remove();
        }
        document.getElementById('current-file').textContent = 'No file open';
        var wm = document.getElementById('welcome-message');
        if (wm) wm.style.display = '';
        document.querySelectorAll('.tree-item.active').forEach(function(el) {
            el.classList.remove('active');
        });
    } else if (state.activeTab >= state.openTabs.length) {
        switchTab(state.openTabs.length - 1);
    } else if (state.activeTab === idx) {
        switchTab(Math.min(idx, state.openTabs.length - 1));
    } else if (state.activeTab > idx) {
        state.activeTab--;
    }
    renderTabs();
}

function saveCurrentFile() {
    if (state.activeTab === null || !state.editor) return;
    var tab = state.openTabs[state.activeTab];
    tab.content = state.editor.getValue();

    var statusEl = document.getElementById('save-status');
    statusEl.textContent = 'Saving...';
    statusEl.className = 'save-status saving';

    fetch('/api/file', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: tab.path, content: tab.content })
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
        if (data.success) {
            tab.original = tab.content;
            tab.modified = false;
            statusEl.textContent = 'Saved';
            statusEl.className = 'save-status saved';
            renderTabs();
            setTimeout(function() {
                statusEl.textContent = '';
                statusEl.className = 'save-status';
            }, 2000);
        } else {
            statusEl.textContent = 'Error: ' + (data.error || 'Unknown');
            statusEl.className = 'save-status error';
        }
    })
    .catch(function() {
        statusEl.textContent = 'Save failed';
        statusEl.className = 'save-status error';
    });
}

// ===== Tabs Rendering =====
function renderTabs() {
    var container = document.getElementById('file-tabs');
    container.innerHTML = '';
    state.openTabs.forEach(function(tab, idx) {
        var tabEl = document.createElement('div');
        tabEl.className = 'file-tab' +
            (idx === state.activeTab ? ' active' : '') +
            (tab.modified ? ' modified' : '');
        tabEl.innerHTML = '<span class="tab-name">' + escapeHtml(tab.name) +
            '</span><span class="tab-close">&times;</span>';
        tabEl.addEventListener('click', function() { switchTab(idx); });
        tabEl.querySelector('.tab-close').addEventListener('click', function(e) {
            closeTab(idx, e);
        });
        container.appendChild(tabEl);
    });
}

// ===== Utilities =====
function escapeHtml(str) {
    var div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}
"""


# EOF
