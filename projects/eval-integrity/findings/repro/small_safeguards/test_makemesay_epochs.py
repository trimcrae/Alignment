"""MakeMeSay: all four rate metrics key off Score.answer (a label string), which
inspect_ai's epoch reducer sets to None whenever the epochs disagree.

makemesay's Task sets no `epochs=`, so `--epochs N` uses the default reducer
(inspect_ai/_eval/task/results.py:366-367 -> mean_score()), and
inspect_ai/scorer/_reducer/reducer.py:556-566 keeps `answer` only if it is equal
across all epochs. The metrics in makemesay/scorer.py:19-58 divide by
len(scores), so a sample with mixed outcomes lands in the denominator of all four
rates and the numerator of none.
"""

from inspect_ai.scorer import CORRECT, INCORRECT, SampleScore, Score, mean_score

from inspect_evals.makemesay.scorer import (
    loss_rate,
    user_aware_of_manipulation_rate,
    violation_rate,
    win_rate,
)

OUTCOMES = ["win", "loss", "violation of rules", "user aware of manipulation"]


def _rates(sample_scores):
    return {
        "win_rate": win_rate()(sample_scores),
        "loss_rate": loss_rate()(sample_scores),
        "violation_rate": violation_rate()(sample_scores),
        "user_aware_rate": user_aware_of_manipulation_rate()(sample_scores),
    }


def test_epoch_reducer_nulls_the_outcome_label_and_deflates_every_rate():
    reducer = mean_score()

    # sample A: won in both epochs.  sample B: won once, lost once.
    a = [Score(value=CORRECT, answer="win"), Score(value=CORRECT, answer="win")]
    b = [Score(value=CORRECT, answer="win"), Score(value=INCORRECT, answer="loss")]

    ra, rb = reducer(a), reducer(b)
    print(f"\nsample A epochs ['win','win']  -> reduced value={ra.value!r} answer={ra.answer!r}")
    print(f"sample B epochs ['win','loss'] -> reduced value={rb.value!r} answer={rb.answer!r}")
    assert ra.answer == "win"
    assert rb.answer is None

    reduced = [SampleScore(score=ra, sample_id="A"), SampleScore(score=rb, sample_id="B")]
    rates = _rates(reduced)
    print(f"metrics over the 2 reduced samples: {rates}")
    print(f"sum of the four rates = {sum(rates.values())} (should be 1.0)")
    assert rates["win_rate"] == 0.5  # the mixed sample is not counted anywhere
    assert sum(rates.values()) == 0.5

    # 1 epoch, same two games: rates sum to 1 and win_rate is 0.75 across 4 games
    single = [
        SampleScore(score=Score(value=CORRECT, answer="win"), sample_id="A1"),
        SampleScore(score=Score(value=CORRECT, answer="win"), sample_id="A2"),
        SampleScore(score=Score(value=CORRECT, answer="win"), sample_id="B1"),
        SampleScore(score=Score(value=INCORRECT, answer="loss"), sample_id="B2"),
    ]
    rates_single = _rates(single)
    print(f"the same four games scored as separate samples: {rates_single} "
          f"(sum={sum(rates_single.values())})")
    assert sum(rates_single.values()) == 1.0


def test_every_pair_of_differing_outcomes_loses_its_label():
    reducer = mean_score()
    for i, o1 in enumerate(OUTCOMES):
        for o2 in OUTCOMES[i + 1:]:
            r = reducer([
                Score(value=CORRECT if o1 == "win" else INCORRECT, answer=o1),
                Score(value=CORRECT if o2 == "win" else INCORRECT, answer=o2),
            ])
            print(f"epochs ({o1!r}, {o2!r}) -> answer={r.answer!r}")
            assert r.answer is None
