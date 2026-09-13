# WMDP and SAD ports: lenient SAD parser credits prose that starts with the right letter; unseeded shuffles; verbatim SAD items in a public repo; WMDP protocol differs from the paper

```
Target:            UKGovernmentBEIS/inspect_evals, evals sad (task version 3-A) and wmdp (task version 2-A)
Version:           inspect_evals commit 360484a (2026-09-12); references LRudL/sad commit dfc5c98 with its scoring library LRudL/evalugator commit 1787ab8; centerforaisafety/wmdp commit c0b6c12 plus lm-evaluation-harness v0.4.2 task configs
Defect classes:    4/1 (SAD parser), 3 (unseeded randomness), 7 (contamination hygiene), 6 (WMDP protocol fidelity)
Reproduction:      repro/sad/ and repro/wmdp/ (20 tests, all pass; the SAD fixtures stage the reference clone's data zips into a temporary cache so the port's own loader runs unmodified)
Severity:          medium for each of the four items
Confidence:        high (parser and seeding verified by reading the code and rerunning the reproductions)
Disclosure:        drafted 2026-09-13; awaiting repo-owner review before an upstream issue is opened. The contamination item should go to the maintainers and the SAD authors without quoting the affected items.
Full audit:        2026-09-13-wmdp-sad-full-audit.md (agent report, with SAD item texts redacted)
```

## Verified findings

1. **SAD's `lenient_mcq_choice` credits any completion that starts with the correct option's letter or text.** `scorer.py` `_matches_choice_pattern` returns `response.startswith((letter, f"({letter})", choice_text))`, and the scorer checks the correct choice first. So a refusal beginning "As an AI..." is CORRECT whenever the target is A, and a wrong answer whose text extends the correct text (for example "Surely not" against "Surely") is CORRECT. The official parser (in the evalugator library) treats a letter followed by another letter as a word, only accepts `(X)`, `X)` or a bare `X`, and never matches choice text for SAD's templates; unparsed answers score 0 per sample with a chance-level correction at the task level. With choice shuffling on, the error averages toward chance but still misclassifies samples; with `shuffle_choices=False`, every "A"-initial refusal scores 1.0. The agent counted 91, 24 and 7 samples in the three facts and influence tasks whose wrong-answer text collides this way.
2. **Choice order and stages wording are shuffled without a seed by default** (confirms upstream issue #2401 and extends it). `dataset.py` calls `shuffle_choices(seed=None)`; `stages.py` re-seeds the process-global `random` module per sample (`random.seed(None)` by default) and draws wording and placement from it, which also clobbers global RNG state for everything else in the process. The reference renders every sample with a deterministic seed chain starting at 42. Two default loads of `facts_llms` differ on 119 of 249 targets.
3. **Verbatim SAD questions and answers are committed in plain text in the public inspect_evals repository** (tests and README for the SAD port), and no file carries the SAD canary string. The SAD README states that question and answer texts must never appear in plain text anywhere scrapable, including private repositories, which is why the official data ships as encrypted zips with a canary. No score effect; erodes the benchmark's anti-contamination guarantee. File and line references are in the full audit; the texts are not reproduced here.
4. **WMDP is scored generatively rather than by log-likelihood.** The port uses `multiple_choice()` and `choice()`, so a model must emit `ANSWER: X`; refusals, bare letters, and restated answers all score INCORRECT. The WMDP README says evaluation used lm-evaluation-harness v0.4.2, whose task config is a forced log-likelihood choice over A to D. The port's README does not say the protocol differs. Effect: not comparable with the paper's baselines, and downward for models that refuse hazardous questions, which matters when WMDP is used to measure unlearning.

Lower-severity items in the full audit: SAD situating-prompt whitespace differences, no `max_tokens` where the reference sets 10 or 20, and a WMDP test that needs the Hugging Face Hub but lacks the marker that skips it offline.

## Proposed fixes

Replace the prefix match with the official parsing rules (letter must not be followed by another letter; no choice-text matching for SAD templates) and add tests for prose and colliding texts; seed the choice shuffle and the stages wording from a private `random.Random` derived from the sample id, defaulting to a fixed seed, with a comparability version bump; remove the plain-text SAD items from tests and README (use synthetic fixtures) and notify the SAD authors; document the WMDP protocol difference in its README or add a log-likelihood variant.
