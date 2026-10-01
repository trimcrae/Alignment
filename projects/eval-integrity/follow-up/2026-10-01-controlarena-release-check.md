# ControlArena source release check

Produced by OpenAI Codex (AI agent), session `usage-sprint-2026-10-01-release-check`, against Alignment head `a09974d9fd9283473127b3b20f4a77c54afb0579`. Read-only collection finished **2026-10-01T22:48:44Z**. Verification: direct GitHub API ancestry comparisons and one pinned source read; independent AI spot-check of latest release metadata and its comparison. No package was downloaded or executed.

**No currently observed GitHub tag contains the confirmed fix commit in its ancestry.** All 86 observed public releases match 86 lightweight tag refs; every pinned tag commit is an ancestor of fix `5792fe40f7ee7fbf4537b79588872e28fd5dbce3`, rather than a descendant. GitHub reports `behind`, `ahead_by: 0`, and 13–903 commits behind. The latest published source release, [v19.0.0](https://github.com/UKGovernmentBEIS/control-arena/releases/tag/v19.0.0), also still contains the original faulty scorer inversion.

This resolves source-tag inclusion negatively at collection time. **Installed/distributed package inclusion remains unknown** because registry metadata, wheels and sdists were not inspected. GitHub source releases, release-note text, and package publication are separate facts.

| Observation | Exact evidence |
| --- | --- |
| Accepted fix integrated into main | [PR #883](https://github.com/UKGovernmentBEIS/control-arena/pull/883); commit `5792fe40f7ee7fbf4537b79588872e28fd5dbce3` |
| Full public release inventory | [100-item page 1](https://api.github.com/repos/UKGovernmentBEIS/control-arena/releases?per_page=100&page=1): 86 releases; [page 2](https://api.github.com/repos/UKGovernmentBEIS/control-arena/releases?per_page=100&page=2): empty |
| Full observed tag inventory | [Tag refs](https://api.github.com/repos/UKGovernmentBEIS/control-arena/git/refs/tags): 86 commit refs; identical names and SHAs before and after comparisons |
| Latest published release | v19.0.0, published 2026-07-31T11:31:42Z; non-draft, non-prerelease; no attached GitHub assets |
| Latest tag commit | [`6d7259ec00f505869705e05ecc84df19b6230c7b`](https://api.github.com/repos/UKGovernmentBEIS/control-arena/git/refs/tags/v19.0.0) |
| Fix-to-latest-tag ancestry | [Pinned comparison](https://api.github.com/repos/UKGovernmentBEIS/control-arena/compare/5792fe40f7ee7fbf4537b79588872e28fd5dbce3...6d7259ec00f505869705e05ecc84df19b6230c7b): behind, ahead 0, behind 13, merge-base exactly the tag commit |
| Latest-tag source | [Pinned scorer](https://github.com/UKGovernmentBEIS/control-arena/blob/6d7259ec00f505869705e05ecc84df19b6230c7b/control_arena/settings/sae_interp_sabotage/scorers.py); blob `43005f96e44866baff3be8135534a0203106cf47` |

The latest-tag source still assigns:

```python
response.value = INCORRECT if response.value == CORRECT else CORRECT
```

That is the original inversion which credits the non-CORRECT failure value as success. This is a static source observation, not a new execution or an estimate of live judge failures. The accepted fix on the previously pinned main source instead inverts only valid CORRECT/INCORRECT verdicts.

[Machine-readable receipts](2026-10-01-controlarena-release-check.json) retain all 86 tag names, release IDs/publication dates, asset counts, commit SHAs, comparison status/counts, and merge-base SHAs, with endpoint templates and collection provenance. Every comparison returned the requested fix as base, the tag as merge-base, zero ahead, and positive behind; no comparison failed. The latest release notes describe #852, not #883; their omission is recorded but is not used to prove exclusion.

The first sweep used the normal repository tags URL, which this connector rejects as an unapproved endpoint. The successful Git data refs endpoint supplied the complete observed tag list. Requests were not an atomic snapshot; the tag inventory was reread afterward and remained identical. Absence of the accepted commit does not rule out an equivalent independently implemented change under another SHA in every historical tag; only v19.0.0 source was separately inspected. Older releases expose 32 total attached assets; none were downloaded, so no artifact-content claim is made.

The reviewed ledger/code is unchanged. Its `release_status: not-checked` remains a package-release limitation; this dated artifact supplies the narrower source-tag result without extending schema 1. The unchanged implementation at `a09974d9fd9283473127b3b20f4a77c54afb0579` passed validation and all 41 cases in [Node 22 CI run 36936638185](https://github.com/trimcrae/Alignment/actions/runs/36936638185). This documentation/data update gets the same existing CI checks; no new regression test is needed for a static receipt collection.

The next useful evidence, if registry/package-read tools become available, is to identify the actual published distribution version, hash a retrieved artifact, and inspect its scorer content. Do not infer a released-package fix from main, a release workflow's intent, or an empty GitHub asset list.
