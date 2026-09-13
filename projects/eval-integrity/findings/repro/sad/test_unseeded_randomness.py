"""Finding: SAD tasks randomise without a seed by default (inspect_evals issue #2401 family).

1. `get_SAD_dataset(..., seed=None)` -> `MemoryDataset.shuffle_choices(seed=None)` ->
   `random.Random(None)` (OS entropy). Two default loads give different targets.
2. `stages_user_prompt_modifier(task, seed=None)` calls `random.seed(None)` and then
   `random.choice(...)` twice, so the question wording and above/below placement are
   also unseeded, AND the *global* `random` module state is reseeded per sample.
Reference: evalugator SimpleEval(seed=42) + seed_generator -> every sample rendered with
seed 42, 43, ... (choice order, template choice and text variant all deterministic).
"""

import asyncio
import hashlib
import random

from inspect_ai.model import ChatMessageUser, ModelName
from inspect_ai.solver import TaskState

from inspect_evals.sad.dataset import get_SAD_dataset
from inspect_evals.sad.download_data import SAD
from inspect_evals.sad.sad import sad_facts_llms, sad_stages_full
from inspect_evals.sad.stages import stages_user_prompt_modifier


def _targets(ds):
    return [s.target for s in ds]


def test_default_choice_shuffle_is_unseeded(sad_cache):
    a = get_SAD_dataset(SAD.FACTS_LLMS)  # defaults: shuffle_choices=True, seed=None
    b = get_SAD_dataset(SAD.FACTS_LLMS)
    diff = sum(x != y for x, y in zip(_targets(a), _targets(b)))
    print(f"\nfacts_llms: {len(a)} samples, targets differ between two default loads on {diff} samples")
    assert diff > 0, "two default loads gave identical choice orders (would be astronomically unlikely if unseeded)"

    s1 = get_SAD_dataset(SAD.FACTS_LLMS, seed=0)
    s2 = get_SAD_dataset(SAD.FACTS_LLMS, seed=0)
    assert _targets(s1) == _targets(s2), "seeded loads should be deterministic"


def test_task_default_seed_is_none(sad_cache):
    t1 = sad_facts_llms()
    t2 = sad_facts_llms()
    diff = sum(x != y for x, y in zip(_targets(t1.dataset), _targets(t2.dataset)))
    print(f"sad_facts_llms(): two default task constructions differ on {diff}/{len(t1.dataset)} targets")
    assert diff > 0


def _state(sample_id: str) -> TaskState:
    return TaskState(
        model=ModelName("mockllm/model"),
        sample_id=sample_id,
        epoch=1,
        input="BODY",
        messages=[ChatMessageUser(content="BODY")],
        choices=["a", "b", "c", "d"],
    )


async def _identity(state, *args, **kwargs):
    return state


def test_stages_prompt_variant_is_unseeded_by_default():
    solver = stages_user_prompt_modifier(SAD.STAGES_FULL, seed=None)
    outs = set()
    for _ in range(60):
        st = asyncio.run(solver(_state("stages_full:0"), _identity))
        outs.add(st.user_prompt.text)
    print(f"stages_full sample 'stages_full:0' rendered {len(outs)} distinct prompts over 60 default runs")
    assert len(outs) > 1, "prompt wording/placement should vary across runs when unseeded"


def test_stages_solver_reseeds_global_random_module():
    """The solver calls random.seed(...) on the process-global RNG, clobbering it for everyone."""
    solver = stages_user_prompt_modifier(SAD.STAGES_FULL, seed=42)
    sample_id = "stages_full:7"
    expected_seed = int(hashlib.sha256(f"42:{sample_id}".encode()).hexdigest(), 16)

    random.seed(123456)  # some unrelated caller's state
    before = random.getstate()
    asyncio.run(solver(_state(sample_id), _identity))
    after_solver = random.random()

    random.seed(expected_seed)
    random.choice(["above", "below"])
    random.choice([0, 1])
    predicted = random.random()

    print(f"random.random() after solver = {after_solver!r}; predicted from sha256(42:{sample_id}) = {predicted!r}")
    assert after_solver == predicted, "global random state was not reseeded as expected"
    random.setstate(before)
    assert random.random() != after_solver  # the original stream was different -> state was clobbered


def test_stages_full_task_default_prompts_nondeterministic(sad_cache):
    t = sad_stages_full()
    assert t.dataset[0].target in "ABCD"
    # solver[0] is stages_user_prompt_modifier(task, seed=None)
    solver = t.solver[0]
    outs = set()
    for _ in range(40):
        st = asyncio.run(solver(_state("stages_full:0"), _identity))
        outs.add(st.user_prompt.text)
    print(f"sad_stages_full() default: {len(outs)} distinct user prompts for the same sample over 40 runs")
    assert len(outs) > 1
