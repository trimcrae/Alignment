#!/usr/bin/env bash
# Re-creates the cross-release diff of the MASK port and the reference-prompt
# provenance check used in findings/mask.md.  Needs pypi.org, files.pythonhosted.org
# and raw.githubusercontent.com.
#   bash findings/repro/mask/version_diff.sh
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
AUDIT=$(cd "$HERE/../../.." && pwd)
PY="$AUDIT/inspect_evals/.venv/bin/python"
WORK=$(mktemp -d)
curl -sS https://pypi.org/pypi/inspect-evals/json -o "$WORK/pypi.json"
for v in 0.16.0 0.17.0 0.18.0 0.19.0; do
  URL=$("$PY" -c "import json; d=json.load(open('$WORK/pypi.json')); print(next(f['url'] for f in d['releases']['$v'] if f['filename'].endswith('.whl')))")
  curl -sS -L -o "$WORK/w$v.whl" "$URL"
  "$PY" -c "import zipfile; z=zipfile.ZipFile('$WORK/w$v.whl'); z.extractall('$WORK/x$v', [n for n in z.namelist() if n.startswith('inspect_evals/mask/')])"
  echo "== $v: $(grep '^version' "$WORK/x$v/inspect_evals/mask/eval.yaml")"
done
echo "== src: $(grep '^version' "$AUDIT/inspect_evals/src/inspect_evals/mask/eval.yaml")"
for pair in "0.16.0 0.17.0" "0.17.0 0.18.0" "0.18.0 0.19.0"; do
  set -- $pair
  echo "## $1 -> $2 (code files that differ)"
  diff -r -q "$WORK/x$1/inspect_evals/mask" "$WORK/x$2/inspect_evals/mask" | grep -v "README\|appendix\|assets" || true
done
echo "## 0.19.0 -> src"
diff -r -u -x README.md -x appendix.md -x assets -x __pycache__ "$WORK/x0.19.0/inspect_evals/mask" "$AUDIT/inspect_evals/src/inspect_evals/mask" || true
echo "## reference prompts at d76dc0b (commit cited in port prompts.py) vs clone 25e0b12"
curl -sS -o "$WORK/ref_prompts_d76dc0b.py" https://raw.githubusercontent.com/centerforaisafety/mask/d76dc0bdd75fb79936958c4239536bb3fd96a9b7/mask/prompts/evaluation_prompts.py
diff "$WORK/ref_prompts_d76dc0b.py" "$AUDIT/mask_official/mask/prompts/evaluation_prompts.py" && echo IDENTICAL
rm -rf "$WORK"
