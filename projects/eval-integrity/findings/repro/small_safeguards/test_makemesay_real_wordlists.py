"""MakeMeSay: the SHIPPED word lists vs the debrief-message false-win bug (MMS-2)
and vs eval.yaml's dataset_samples (MMS-6).

The five jsonl files under ./wordlists/ were fetched from
https://media.githubusercontent.com/media/openai/evals/<pinned sha>/evals/registry/data/make_me_say/<d>.jsonl
(the LFS media endpoint; raw.githubusercontent.com serves only the LFS pointer).
Their sha256s equal inspect_evals/src/inspect_evals/makemesay/utils.py:CHECKSUMS,
i.e. these are byte-for-byte the files the port downloads and verifies.
"""

import hashlib
import json
from pathlib import Path

import pytest

from inspect_evals.makemesay.game import Game, Message, Player
from inspect_evals.makemesay.prompts import get_default_feedback_message
from inspect_evals.makemesay.scorer import makemesay_scorer
from inspect_evals.makemesay.utils import CHECKSUMS
from inspect_ai.scorer import Target
from types import SimpleNamespace

WORDLISTS = Path(__file__).parent / "wordlists"
VARIANTS = ["easy", "medium", "medium-and-hard", "hard", "very-hard"]


def _words(variant: str) -> list[str]:
    lines = (WORDLISTS / f"{variant}.jsonl").read_text().splitlines()
    return [json.loads(x)["input"]["codeword"] for x in lines if x.strip()]


def test_wordlists_are_the_files_the_port_verifies():
    for v in VARIANTS:
        digest = hashlib.sha256((WORDLISTS / f"{v}.jsonl").read_bytes()).hexdigest()
        assert digest == CHECKSUMS[v], v
        print(f"{v}: sha256 matches utils.py CHECKSUMS, {len(_words(v))} codewords")


def test_dataset_samples_189_is_the_sum_over_all_five_variants():
    counts = {v: len(_words(v)) for v in VARIANTS}
    total = sum(counts.values())
    print(f"\nper-variant counts: {counts}")
    print(f"sum over all variants = {total}; eval.yaml dataset_samples = 189")
    print(f"default variant 'medium-and-hard' = {counts['medium-and-hard']} samples")
    assert total == 189
    assert counts["medium-and-hard"] == 50


def _mentions(codeword: str, text: str) -> bool:
    g = Game(
        manipulator=Player(id="manipulator"),
        manipulatee=Player(id="manipulatee"),
        current_player=Player(id="manipulatee"),
        messages=(),
        word_list=(codeword,),
        max_turns=30,
    )
    return g._mentions_codeword(text)


def test_which_shipped_codewords_are_triggered_by_the_debrief_text():
    debrief = get_default_feedback_message(None)  # text is constant
    hits = {}
    for v in VARIANTS:
        hits[v] = [w for w in _words(v) if _mentions(w, debrief)]
    print("\ncodewords whose lemma appears in the debrief message (=> automatic is_win):")
    for v in VARIANTS:
        print(f"  {v:16s} {len(hits[v])}/{len(_words(v))}: {hits[v]}")
    # Result: only the `easy` variant is affected, and only via stop-words.
    assert hits["easy"], "expected easy-list hits"
    for v in ["medium", "medium-and-hard", "hard", "very-hard"]:
        assert hits[v] == [], f"{v} unexpectedly affected"
    print("=> default variant 'medium-and-hard' is NOT affected; only 'easy' (stop-words) is.")


@pytest.mark.asyncio
async def test_affected_default_codewords_score_win_with_nobody_saying_them():
    """Full port path: solver's debrief message + scorer, no player ever says the word."""
    debrief = get_default_feedback_message(None)
    affected = [w for w in _words("easy") if _mentions(w, debrief)][:4]
    scorer = makemesay_scorer()
    for w in affected:
        manipulator, manipulatee = Player(id="manipulator"), Player(id="manipulatee")
        msgs = (
            Message(role="system", content=f"codeword is {w}", name="manipulator"),
            Message(role="assistant", content="Nice weather today.", name="manipulator"),
            Message(role="assistant", content="Indeed it is.", name="manipulatee"),
            # exactly what solver.py:137-143 appends: role="user", name=manipulatee
            Message(role="user", content=debrief, name="manipulatee"),
            Message(role="assistant", content="I think the codeword was tulip", name="manipulatee"),
        )
        game = Game(manipulator, manipulatee, manipulatee, msgs, (w,), 30)
        state = SimpleNamespace(metadata={"game": game, "user_aware": False})
        score = await scorer(state, Target([w]))
        print(f"codeword={w!r} (easy list): nobody said it, guess was wrong -> is_win={game.is_win()} "
              f"outcome={score.answer!r} value={score.value!r}")
        assert game.is_win() is True
        assert score.answer == "win"


def test_is_over_postcondition_fails_after_a_finished_port_game():
    """solver.py adds the debrief as role="user" (ref: "system"), so after the game
    the manipulatee sees max_turns+2 non-system messages and is_over()'s
    post-condition (game.py:354, identical to reference core.py:320) is violated.
    Not reached by the scorer today, so latent."""
    manipulator, manipulatee = Player(id="manipulator"), Player(id="manipulatee")
    n = 4
    msgs = [
        Message(role="system", content="manipulator preamble", name="manipulator"),
        Message(role="system", content="manipulatee preamble", name="manipulatee"),
    ]
    for i in range(n):
        who = "manipulator" if i % 2 == 0 else "manipulatee"
        msgs.append(Message(role="assistant", content=f"turn {i}", name=who))
    msgs.append(Message(role="user", content="debrief", name="manipulatee"))  # solver.py:137-143
    msgs.append(Message(role="assistant", content="I think the codeword was tulip", name="manipulatee"))
    game = Game(manipulator, manipulatee, manipulatee, tuple(msgs), ("salmon",), n)
    non_system = [m for m in game.view_as(manipulatee) if m.role != "system"]
    print(f"\nmax_turns={n}; non-system messages the manipulatee sees after the game = {len(non_system)} "
          f"(post-condition allows <= {n + 1})")
    with pytest.raises(AssertionError):
        game.is_over()
    print("game.is_over() -> AssertionError (reference: debrief is a system message, so count is max_turns+1)")
