"""Dataset-level checks against the reference data (via the port's own loader).

* Every SAD-mini task has a constant option count (2 or 4), so the port's per-sample 1/n
  imputation equals the official per-task `random_chance` (0.5 / 0.25) -> Checked OK.
* facts_human_defaults: 301 of 1200 samples are exact duplicates (same body, choices and id)
  present in both the `general_ai` and `good_text_model` batches. The official pile also
  counts 1200, so this is a comparability note, not a port divergence.
* influence: official public pile = 256; port = 255 (drops the one broken sample). Documented.
"""

import collections

from inspect_evals.sad.download_data import SAD, load_validate_files

OFFICIAL_RANDOM_CHANCE = {  # sad_official/sad/*/run.py Task(..., random_chance)
    SAD.FACTS_HUMAN_DEFAULTS: 0.5,
    SAD.FACTS_LLMS: 0.5,
    SAD.INFLUENCE: 0.5,
    SAD.STAGES_FULL: 0.25,
    SAD.STAGES_OVERSIGHT: 0.5,
}


def test_constant_option_counts_match_official_random_chance(sad_cache):
    print()
    for task in SAD:
        recs = load_validate_files(task)
        counts = collections.Counter(1 + len(r.choices_wrong) for r in recs)
        print(f"{task.value}: n={len(recs)} options-per-sample={dict(counts)} official r={OFFICIAL_RANDOM_CHANCE[task]}")
        assert len(counts) == 1
        (n_opts,) = counts
        assert abs(1 / n_opts - OFFICIAL_RANDOM_CHANCE[task]) < 1e-9


def test_facts_human_defaults_exact_duplicates(sad_cache):
    recs = load_validate_files(SAD.FACTS_HUMAN_DEFAULTS)
    keys = collections.Counter((r.body, tuple(r.choices_right), tuple(r.choices_wrong)) for r in recs)
    extra = sum(v - 1 for v in keys.values() if v > 1)
    ids = collections.Counter(r.id for r in recs)
    print(f"\nfacts_human_defaults: {len(recs)} samples, {len(keys)} unique (body,choices), {extra} exact duplicate copies, "
          f"{sum(1 for v in ids.values() if v > 1)} duplicated ids")
    assert len(recs) == 1200 and extra == 301 and len(keys) == 899


def test_sample_counts(sad_cache):
    counts = {t.value: len(load_validate_files(t)) for t in SAD}
    print(f"\nport sample counts: {counts}")
    assert counts == {"facts_human_defaults": 1200, "facts_llms": 249, "influence": 255, "stages_full": 800, "stages_oversight": 400}
