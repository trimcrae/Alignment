#!/usr/bin/env bash
# Rebuild the sprint-1 audit environment. The original lived in an ephemeral
# container scratchpad, so anything that needs to rerun a reproduction has to
# recreate it. Pins are the exact commits the sprint-1 findings were verified
# against; do not float them, or a reproduction may pass or fail for the wrong
# reason.
#
# Usage: bash setup-audit-env.sh [target-dir]      (default: ./audit)
set -euo pipefail
DIR="${1:-audit}"
mkdir -p "$DIR"; cd "$DIR"

clone() { # repo commit dir
  if [ -d "$3/.git" ]; then echo "skip $3 (exists)"; return; fi
  git clone -q "https://github.com/$1" "$3"
  git -C "$3" fetch -q --depth 1 origin "$2" 2>/dev/null || true
  git -C "$3" checkout -q "$2" 2>/dev/null || echo "WARNING: could not check out $2 in $3; findings may not reproduce"
}

# Audit targets
clone UKGovernmentBEIS/inspect_evals   360484a inspect_evals
clone meridianlabs-ai/inspect_petri    e199ec1 inspect_petri
clone UKGovernmentBEIS/control-arena   b9d19de control_arena
clone METR/public-tasks                5418666 metr_public_tasks
clone robocurve/inspect-robots         7e4d1b7 inspect_robots       # added 2026-09-19

# Reference implementations the findings diff against
clone LRudL/sad                        dfc5c98 sad_official
clone centerforaisafety/mask           25e0b12 mask_official
clone alexandrasouly/strongreject      f7cad6c strongreject_official
clone centerforaisafety/wmdp           c0b6c12 wmdp_official
clone google-deepmind/dangerous-capability-evaluations 4794011 gdm_dce_official
clone andyzorigin/cybench              1097a72 cybench_official
clone openai/evals                     8eac7a7 openai_evals_official
clone yf-he/InstrumentalEval           2696781 instrumentaleval_official
clone allenai/noncompliance            25bf77c coconot_official
clone anthropic-experimental/agentic-misalignment ea0630e agentic_misalignment_official
clone UKGovernmentBEIS/inspect_ai      ce5617d3 inspect_ai_target   # the version the core findings are against

# Python env. inspect_evals pins an exact uv version in pyproject.toml; honour it.
command -v uv >/dev/null || python3 -m pip install -q --user uv
UVREQ=$(grep -oP 'required-version = "==\K[0-9.]+' inspect_evals/pyproject.toml || true)
if [ -n "$UVREQ" ] && ! uv --version 2>/dev/null | grep -q "$UVREQ"; then
  python3 -m pip install -q --user "uv==$UVREQ"
fi
( cd inspect_evals && UV_HTTP_TIMEOUT=180 uv sync --python 3.11 --group dev \
    --extra gdm_stealth --extra makemesay --extra cybench )
( cd inspect_petri && UV_HTTP_TIMEOUT=180 uv sync --python 3.11 2>/dev/null || true )
( cd control_arena && UV_HTTP_TIMEOUT=180 uv sync --python 3.11 2>/dev/null || true )
# inspect-robots is numpy-only; its dev extra brings pytest. Run its repro with:
#   cd inspect_robots && .venv/bin/python -m pytest ../findings/repro/inspect_robots -q
( cd inspect_robots && uv venv -q .venv && UV_HTTP_TIMEOUT=180 uv pip install -q -e ".[dev]" 2>/dev/null || true )

cat <<'MSG'

Done. To rerun a reproduction, copy the folder you need from
projects/eval-integrity/findings/repro/<target>/ into this directory as
findings/repro/<target>/ (the scripts expect that layout), then:

  cd inspect_evals && .venv/bin/python -m pytest ../findings/repro/<target> -q

Known environment gaps that change results:
  - No Docker daemon: container-based scorers (Cybench, the DeepMind CTFs,
    METR task families, most ControlArena settings) cannot be executed.
  - huggingface.co blocked in the standard sandbox: dataset-download tests skip,
    and MASK/AgentHarm/CoCoNot loaders cannot run. A computer-use session with
    wider network access fixes this.
  - Some suites fail on a tiktoken download (openaipublic.blob.core.windows.net).
    Those failures are environmental, not findings; the Petri and small-safeguards
    repro folders carry token-count stubs that work around it.
MSG
