#!/bin/bash
# -*- coding: utf-8 -*-
# ROLE: engine-vendored — DO NOT edit here. `scitex-writer update-project`
# overwrites this file on every re-vendor; fix it upstream in the
# scitex-writer package instead (local edits are lost, and update-project
# may set it read-only in the consumer workspace after vendoring).
# File: scripts/shell/modules/check_spartan_login.sh
#
# Refuse to run the TeX toolchain on a Spartan HPC LOGIN node. Compiling
# (pdflatex/bibtex/latexmk) on a login node is prohibited heavy compute — admins
# kill the process and can sanction the account (HPC incident 2026-07-01,
# scitex-hpc). The login node now also runs a guard that REFUSES the toolchain
# with exit 100 + "[BLOCKED]" on stderr unless inside a SLURM job.
#
# This guard is PORTABLE: it is a no-op everywhere except a Spartan login node
# with no active SLURM job, and it does NOT bake SLURM into the compile engine —
# it only DETECTS the prohibited node and aborts with an actionable hint
# (route the build through srun on a compute node). The SLURM wrapper itself is
# owned by scitex-hpc's `spartan-tex` helper, not by scitex-writer.
#
# Detection (per scitex-hpc, in priority order):
#   1. hostname matches spartan-login*  (robust, independent of the guard)
#   2. AND no SLURM_JOB_ID  (bad state = login host outside a job)
# The guard's own contract (exit 100 / "[BLOCKED]") is the secondary signal if
# a real compile call is reached without this early check firing.

# Pure predicate: true (0) iff host is a Spartan login node AND not in a SLURM
# job. Args: $1=hostname, $2=SLURM_JOB_ID. Kept arg-driven so it is testable
# without spoofing uname/the environment.
_scitex_on_spartan_login_no_job() {
    local host="$1"
    local job="$2"
    case "$host" in
        spartan-login*)
            [ -z "$job" ] && return 0
            ;;
    esac
    return 1
}

# Guard: abort with an actionable hint when on a Spartan login node outside a
# SLURM job. Returns 0 (proceed) otherwise. Callers: `scitex_guard_spartan_login || exit 1`.
scitex_guard_spartan_login() {
    if _scitex_on_spartan_login_no_job "$(uname -n)" "${SLURM_JOB_ID:-}"; then
        cat >&2 <<'EOF'
ERRO:     Refusing to compile on a Spartan LOGIN node — running pdflatex/latexmk
ERRO:     here is prohibited heavy compute (admins kill it; the account can be
ERRO:     sanctioned). Re-run the build inside a SLURM job on a COMPUTE node:
ERRO:
ERRO:       srun --partition=cascade --qos=publiccpu --time=0:30:00 \
ERRO:            --cpus-per-task=2 --mem=4G bash scripts/shell/compile_manuscript.sh
ERRO:
ERRO:     Run it from the repo on SHARED storage ($HOME or /data, NOT /tmp —
ERRO:     login and compute nodes do not share /tmp). Quick ad-hoc alternative:
ERRO:     `spartan-tex <file.tex>` (scitex-hpc helper that wraps a compile in srun).
EOF
        return 1
    fi
    return 0
}

# When executed directly (not sourced), run the guard and exit with its code so
# callers can `"$PROJECT_ROOT/scripts/shell/modules/check_spartan_login.sh" || exit 1`.
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    scitex_guard_spartan_login || exit 1
fi
