#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: scripts/python/render_claims.py
# Purpose: Pre-compile generation step -- regenerate 00_shared/claims_rendered.tex
#          from 00_shared/claims.json (the \vclaim value SSoT) before the
#          manuscript is flattened. The shell compile path (compile_*.sh) did
#          NOT regenerate this file, so a stale/hand-edited claims_rendered.tex
#          could ship outdated \vclaim values (or a legacy prototype block)
#          into the PDF. render_claims() fully overwrites the file, so running
#          it here guarantees freshness.
#
#          FAIL LOUD: if claims.json exists but rendering fails, exit non-zero
#          so the compile aborts instead of shipping a stale file. No severity
#          knob -- a render failure when claims.json is present is always a
#          defect (malformed JSON / broken claim), unlike the style/policy
#          checks which a team may legitimately set to warn/off.
#
#          No-op (exit 0) when claims.json is absent: claims are optional.

import sys
from pathlib import Path


def main(argv) -> int:
    project_dir = argv[1] if len(argv) > 1 else "."
    project_path = Path(project_dir).resolve()
    claims_json = project_path / "00_shared" / "claims.json"

    if not claims_json.exists():
        return 0

    try:
        from scitex_writer._mcp.handlers._claim import render_claims
    except Exception as exc:  # ImportError or a broken install -- surface it
        print(
            f"ERRO:     Cannot import render_claims to regenerate "
            f"claims_rendered.tex: {exc}",
            file=sys.stderr,
        )
        return 1

    result = render_claims(str(project_path))
    if not result.get("success"):
        print(
            f"ERRO:     Failed to render claims_rendered.tex from {claims_json}: "
            f"{result.get('error', 'unknown error')}. Fix claims.json or the "
            f"claim definitions; compiling now would ship a stale "
            f"claims_rendered.tex.",
            file=sys.stderr,
        )
        return 1

    print(
        f"INFO:     Rendered claims_rendered.tex "
        f"({result.get('claims_count', 0)} claims) from claims.json"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

# EOF
