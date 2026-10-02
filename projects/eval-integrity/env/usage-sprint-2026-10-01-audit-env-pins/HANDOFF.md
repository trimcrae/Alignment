# Audit environment pin enforcement handoff

AI-authored by OpenAI Codex, session `usage-sprint-2026-10-01`; completed October 2, 2026 UTC. Repository: `trimcrae/Alignment`. [Draft PR11](https://github.com/trimcrae/Alignment/pull/11), branch `codex/usage-sprint-2026-10-01-audit-env-pins`. Main remains `c79d38e9e49d9c2fd133b6c4faf6412760089afe`; no merge is authorized. Human review remains pending.

## Completed work

The original repository-owned setup helper, Git blob `b976c94e104274876257832224bb7bf53995f0e8`, returned success for an existing checkout without checking its origin or revision, and converted failed pin checkout into a successful warning. Actual offline Bash/Git witnesses reproduced both mechanisms.

The repaired helper accepts an existing checkout only after matching the configured origin, refusing source-masking index flags and ordinary dirty state, resolving the literal hexadecimal pin, and matching HEAD. Existing mismatches are refused without resetting, checking out, fetching, clearing flags, rewriting configuration or cleaning files. New checkout failures are fatal. A resolved branch/tag cannot substitute another commit for the literal pin.

All 15 original pin declarations and the setup header/installation/reproduction tail are byte-identical. All 116 original non-setup file blobs are unchanged. No scientific findings, source evidence, provider ledgers or completed sprint branch were rewritten.

## Actual validation and review

Reviewed/tested source: `1d7eb0ac1b39ca603d56b9e848dc8d09789da0ae`, tree `627a234d5abbc24698e5001c3bdba594eb623163`. [Actual CI37001446934](https://github.com/trimcrae/Alignment/actions/runs/37001446934), job `110819822258`, attempt 1, completed SUCCESS at that exact head. Bash 5.2.21, Git 2.55.0 and Python 3.12.3 executed **31 unittest methods in 3.455 seconds, OK**: two original-helper witnesses, one source-bound prior-repair witness and 28 final controls. Syntax, original Git blob bindings, unchanged prefix/tail/pins and clean tracked checkout also passed.

The actual PR checkout `b32677f473b4d6a9adb7ff57d741926faed5b51c` has that identical tree and parents `c79d38e9` + `1d7eb0ac`. The independent AI reviewer separately read source/methods, exact CI, original transcripts and checkout/source trees; those gates cleared. No human-review or independent scientific-evaluation claim is made.

[Earlier CI37000800204](https://github.com/trimcrae/Alignment/actions/runs/37000800204) at `61ddfd3722a1fd163a3f33e0146155f5bb7110ca` also succeeded: 27 methods in 1.281 seconds. Packaging review then identified that Git status can conceal changed tracked bytes under assume-unchanged/skip-worktree flags. The final source-bound witness actually demonstrated that **our earlier repair** admitted such an edit; final controls refuse the flags and preserve exact state. The earlier run was successful and did not cover this edge; it is not described as a baseline or environment failure.

The original logs are retained unchanged: `initial-ci.log`, 18,971 UTF-8 bytes, SHA256 `cf509e2417c4e3b35a4ef4a93fc15574e310d785a1ffa57998e8eeb0e1853de3`; `final-ci.log`, 19,815 bytes, SHA256 `290336141523e861e6a436070a4c1155bbc2a677e445924a892e42ce5fc23400`. Exact receipts and tested Git blobs are in [validation-receipt.json](validation-receipt.json).

## Limits and next bounded action

Tests use real Bash/Git in temporary Linux repositories, with file-only transport; the forced checkout-failure control wraps only that Git command. They are not Node/browser/model/scientific evaluations. Full setup was executed only through a deliberate first-target refusal before installation; no real uv/pip, upstream source checkout, model/API, paid job, outreach, upstream submission or main merge occurred. This work is available in public draft PR11.

Configured origin strings and literal abbreviated pins are checked; remote ownership/transport and dependency reproducibility are not authenticated. Ignored environment/build outputs remain allowed and unverified. Sparse/skip-worktree or assume-unchanged checkouts are refused; no index flag repair occurs. New failed clones may remain for inspection, with no destructive cleanup.

The next bounded action is owner review of draft PR11. Reopen runtime work only for a distinct demonstrated admission defect or changed relevant source. Preserve the existing missing-input results and completed provider/source routes; do not repeat unchanged audits or extend the finite sprint.
