#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_editor/_templates/_scripts_ui.py

"""JavaScript for compilation, PDF viewer, toolbar, and UI interactions."""

UI_SCRIPTS = """
// ===== Compilation =====
function startCompile() {
    if (state.compiling) return;

    // Save current file first
    if (state.activeTab !== null && state.editor) {
        var tab = state.openTabs[state.activeTab];
        tab.content = state.editor.getValue();
        if (tab.modified) {
            fetch('/api/file', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ path: tab.path, content: tab.content })
            }).then(function(r) { return r.json(); }).then(function(data) {
                if (data.success) {
                    tab.original = tab.content;
                    tab.modified = false;
                    renderTabs();
                }
            });
        }
    }

    var docType = document.getElementById('doc-type-select').value;
    state.compiling = true;
    document.body.classList.add('compiling');
    document.getElementById('btn-compile').disabled = true;
    document.getElementById('log-content').textContent = 'Starting compilation...\\n';
    document.getElementById('log-panel').style.display = '';

    fetch('/api/compile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ doc_type: docType })
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
        if (data.error) {
            document.getElementById('log-content').textContent += 'Error: ' + data.error + '\\n';
            state.compiling = false;
            document.body.classList.remove('compiling');
            document.getElementById('btn-compile').disabled = false;
            return;
        }
        pollCompilation();
    })
    .catch(function(err) {
        document.getElementById('log-content').textContent +=
            'Request failed: ' + err + '\\n';
        state.compiling = false;
        document.body.classList.remove('compiling');
        document.getElementById('btn-compile').disabled = false;
    });
}

function pollCompilation() {
    state.pollTimer = setInterval(function() {
        fetch('/api/compile/status')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (data.log) {
                    document.getElementById('log-content').textContent = data.log;
                }
                if (!data.compiling) {
                    clearInterval(state.pollTimer);
                    state.compiling = false;
                    document.body.classList.remove('compiling');
                    document.getElementById('btn-compile').disabled = false;
                    if (data.result && data.result.success) {
                        document.getElementById('log-content').textContent +=
                            '\\n\\nCompilation successful!';
                        loadPdf();
                    } else {
                        var err = data.result ?
                            (data.result.error || 'Unknown error') : 'Unknown error';
                        document.getElementById('log-content').textContent +=
                            '\\n\\nCompilation failed: ' + err;
                    }
                }
            });
    }, 1000);
}

// ===== PDF Viewer =====
function loadPdf() {
    var docType = document.getElementById('doc-type-select').value;
    var url = '/api/pdf?doc_type=' + docType + '&t=' + Date.now();

    pdfjsLib.GlobalWorkerOptions.workerSrc =
        'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

    pdfjsLib.getDocument(url).promise
        .then(function(pdf) {
            state.pdfDoc = pdf;
            state.pdfPage = 1;
            document.getElementById('pdf-placeholder').style.display = 'none';
            document.getElementById('pdf-canvas').style.display = '';
            document.getElementById('pdf-controls').style.display = '';
            renderPdfPage();
        })
        .catch(function(err) {
            document.getElementById('pdf-placeholder').innerHTML =
                '<p>Failed to load PDF</p><p class="hint">' +
                escapeHtml(String(err)) + '</p>';
            document.getElementById('pdf-placeholder').style.display = '';
        });
}

function renderPdfPage() {
    if (!state.pdfDoc) return;
    state.pdfDoc.getPage(state.pdfPage).then(function(page) {
        var canvas = document.getElementById('pdf-canvas');
        var ctx = canvas.getContext('2d');

        var container = document.getElementById('pdf-container');
        var containerWidth = container.clientWidth - 32;
        var unscaledViewport = page.getViewport({ scale: 1.0 });
        var fitScale = containerWidth / unscaledViewport.width;

        var scale = state.pdfScale === 0 ? fitScale : state.pdfScale;
        var viewport = page.getViewport({ scale: scale });

        var dpr = window.devicePixelRatio || 1;
        canvas.width = viewport.width * dpr;
        canvas.height = viewport.height * dpr;
        canvas.style.width = viewport.width + 'px';
        canvas.style.height = viewport.height + 'px';
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

        page.render({ canvasContext: ctx, viewport: viewport });

        document.getElementById('pdf-page-info').textContent =
            state.pdfPage + ' / ' + state.pdfDoc.numPages;
        var pctText = state.pdfScale === 0 ?
            'Fit' : Math.round(state.pdfScale * 100) + '%';
        document.getElementById('pdf-zoom-level').textContent = pctText;
    });
}

// ===== Bibliography =====
function loadBibEntries() {
    fetch('/api/bib/entries')
        .then(function(r) { return r.json(); })
        .then(function(data) {
            var container = document.getElementById('bib-list');
            if (!data.entries || data.entries.length === 0) {
                container.innerHTML =
                    '<div class="loading">No bibliography entries found.</div>';
                return;
            }
            container.innerHTML = '';
            data.entries.forEach(function(entry) {
                var el = document.createElement('div');
                el.className = 'bib-entry';
                el.innerHTML = '<span class="bib-key">' +
                    escapeHtml(entry.citation_key) + '</span>' +
                    '<span class="bib-type">' +
                    escapeHtml(entry.entry_type) + '</span>' +
                    '<span class="bib-file">' +
                    escapeHtml(entry.bibfile) + '</span>';
                el.addEventListener('click', function() {
                    if (state.editor) {
                        state.editor.replaceSelection(
                            '\\\\cite{' + entry.citation_key + '}');
                        state.editor.focus();
                    }
                });
                container.appendChild(el);
            });
        })
        .catch(function() {
            document.getElementById('bib-list').innerHTML =
                '<div class="loading">Error loading bibliography.</div>';
        });
}

// ===== Preview Tabs =====
function setupPreviewTabs() {
    document.querySelectorAll('.preview-tab').forEach(function(tab) {
        tab.addEventListener('click', function() {
            var view = this.getAttribute('data-view');
            document.querySelectorAll('.preview-tab').forEach(function(t) {
                t.classList.remove('active');
            });
            this.classList.add('active');
            document.querySelectorAll('.preview-view').forEach(function(v) {
                v.classList.remove('active');
            });
            document.getElementById(view + '-view').classList.add('active');
        });
    });
}

// ===== Toolbar =====
function setupToolbar() {
    document.getElementById('btn-compile').addEventListener('click', startCompile);

    document.getElementById('btn-toggle-log').addEventListener('click', function() {
        var logPanel = document.getElementById('log-panel');
        logPanel.style.display = logPanel.style.display === 'none' ? '' : 'none';
    });

    document.getElementById('btn-close-log').addEventListener('click', function() {
        document.getElementById('log-panel').style.display = 'none';
    });

    document.getElementById('btn-toggle-theme').addEventListener('click', toggleTheme);
    document.getElementById('btn-refresh-pdf').addEventListener('click', loadPdf);

    document.getElementById('btn-collapse-sidebar').addEventListener('click', function() {
        var sidebar = document.getElementById('sidebar');
        sidebar.classList.toggle('collapsed');
        var resizer = document.getElementById('sidebar-resizer');
        resizer.style.display = sidebar.classList.contains('collapsed') ? 'none' : '';
    });

    // PDF controls
    document.getElementById('btn-pdf-prev').addEventListener('click', function() {
        if (state.pdfPage > 1) { state.pdfPage--; renderPdfPage(); }
    });
    document.getElementById('btn-pdf-next').addEventListener('click', function() {
        if (state.pdfDoc && state.pdfPage < state.pdfDoc.numPages) {
            state.pdfPage++; renderPdfPage();
        }
    });
    document.getElementById('btn-pdf-zoom-in').addEventListener('click', function() {
        if (state.pdfScale === 0) state.pdfScale = 1.0;
        state.pdfScale = Math.min(state.pdfScale + 0.25, 4.0);
        renderPdfPage();
    });
    document.getElementById('btn-pdf-zoom-out').addEventListener('click', function() {
        if (state.pdfScale === 0) state.pdfScale = 1.0;
        state.pdfScale = Math.max(state.pdfScale - 0.25, 0.25);
        renderPdfPage();
    });
    document.getElementById('btn-pdf-fit').addEventListener('click', function() {
        state.pdfScale = 0;
        renderPdfPage();
    });

    document.getElementById('doc-type-select').addEventListener('change', loadPdf);
    loadPdf();
}

// ===== Theme Toggle =====
function toggleTheme() {
    var html = document.documentElement;
    var current = html.getAttribute('data-theme');
    var next = current === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', next);
    document.getElementById('theme-icon').innerHTML =
        next === 'dark' ? '&#9788;' : '&#9789;';
    localStorage.setItem('scitex-writer-theme', next);
    if (state.editor) state.editor.refresh();
}

// Restore saved theme
(function() {
    var saved = localStorage.getItem('scitex-writer-theme');
    if (saved) {
        document.documentElement.setAttribute('data-theme', saved);
        document.addEventListener('DOMContentLoaded', function() {
            document.getElementById('theme-icon').innerHTML =
                saved === 'dark' ? '&#9788;' : '&#9789;';
        });
    }
})();

// ===== Keyboard Shortcuts =====
function setupKeyboard() {
    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'B') {
            e.preventDefault(); startCompile();
        }
        if ((e.ctrlKey || e.metaKey) && !e.shiftKey && e.key === 's') {
            e.preventDefault(); saveCurrentFile();
        }
        if ((e.ctrlKey || e.metaKey) && e.key === 'w') {
            e.preventDefault();
            if (state.activeTab !== null) closeTab(state.activeTab);
        }
    });
}

// ===== Panel Resizers =====
function setupResizers() {
    document.querySelectorAll('.resizer').forEach(function(resizer) {
        var startX, startWidth, target, direction;

        resizer.addEventListener('mousedown', function(e) {
            e.preventDefault();
            var targetId = resizer.getAttribute('data-target');
            target = document.getElementById(targetId);
            direction = resizer.getAttribute('data-direction');
            startX = e.clientX;
            startWidth = target.offsetWidth;
            resizer.classList.add('active');
            document.addEventListener('mousemove', onMouseMove);
            document.addEventListener('mouseup', onMouseUp);
        });

        function onMouseMove(e) {
            var delta = direction === 'left' ?
                e.clientX - startX : startX - e.clientX;
            target.style.width = Math.max(40, startWidth + delta) + 'px';
        }

        function onMouseUp() {
            resizer.classList.remove('active');
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);
            if (state.editor) state.editor.refresh();
        }
    });
}
"""


# EOF
