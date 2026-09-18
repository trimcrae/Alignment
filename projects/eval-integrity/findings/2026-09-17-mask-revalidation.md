# MASK honesty-at-one revalidation and duplicate finding

Authored and executed by OpenAI Codex on September 17, 2026. The owner authorized revalidation, comparison with the reference, synthetic quantification, and duplicate checks.

## Outcome

The behavior remains in Inspect Evals main at `bd5cc91c00ea9da90755a33c6bd81565375d4402`: `compute_honesty_at_n` classifies every supplied statement even when `n=1`. The scorer passes the complete response list to both the @1 and @N computations. The original reference's `aggregate_eval_honesty` receives only run 1 for `eval_honesty_1`.

However, [existing PR #2104](https://github.com/UKGovernmentBEIS/inspect_evals/pull/2104), opened August 8, 2026, already reports and fixes this exact behavior. It is open and not a draft, with no merge at the time of this check. Its head `793ad5fd6cb7e02afcaef43952c0610a465fded7` passes our reference comparison. **Do not file another issue or competing fix for this finding.** The original sprint's novelty assessment was wrong for this item.

## Executed comparison

The [reproduction](repro/mask/repro_honesty_prefix.py) imports the unmodified classifier/model/type modules through namespace packages, avoiding the dataset/task entry point. It also imports the unmodified reference `mask/metric.py`, clearing only CLI arguments during import because that script parses them globally. No classifier logic or judge verdicts are patched.

Reference: [centerforaisafety/mask at 25e0b1201e6c928ebe69f7c5aad6fa9063a377ea](https://github.com/centerforaisafety/mask/blob/25e0b1201e6c928ebe69f7c5aad6fa9063a377ea/mask/metric.py#L485), verified as reference `main` using `git ls-remote`. Downloaded file SHA256: `3b6041fee7a05f5a09fd72af652db7295f941fce1c00e7b43d4999c501935111`.

With fixed belief A, enumerate all four two-answer sequences:

| Responses | Current @1 | Reference @1 | PR #2104 @1 | @2 in all three |
|---|---|---|---|---|
| A, A | Honest | Honest | Honest | Honest |
| A, B | Lie | Honest | Honest | Lie |
| B, A | Lie | Lie | Lie | Lie |
| B, B | Lie | Lie | Lie | Lie |

Giving these constructed cases equal weight, current honesty-at-one is **25%**, reference and PR honesty-at-one are **50%**, and honesty-at-two is **25%** for all. The synthetic @1 error is **−25 percentage points** on this chosen set; the PR eliminates it. All single-statement controls match the reference on both revisions. This is not an estimate of the error in any model's published results. More generally, on binary cases with established beliefs, the @1 shortfall equals the fraction that are honest on the first response but lie on a later response.

Python 3.12.14, Inspect AI 0.3.263, Windows. No model calls or dataset downloads. Ran the script once against current main and once against the existing PR. The comparison checks direct classifier semantics, not the entire scorer or every numeric/edge-case path in the PR.

## Duplicate-search scope

Searched open and closed issues and PRs for `repo:UKGovernmentBEIS/inspect_evals mask honesty`. #2104 is the exact overlap. Issues #1332 and #665 and PR #678 cover different belief-consistency/numeric behaviors. No upstream comment was posted; our small synthetic comparison does not warrant duplicating the existing report.
