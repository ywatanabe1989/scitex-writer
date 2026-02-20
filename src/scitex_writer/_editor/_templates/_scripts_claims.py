#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_editor/_templates/_scripts_claims.py

"""JavaScript for the Claims panel and hover tooltip."""

CLAIMS_SCRIPTS = r"""
// ===== Claims =====

// Initialize Mermaid (called once after page load)
var mermaidReady = false;
function initMermaid() {
    if (typeof mermaid !== 'undefined' && !mermaidReady) {
        mermaid.initialize({
            startOnLoad: false,
            theme: document.documentElement.getAttribute('data-theme') === 'dark'
                    ? 'dark' : 'default',
            securityLevel: 'loose'
        });
        mermaidReady = true;
    }
}

// Render Mermaid code to SVG, inject into container element
async function renderMermaidDiagram(code, container) {
    initMermaid();
    if (!mermaidReady) {
        container.innerHTML = '<span class="ct-muted">Mermaid not loaded</span>';
        return;
    }
    try {
        var id = 'mermaid-' + Date.now();
        var result = await mermaid.render(id, code);
        container.innerHTML = result.svg;
        // Make SVG responsive
        var svg = container.querySelector('svg');
        if (svg) {
            svg.style.maxWidth = '100%';
            svg.style.height = 'auto';
        }
    } catch (e) {
        container.innerHTML = '<span class="ct-muted">Diagram error: ' + e.message + '</span>';
    }
}

// ---- Claims Panel ----

function loadClaims() {
    var list = document.getElementById('claims-list');
    var countEl = document.getElementById('claims-count');
    if (!list) return;
    list.innerHTML = '<div class="loading">Loading claims...</div>';

    fetch('/api/claims')
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (!data.success) {
                list.innerHTML = '<div class="claims-empty">Error: ' + (data.error || 'unknown') + '</div>';
                return;
            }
            if (data.count === 0) {
                list.innerHTML = '<div class="claims-empty">' +
                    '<p>No claims defined yet.</p>' +
                    '<p class="hint">Add claims to 00_shared/claims.json<br>' +
                    'or use the MCP tool <code>writer_add_claim</code>.</p>' +
                    '</div>';
                if (countEl) countEl.textContent = '';
                return;
            }
            if (countEl) countEl.textContent = data.count + ' claim' + (data.count !== 1 ? 's' : '');
            list.innerHTML = '';
            data.claims.forEach(function(claim) {
                list.appendChild(buildClaimCard(claim));
            });
        })
        .catch(function(e) {
            list.innerHTML = '<div class="claims-empty">Failed to load claims: ' + e + '</div>';
        });
}

function buildClaimCard(claim) {
    var card = document.createElement('div');
    card.className = 'claim-card';
    card.setAttribute('data-claim-id', claim.claim_id);

    var provenanceBadge = claim.has_provenance
        ? '<span class="claim-badge claim-badge-provenance" title="Has provenance">&#9679;</span>'
        : '<span class="claim-badge claim-badge-noprov" title="No provenance">&#9675;</span>';

    var typeBadge = '<span class="claim-type-badge claim-type-' + claim.type + '">'
        + claim.type + '</span>';

    card.innerHTML =
        '<div class="claim-card-header">' +
            '<span class="claim-card-id">' + escapeHtml(claim.claim_id) + '</span>' +
            typeBadge +
            provenanceBadge +
        '</div>' +
        '<div class="claim-card-preview">' + escapeHtml(claim.preview_nature) + '</div>' +
        (claim.context
            ? '<div class="claim-card-context">' + escapeHtml(claim.context) + '</div>'
            : '') +
        '<div class="claim-card-actions">' +
            '<button class="btn btn-sm btn-secondary claim-btn-inspect" ' +
                    'data-id="' + escapeHtml(claim.claim_id) + '"' +
                    'title="Inspect claim + chain">&#128270; Inspect</button>' +
            '<button class="btn btn-sm claim-btn-insert" ' +
                    'data-id="' + escapeHtml(claim.claim_id) + '" ' +
                    'title="Insert \\stxclaim{id} at cursor">&#8628; Insert</button>' +
        '</div>';

    // Inspect button → show tooltip panel inline (expanded card)
    card.querySelector('.claim-btn-inspect').addEventListener('click', function() {
        var id = this.getAttribute('data-id');
        showInspectPanel(id, card);
    });

    // Insert button → paste \stxclaim{id} into editor
    card.querySelector('.claim-btn-insert').addEventListener('click', function() {
        var id = this.getAttribute('data-id');
        if (state.editor) {
            state.editor.replaceSelection('\\stxclaim{' + id + '}');
            state.editor.focus();
        }
    });

    return card;
}

function showInspectPanel(claimId, card) {
    // Remove any existing inline inspect panels
    document.querySelectorAll('.claim-inspect-panel').forEach(function(el) {
        el.remove();
    });

    var panel = document.createElement('div');
    panel.className = 'claim-inspect-panel';
    panel.innerHTML = '<div class="claim-inspect-loading">Loading chain...</div>';
    card.appendChild(panel);

    fetch('/api/claims/' + encodeURIComponent(claimId) + '/chain')
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (!data.success) {
                panel.innerHTML = '<div class="ct-muted">Error: ' + data.error + '</div>';
                return;
            }
            var html = buildInspectPanelHTML(data);
            panel.innerHTML = html;

            // Render chain diagram if Mermaid code available
            if (data.mermaid) {
                var diagramEl = panel.querySelector('.inspect-chain-diagram');
                if (diagramEl) {
                    renderMermaidDiagram(data.mermaid, diagramEl);
                }
            }
        })
        .catch(function(e) {
            panel.innerHTML = '<div class="ct-muted">Failed: ' + e + '</div>';
        });
}

function buildInspectPanelHTML(data) {
    var p = data.previews || {};
    var claim = data.claim || {};
    var html = '<div class="inspect-styles">';
    html += '<div class="inspect-row"><span class="ct-label">Nature</span>' +
            '<span class="ct-value ct-latex">' + escapeHtml(p.nature || '') + '</span></div>';
    html += '<div class="inspect-row"><span class="ct-label">APA</span>' +
            '<span class="ct-value ct-latex">' + escapeHtml(p.apa || '') + '</span></div>';
    html += '<div class="inspect-row"><span class="ct-label">Plain</span>' +
            '<span class="ct-value">' + escapeHtml(p.plain || '') + '</span></div>';
    if (claim.context) {
        html += '<div class="inspect-row"><span class="ct-label">Context</span>' +
                '<span class="ct-value ct-muted">' + escapeHtml(claim.context) + '</span></div>';
    }
    if (claim.session_id || claim.output_file) {
        html += '<div class="inspect-row"><span class="ct-label">Session</span>' +
                '<span class="ct-value ct-mono ct-muted">' +
                escapeHtml(claim.session_id || '—') + '</span></div>';
        if (claim.output_file) {
            html += '<div class="inspect-row"><span class="ct-label">Source</span>' +
                    '<span class="ct-value ct-mono ct-muted">' +
                    escapeHtml(claim.output_file) + '</span></div>';
        }
    }
    html += '</div>';

    if (data.mermaid) {
        var badge = data.clew_available
            ? '<span class="ct-clew-badge ct-clew-ok">clew ✓</span>'
            : '';
        html += '<div class="inspect-chain-section">' +
                '<div class="ct-label">Verification Chain ' + badge + '</div>' +
                '<div class="inspect-chain-diagram"></div>' +
                '</div>';
    } else if (data.has_provenance && !data.clew_available) {
        html += '<div class="inspect-chain-section">' +
                '<div class="ct-muted inspect-no-clew">' +
                '&#9888; Provenance stored but <code>scitex.clew</code> not installed. ' +
                'Install scitex to visualize the chain.</div>' +
                '</div>';
    } else if (!data.has_provenance) {
        html += '<div class="inspect-chain-section">' +
                '<div class="ct-muted inspect-no-clew">' +
                'No provenance data. Add <code>session_id</code> or <code>output_file</code> ' +
                'to link this claim to a Clew-tracked computation.</div>' +
                '</div>';
    }

    return html;
}

// ---- Hover Tooltip ----

var _tooltipTimer = null;
var _activeTooltipId = null;

function findClaimIdAtPos(line, ch) {
    // Match \stxclaim{id} or \stxclaim[style]{id}
    var re = /\\stxclaim(?:\[[^\]]*\])?\{([^}]+)\}/g;
    var match;
    while ((match = re.exec(line)) !== null) {
        if (ch >= match.index && ch <= match.index + match[0].length) {
            return match[1];
        }
    }
    return null;
}

function setupClaimHover() {
    // Wait until editor is created, then attach listener
    var checkInterval = setInterval(function() {
        if (!state.editor) return;
        clearInterval(checkInterval);

        state.editor.getWrapperElement().addEventListener('mousemove', function(e) {
            if (!state.editor) return;
            try {
                var pos = state.editor.coordsChar({ left: e.clientX, top: e.clientY });
                var line = state.editor.getLine(pos.line) || '';
                var claimId = findClaimIdAtPos(line, pos.ch);
                if (claimId) {
                    if (claimId !== _activeTooltipId) {
                        clearTimeout(_tooltipTimer);
                        _tooltipTimer = setTimeout(function() {
                            showHoverTooltip(claimId, e.clientX, e.clientY);
                        }, 300); // 300ms debounce
                        _activeTooltipId = claimId;
                    }
                } else {
                    clearTimeout(_tooltipTimer);
                    _activeTooltipId = null;
                    // Give time for user to move mouse into tooltip
                    setTimeout(function() {
                        var tooltip = document.getElementById('claim-tooltip');
                        if (tooltip && !tooltip.matches(':hover')) {
                            hideClaimTooltip();
                        }
                    }, 400);
                }
            } catch(e) { /* coordsChar can throw on edge cases */ }
        });

        state.editor.getWrapperElement().addEventListener('mouseleave', function() {
            clearTimeout(_tooltipTimer);
            _activeTooltipId = null;
            setTimeout(function() {
                var tooltip = document.getElementById('claim-tooltip');
                if (tooltip && !tooltip.matches(':hover')) {
                    hideClaimTooltip();
                }
            }, 500);
        });
    }, 200);

    // Tooltip stays visible while hovered
    var tooltip = document.getElementById('claim-tooltip');
    if (tooltip) {
        tooltip.addEventListener('mouseleave', function() {
            hideClaimTooltip();
        });
        document.getElementById('ct-close').addEventListener('click', function() {
            hideClaimTooltip();
        });
    }
}

function showHoverTooltip(claimId, mouseX, mouseY) {
    var tooltip = document.getElementById('claim-tooltip');
    if (!tooltip) return;

    // Reset tooltip content
    document.getElementById('ct-id').textContent = claimId;
    document.getElementById('ct-type').textContent = '';
    document.getElementById('ct-nature').textContent = '';
    document.getElementById('ct-apa').textContent = '';
    document.getElementById('ct-plain').textContent = '';
    document.getElementById('ct-context-section').style.display = 'none';
    document.getElementById('ct-provenance-section').style.display = 'none';
    document.getElementById('ct-chain-section').style.display = 'none';
    document.getElementById('ct-chain-diagram').innerHTML =
        '<div class="ct-chain-loading">Loading chain...</div>';

    // Position tooltip near mouse, keeping in viewport
    tooltip.style.display = 'block';
    var vw = window.innerWidth, vh = window.innerHeight;
    var tw = Math.min(tooltip.offsetWidth || 400, 420);
    var left = Math.min(mouseX + 12, vw - tw - 12);
    var top = mouseY + 20;
    if (top + 300 > vh) top = mouseY - 320;
    tooltip.style.left = left + 'px';
    tooltip.style.top = top + 'px';

    // Fetch claim + chain data
    fetch('/api/claims/' + encodeURIComponent(claimId) + '/chain')
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (!data.success) {
                document.getElementById('ct-nature').textContent = 'Claim not found';
                return;
            }
            populateTooltip(data);
        })
        .catch(function(e) {
            document.getElementById('ct-nature').textContent = 'Error: ' + e;
        });
}

function populateTooltip(data) {
    var claim = data.claim || {};
    var previews = data.previews || {};

    document.getElementById('ct-type').textContent = claim.type || '';
    document.getElementById('ct-nature').textContent = previews.nature || '';
    document.getElementById('ct-apa').textContent = previews.apa || '';
    document.getElementById('ct-plain').textContent = previews.plain || '';

    if (claim.context) {
        document.getElementById('ct-context').textContent = claim.context;
        document.getElementById('ct-context-section').style.display = '';
    }

    if (claim.session_id || claim.output_file) {
        var prov = [];
        if (claim.session_id) prov.push('session: ' + claim.session_id);
        if (claim.output_file) prov.push('file: ' + claim.output_file);
        document.getElementById('ct-provenance').textContent = prov.join('\n');
        document.getElementById('ct-provenance-section').style.display = '';
    }

    if (data.mermaid) {
        var chainSection = document.getElementById('ct-chain-section');
        chainSection.style.display = '';
        var badge = document.getElementById('ct-clew-badge');
        badge.textContent = data.clew_available ? 'clew ✓' : '';
        badge.className = 'ct-clew-badge' + (data.clew_available ? ' ct-clew-ok' : '');
        var diagramEl = document.getElementById('ct-chain-diagram');
        renderMermaidDiagram(data.mermaid, diagramEl);
    } else if (data.has_provenance) {
        var chainSection2 = document.getElementById('ct-chain-section');
        chainSection2.style.display = '';
        document.getElementById('ct-chain-diagram').innerHTML =
            '<span class="ct-muted">Install scitex to visualize the chain.</span>';
    }
}

function hideClaimTooltip() {
    var tooltip = document.getElementById('claim-tooltip');
    if (tooltip) tooltip.style.display = 'none';
    _activeTooltipId = null;
}

// ---- Init ----

function initClaims() {
    // Refresh claims button
    var btnRefresh = document.getElementById('btn-refresh-claims');
    if (btnRefresh) btnRefresh.addEventListener('click', loadClaims);

    // Render .tex button
    var btnRender = document.getElementById('btn-render-claims');
    if (btnRender) {
        btnRender.addEventListener('click', function() {
            btnRender.disabled = true;
            btnRender.textContent = 'Rendering...';
            fetch('/api/claims/render', { method: 'POST' })
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    btnRender.disabled = false;
                    btnRender.innerHTML = '&#9881; Render .tex';
                    if (data.success) {
                        btnRender.title = 'Rendered ' + data.claims_count + ' claims';
                    }
                })
                .catch(function() {
                    btnRender.disabled = false;
                    btnRender.innerHTML = '&#9881; Render .tex';
                });
        });
    }

    // Setup hover detection
    setupClaimHover();
    initMermaid();
}
"""
