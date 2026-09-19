# Eval-integrity audit program

Status: sprint 1 complete (2026-09-13). All eleven targets audited; see `CHANGELOG.md` for the index and its calibration note, `findings/` for the write-ups, `METHODS.md` for how it was done, and `NEXT-STEPS.md` for what to do next. Of the findings labelled high severity, 7 look solid, live and novel; none has been confirmed by a maintainer, and nothing has been filed upstream. Three targets have findings held privately. A twelfth target, Inspect Robots, was added at the owner's request on 2026-09-19 and audited the same day: one reportable defect with a verified fix, drafted for filing.

## Purpose

Find and fix defects in the open-source safety evaluations that labs, AI security institutes, and researchers run on frontier models: exploitable scorers, ground-truth errors, unseeded randomness, judge and parser bugs, prompt plumbing mistakes, deviations from the paper being implemented, contamination hygiene, and sandbox leakage. These numbers feed system cards, risk reports, and safety cases, so a scorer that awards credit to garbage or a judge that silently lowers a concern score produces false assurance about exactly the capabilities and propensities that matter for catastrophic risk.

## Why this fits the repo

- Needs careful code reading and tests, not GPUs or an API key.
- Findings are concrete, reproducible, and reportable. A failing test is convincing regardless of who wrote it.
- Maintainers ask for this. The UK AISI eval library's contributor guide says it "relied (and continues to rely!) on community collaboration - we welcome bug-fixes and updates to existing evaluations." METR's public-task README says the tasks "may contain bugs or issues" and asks for bug reports. Recent issue trackers show the defects are real: unseeded shuffles in several evals, a judge parser that inverts results, a benchmark with a 54% ground-truth failure rate, six scorer exploits in METR's public tasks, and a Petri issue where judge refusals silently lower reported concern.

## Targets

Tier 1: open evals that demonstrably appear in system cards or institute pre-deployment testing.

| Target | Where | Why it matters |
|---|---|---|
| Cybench | `inspect_evals/cybench` | Used by the US and UK AISIs in joint pre-deployment tests and reported in Anthropic system cards since Claude 3.7 Sonnet |
| DeepMind dangerous-capability suites | `inspect_evals/gdm_capabilities/*` (in-house CTF, InterCode CTF, self-proliferation, self-reasoning, stealth) | Open-sourced by DeepMind; the evaluation families behind its Frontier Safety Framework reporting |
| Petri judge and aggregation | `meridianlabs-ai/inspect_petri` | Part of every Anthropic alignment assessment since Claude Sonnet 4.5; used by UK AISI; adapted by DeepMind |
| Safeguards catalog | `inspect_evals`: `strong_reject`, `agentharm`, `agentharm_benign`, `wmdp_*`, `mask`, `lab_bench_protocolqa`, `coconot`, `makemesay`, `make_me_pay` | Default choices for jailbreak, misuse, and honesty measurements in papers and cards |
| Scheming catalog | `inspect_evals`: `agentic_misalignment`, `sad_*`, `instrumentaleval`, `gdm_stealth` family | Propensity evals that feed alignment assessments; several already have open integrity issues |
| METR public tasks | `METR/public-tasks` (31 tasks in 10 families) and `METR/inspect-tasks-public` (RE-Bench port) | Autonomy and AI R&D capability measurement; scorer exploits already found in some families |
| ControlArena settings | `UKGovernmentBEIS/control-arena` | Side-task scorers and safety calculations behind control evaluations |

Added 2026-09-19 at the owner's request:

