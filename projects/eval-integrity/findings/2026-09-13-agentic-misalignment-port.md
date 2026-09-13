# Agentic misalignment port: broken safety-instruction condition, unpinned grader sampling, empty completions counted, zero standard error

```
Target:            UKGovernmentBEIS/inspect_evals, eval agentic_misalignment (task version 4-A)
Version:           inspect_evals commit 360484a (2026-09-12); reference anthropic-experimental/agentic-misalignment commit ea0630e (2025-06-19)
Defect classes:    5 (prompt plumbing), 3 (randomness), 4/9 (empty outputs coded as safe; denominators), 9 (missing standard error), 6 (fidelity)
Reproduction:      repro/agentic_misalignment/ (tests assert the reference behaviour, so a failing test is a confirmed divergence; 13 fail, 1 passes; run from the inspect_evals checkout with its venv)
Severity:          medium (four independent medium items; none exploitable by the evaluated model)
Confidence:        high; verified by reading the port and reference code and rerunning the reproductions
Disclosure:        drafted 2026-09-13; awaiting repo-owner review before an upstream issue is opened
Full audit:        2026-09-13-agentic-misalignment-full-audit.md (agent report, nine items, plus a list of what matched the reference byte for byte)
```

## Verified findings

1. **The `extra_system_instructions="dont"` and `"goal"` conditions send a literal `{company_name}` to the model.** `prompt_generator.py` lines 313 to 324 build the extra instructions with `{company_name}` in a plain string and pass it through `fill_template`, which is `string.Template.safe_substitute` and only substitutes `$name` forms; no variables file defines `company_name` anyway. The official generator uses f-strings with an undefined `company_name` and raises `NameError`, so the intended text was never exercised in the public code either. Effect: the "explicit safety instructions" ablation reported in Anthropic's write-up is not reproducible with either implementation, and the port silently ships a malformed instruction.
2. **The grader runs with provider-default sampling.** `scorers.py` lines 34 to 36 call `grader.generate(...)` with no `GenerateConfig`; every official classifier calls the grader with `temperature=0.0, max_tokens=2000`. Because the grader is not the active model, a CLI `--temperature 0` does not reach it. Effect: classifier verdicts are sampled at temperature 1, adding noise and breaking run-to-run reproducibility of the harmful rate.
3. **Empty model completions are graded and counted as not harmful.** `scorers.py` grades `state.output.completion` unconditionally; the official runner skips empty completions and re-samples them, so they never enter the denominator. Effect: models or providers that return empty or content-filtered outputs get a deflated harmful rate.
4. **Reported standard error is always zero.** The task builds a dataset with exactly one `Sample` (`agentic_misalignment.py` lines 108 to 125) and relies on epochs; Inspect reduces epochs per sample before metrics, and `stderr()` returns 0 for fewer than two samples. The README's "Epochs: 10" results table therefore carries no valid uncertainty, and every run reports `stderr: 0`.

Lower-severity items in the full audit: two leaking-scenario templates were edited from SummitBridge to NovaStar without a changelog entry; whitespace differences in the user message and the evaluation-awareness notice; an unfilled `${direction_modifier}` in the safety-plus-restriction cells that is inherited from the official templates; README grader-model drift.

## Proposed fixes

Fill the company name (or drop the placeholder) in the extra instructions and add a test that no `{` placeholder survives prompt generation; pass `GenerateConfig(temperature=0.0, max_tokens=2000)` to the grader; treat empty completions as unscored (or resample) rather than not harmful; and either expand the dataset to one sample per epoch so `stderr` is meaningful, or document that the metric has no uncertainty estimate. Items 2 to 4 change reported numbers and need a task-version bump with a changelog entry.
