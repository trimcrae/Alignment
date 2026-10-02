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
  local repo="$1" pin="$2" target="$3" expected actual origin dirty
  local url="https://github.com/$repo"
  if [[ ! "$pin" =~ ^[0-9a-fA-F]{7,40}$ ]]; then
    echo "ERROR: invalid commit pin for $target" >&2; return 1
  fi

  if [ -e "$target" ] || [ -L "$target" ]; then
    # Existing work is read-only: refuse mismatches instead of fixing/resetting it.
    if [ -L "$target" ] || { [ ! -d "$target/.git" ] && [ ! -f "$target/.git" ]; }; then
      echo "ERROR: $target exists but is not a direct Git checkout" >&2; return 1
    fi
    origin=$(git -C "$target" config --get remote.origin.url) || {
      echo "ERROR: no origin in $target" >&2; return 1;
    }
    if [ "$origin" != "$url" ]; then
      echo "ERROR: wrong origin in $target; checkout left unchanged" >&2; return 1
    fi
    dirty=$(GIT_OPTIONAL_LOCKS=0 git -C "$target" status --porcelain --untracked-files=all) || return 1
    if [ -n "$dirty" ]; then
      echo "ERROR: dirty checkout $target; checkout left unchanged" >&2; return 1
    fi
    expected=$(git -C "$target" rev-parse --verify "$pin^{commit}" 2>/dev/null) || {
      echo "ERROR: pin $pin unavailable in $target; checkout left unchanged" >&2; return 1;
    }
    if [[ "$expected" != "${pin,,}"* ]]; then
      echo "ERROR: pin $pin resolved to another revision in $target; checkout left unchanged" >&2; return 1
    fi
    actual=$(git -C "$target" rev-parse --verify HEAD) || return 1
    if [ "$actual" != "$expected" ]; then
      echo "ERROR: wrong HEAD in $target; checkout left unchanged" >&2; return 1
    fi
    echo "verified $target at $expected"
    return 0
  fi

  git clone -q "$url" "$target" || return 1
  expected=$(git -C "$target" rev-parse --verify "$pin^{commit}" 2>/dev/null) || {
    git -C "$target" fetch -q --depth 1 origin "$pin" || return 1
    expected=$(git -C "$target" rev-parse --verify "$pin^{commit}" 2>/dev/null) || {
      echo "ERROR: pin $pin unavailable in $target" >&2; return 1;
    }
  }
  if [[ "$expected" != "${pin,,}"* ]]; then
    echo "ERROR: pin $pin resolved to another revision in $target" >&2; return 1
  fi
  git -C "$target" checkout -q --detach "$expected" || {
    echo "ERROR: could not check out pin $pin in $target" >&2; return 1;
  }
  actual=$(git -C "$target" rev-parse --verify HEAD) || return 1
  if [ "$actual" != "$expected" ]; then
    echo "ERROR: pin verification failed in $target" >&2; return 1
  fi
}

# Audit targets
clone UKGovernmentBEIS/inspect_evals   360484a inspect_evals
clone meridianlabs-ai/inspect_petri    e199ec1 inspect_petri
clone UKGovernmentBEIS/control-arena   b9d19de control_arena
clone METR/public-tasks                5418666 metr_public_tasks

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