| Target | Where | Why it matters |
|---|---|---|
| Inspect Robots | `robocurve/inspect-robots` (the framework behind [inspectrobots.org](https://inspectrobots.org)) | Open evaluation framework for physical AI, "the Inspect AI for robotics": runs VLA and LLM-agent policies on real arms, humanoids and simulators and writes schema-versioned eval logs. Its scorer, grader, reducer and logging code is the substrate every benchmark built on it inherits, including Robocurve's independent real-world benchmarks. Maintainers respond to issues within days and accept fixes with tests; contributor guide requires 100 percent coverage and the `CubePick` mock world for reproductions. |

Tier 2: Bloom behavior configs, Inspect Scout scanners, MonitorBench, VLAF, SLEIGHT-Bench scoring, EvalDetectBench, HCAST public tasks.

## Defect checklist

1. **Scorer exploitability.** Can a trivial, empty, or garbage submission score? Does the scorer run code from an agent-writable path? Are tests unchanged when the answer is replaced with nonsense?
2. **Ground truth.** Mislabeled, ambiguous, or duplicated items; answers that are wrong in the source dataset; items whose answer appears in the prompt.
3. **Randomness.** Unseeded shuffles or sampling that make runs non-reproducible or change the effective dataset between runs.
4. **Judge and parsing.** Regexes or parsers that invert, truncate, or mis-extract verdicts; refusals or empty outputs coded as low concern; judge prompts that leak the expected answer.
5. **Prompt plumbing.** Duplicated system messages, truncated inputs, tool configurations that differ from the paper, missing few-shot examples.
6. **Paper fidelity.** Implementation differs from the published scoring or prompts in ways that break comparability with reported baselines.
7. **Contamination hygiene.** Missing canary strings; datasets loaded from unpinned sources; answers or solutions present in public scraped text.
8. **Sandbox and tool leakage.** Flags or answer keys reachable from the agent's environment; network access in sandboxes that should be isolated; scorer secrets in images.
9. **Metrics.** Wrong aggregation, missing standard errors, pass@k mislabeled as pass@1, per-sample scores averaged over the wrong denominator.
10. **Versioning.** Behavior changes without a task-version bump, which silently breaks comparisons with older logs.

## Method per target

1. Read the paper or specification the eval implements, then the implementation, dataset loader, scorer, and sandbox configuration.
2. Run the eval's existing unit tests locally. Note failures and untested paths.
3. Run the pipeline end to end without a real model where possible: Inspect's mock model provider for plumbing and scoring, a scripted "adversarial submission" for scorer exploitability, and a tiny open model on CPU for smoke tests.
4. For each suspected defect, write a minimal failing test or a reproduction script that a maintainer can run in under a minute.
5. Estimate impact: does it change reported numbers, in which direction, and roughly how much? A defect that only affects logging is still worth fixing but is a lower priority than one that inflates a safety-relevant score.
6. Record the finding using the template below, then follow the disclosure policy.

## Disclosure policy

- **Scorer exploits and anything that could be used to game a benchmark** go to the maintainers privately first (security contact, private report, or a maintainer email), never as public exploit code. METR asks that task solutions not be published; that request is honored without exception.
- **Ordinary bugs** (parsing, seeding, plumbing, metrics) become a public upstream issue plus a PR with a test, following the target repo's contributor guide, task-versioning rules, and changelog requirements.
- **Human review is mandatory.** The UK AISI eval library requires that all code produced by language models or agents be reviewed and tested by a human before submission. The repo owner reviews every issue and PR before it is opened, and every artifact states that it was produced by an AI agent with human review.
- **Public findings log.** A finding appears in the public changelog in this directory only after the maintainers have been notified and, for exploits, after a fix is available.

## Deliverables

- `findings/`: one file per finding, using the template below.
- `CHANGELOG.md`: the public defects log, updated after disclosure.
- Upstream issues and PRs, linked from the findings.
- A short methods note once the first ten findings are in, so other auditors can repeat the process.

## Finding template

```
Target:            <repo / eval / task>
Version:           <commit SHA or task version>
Defect class:      <1-10 from the checklist>
Summary:           <one sentence>
Reproduction:      <test file or script, and how to run it>
Impact:            <which reported number changes, direction, rough magnitude>
Severity:          <high: changes a safety-relevant score | medium: breaks comparability or reproducibility | low: logging or docs>
Disclosure:        <private report sent YYYY-MM-DD | public issue #N | PR #N | fixed in vX>
Notes:             <anything a maintainer needs>
```

## First sprint (proposed)

1. Set up the UK AISI eval library in this environment (GitHub and PyPI are reachable here; Hugging Face is not, so dataset-download tests need a session with wider network access or GitHub Actions). Run the test suite for the tier-1 evals and record what is untested.
2. Audit the small, self-contained, heavily used safeguards evals first: `strong_reject`, `agentharm`, `wmdp_*`, `mask`, `sad_*`. Their scorers and loaders are short enough to read completely.
3. Audit Cybench and the DeepMind in-house CTF suite for flag and answer-key reachability from the agent sandbox, scorer hygiene, and paper fidelity.
4. Audit Petri's judge aggregation and refusal handling, starting from the open issue about judge refusals.
5. Audit the METR public task families not covered by the August and September 2026 reports.

## Environment notes

This sandbox can clone GitHub repositories and install from PyPI, so static analysis, unit tests, and mock-model runs work here. Dataset downloads from Hugging Face and fetches of papers or lab pages need a session with wider network access. Nothing in this program requires an API key.
