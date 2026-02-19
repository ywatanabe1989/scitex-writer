#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_editor/_templates/_styles_claims.py

"""CSS styles for the Claims panel and hover tooltip."""

CLAIMS_STYLES = """
/* ===== Claims Panel ===== */
.claims-toolbar {
    display: flex; align-items: center; gap: 8px;
    padding: 8px 12px; border-bottom: 1px solid var(--border-light);
    flex-shrink: 0;
}
.claims-count {
    font-size: 12px; color: var(--text-muted); margin-left: auto;
}
.claims-list {
    padding: 8px; overflow-y: auto; height: calc(100% - 44px);
    display: flex; flex-direction: column; gap: 6px;
}
.claims-empty {
    padding: 24px; text-align: center; color: var(--text-muted);
    font-size: 13px;
}
.claims-empty p { margin-bottom: 6px; }
.claims-empty .hint { font-size: 12px; }
.claims-empty code {
    font-family: monospace; background: var(--bg-tertiary);
    padding: 1px 4px; border-radius: 3px;
}

/* Claim Card */
.claim-card {
    background: var(--bg-primary); border: 1px solid var(--border-light);
    border-radius: 6px; padding: 8px 10px; font-size: 13px;
    transition: border-color 0.15s;
}
.claim-card:hover { border-color: var(--accent); }
.claim-card-header {
    display: flex; align-items: center; gap: 6px; margin-bottom: 4px;
}
.claim-card-id {
    font-family: monospace; font-weight: 600; color: var(--accent);
    font-size: 12px;
}
.claim-card-preview {
    color: var(--text-primary); margin-bottom: 4px;
    font-size: 12px; line-height: 1.4;
}
.claim-card-context {
    color: var(--text-muted); font-size: 11px; font-style: italic;
    margin-bottom: 4px;
}
.claim-card-actions {
    display: flex; gap: 6px; margin-top: 6px;
}

/* Claim Badges */
.claim-badge { font-size: 14px; }
.claim-badge-provenance { color: var(--success); }
.claim-badge-noprov { color: var(--text-muted); }
.claim-type-badge {
    font-size: 10px; padding: 1px 6px; border-radius: 10px;
    font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px;
}
.claim-type-statistic { background: #dbeafe; color: #1d4ed8; }
.claim-type-value     { background: #dcfce7; color: #166534; }
.claim-type-citation  { background: #fef3c7; color: #92400e; }
.claim-type-figure    { background: #f3e8ff; color: #7c3aed; }
.claim-type-table     { background: #ffe4e6; color: #be123c; }
[data-theme="dark"] .claim-type-statistic { background: #1e3a5f; color: #93c5fd; }
[data-theme="dark"] .claim-type-value     { background: #14532d; color: #86efac; }
[data-theme="dark"] .claim-type-citation  { background: #451a03; color: #fcd34d; }
[data-theme="dark"] .claim-type-figure    { background: #3b0764; color: #d8b4fe; }
[data-theme="dark"] .claim-type-table     { background: #500724; color: #fda4af; }

/* Claim buttons */
.claim-btn-inspect { color: var(--text-secondary); }
.claim-btn-insert  { background: var(--accent-bg); color: var(--accent);
                     border-color: var(--accent); }
.claim-btn-insert:hover { background: var(--accent); color: #fff; }

/* Inline Inspect Panel */
.claim-inspect-panel {
    margin-top: 8px; padding: 8px; border-radius: 4px;
    background: var(--bg-secondary); border: 1px solid var(--border-color);
    font-size: 12px;
}
.claim-inspect-loading { color: var(--text-muted); font-style: italic; padding: 4px 0; }
.inspect-styles { display: flex; flex-direction: column; gap: 4px; margin-bottom: 8px; }
.inspect-row { display: flex; gap: 8px; align-items: baseline; }
.inspect-chain-section { margin-top: 8px; }
.inspect-chain-diagram {
    margin-top: 6px; overflow: auto; max-height: 200px;
    background: var(--bg-primary); border-radius: 4px;
    border: 1px solid var(--border-light); padding: 4px;
}
.inspect-no-clew {
    padding: 6px; font-size: 11px;
    background: var(--bg-tertiary); border-radius: 4px;
}
.inspect-no-clew code {
    font-family: monospace; background: var(--bg-primary);
    padding: 1px 3px; border-radius: 2px;
}

/* Shared claim text helpers */
.ct-label {
    font-size: 11px; font-weight: 600; color: var(--text-muted);
    text-transform: uppercase; letter-spacing: 0.4px; white-space: nowrap;
    min-width: 56px;
}
.ct-value { color: var(--text-primary); font-size: 12px; }
.ct-latex { font-family: monospace; }
.ct-muted { color: var(--text-muted); }
.ct-mono  { font-family: monospace; word-break: break-all; }

/* Clew badge */
.ct-clew-badge {
    font-size: 10px; padding: 1px 5px; border-radius: 8px;
    background: var(--bg-tertiary); color: var(--text-muted);
    margin-left: 6px; vertical-align: middle;
}
.ct-clew-ok { background: #dcfce7; color: #166534; }
[data-theme="dark"] .ct-clew-ok { background: #14532d; color: #86efac; }

/* ===== Hover Tooltip ===== */
.claim-tooltip {
    position: fixed; z-index: 1000;
    width: 380px; max-width: calc(100vw - 24px);
    background: var(--bg-primary); border: 1px solid var(--border-color);
    border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    font-size: 13px; overflow: hidden;
}
.claim-tooltip-header {
    display: flex; align-items: center; gap: 8px;
    padding: 8px 12px; background: var(--bg-secondary);
    border-bottom: 1px solid var(--border-light);
}
.ct-id {
    font-family: monospace; font-weight: 700; color: var(--accent);
    font-size: 13px; flex: 1;
}
.ct-type-badge { font-size: 11px; }
.ct-close {
    background: none; border: none; cursor: pointer;
    color: var(--text-muted); font-size: 16px; line-height: 1;
    padding: 0 2px; border-radius: 3px;
}
.ct-close:hover { color: var(--danger); background: var(--hover-bg); }
.claim-tooltip-body {
    padding: 10px 12px; display: flex; flex-direction: column; gap: 6px;
}
.ct-section { display: flex; gap: 8px; align-items: baseline; }
.claim-tooltip-chain {
    padding: 8px 12px; border-top: 1px solid var(--border-light);
    background: var(--bg-secondary);
}
.ct-chain-label {
    display: flex; align-items: center;
    font-size: 11px; font-weight: 600; color: var(--text-muted);
    text-transform: uppercase; letter-spacing: 0.4px; margin-bottom: 6px;
}
.ct-chain-diagram {
    overflow: auto; max-height: 220px;
    background: var(--bg-primary); border-radius: 4px;
    border: 1px solid var(--border-light); padding: 4px;
}
.ct-chain-loading { color: var(--text-muted); font-style: italic; font-size: 12px; }
"""


# EOF
