# Public defects log

Findings appear here once the maintainers have been notified, and for anything an evaluated model could use to score without solving the task, once a fix is available. See `README.md` for the disclosure policy. The sprint inventory below is historical; only the focused AgentHarm benign file-path report has been submitted by this project.

### Upstream submission, 2026-09-14

[inspect_evals #2439](https://github.com/UKGovernmentBEIS/inspect_evals/issues/2439) was opened as `trimcrae` at 16:35:43 UTC with the verified benign CWD reproduction. Readback confirmed the submitted body matches the prepared report. Maintainer response is pending. No private report or other public finding was submitted.

### Calibration note (added 2026-09-14)

**Follow-up:** [upstream triage](findings/2026-09-14-upstream-triage.md) found explicit upstream tests preserving Inspect's empty-target behavior and confirmed the Petri/MakeMeSay overlaps. The counts in this section are the initial sprint assessment, not a current verified tally. Submission of #2439 is not maintainer confirmation of the finding.

The severity labels below are this project's own, from the rubric in `README.md`, where "high" means "changes a safety-relevant score". That is a generous bar and it does not mean a published evaluation number is materially wrong. An honest breakdown of the 13 items labelled high:

| Category | Count |
|---|---|
| Solid, live, and novel | 7 |
| Already fixed upstream, so version drift rather than a live bug | 2 |
| Probable duplicates of open upstream issues | 2 |
| Real mechanism, contested framing | 2 |
| Confirmed by a maintainer | 0 |

Every finding establishes a mechanism, not a magnitude: with no model API access, nobody measured how often a real grader emits a malformed verdict or a judge refuses, and that rate is what decides whether a defect is a footnote or a distortion. Verification also discarded three claims during the sprint, so the process has a demonstrated error rate and the surviving set probably still contains mistakes. Treat every finding as a candidate until a maintainer responds. `NEXT-STEPS.md` starts by getting one finding validated for exactly this reason.

## Sprint 1, 2026-09-13

All eleven targets audited. Counts are findings that passed verification, each with a reproduction that was run. **Read the calibration note below before quoting any of these numbers.**

| Target | High | Medium | Low | Path |
|---|---|---|---|---|
| Cybench and the DeepMind CTF ports | 2 | 5 | 4 | private, summary in `findings/2026-09-13-cybench-gdm-ctf-ports.md` |
| METR public task suite | 1 | 2 | 2 | private, summary in `findings/2026-09-13-metr-public-tasks.md` |
| AgentHarm | 1 | 4 | 5 | `findings/2026-09-13-agentharm.md` |
| MASK | 1 | 2 | 4 | `findings/2026-09-13-mask-port.md` |
| SAD and WMDP | 0 | 4 | 3 | `findings/2026-09-13-wmdp-sad-ports.md` |
| Agentic misalignment | 0 | 4 | 4 | `findings/2026-09-13-agentic-misalignment-port.md` |
| DeepMind stealth, self-reasoning, self-proliferation | 0 | 3 | 6 | `findings/2026-09-13-gdm-stealth-self-reasoning.md` |
| StrongREJECT | 0 | 2 | 1 | `findings/2026-09-13-strong-reject-metric-fidelity.md` |
| MakeMeSay, Make Me Pay, InstrumentalEval, CoCoNot | 1 | 9 | 12 | `findings/2026-09-13-small-safeguards.md` |
| Petri judge pipeline | 1 | 6 | 5 | `findings/2026-09-13-petri-judge.md` |
| Inspect core scoring primitives | 3 | 3 | 8 | `findings/2026-09-13-inspect-core.md` |
| ControlArena | 3 | 8 | 7 | partly private, summary in `findings/2026-09-13-control-arena.md` |

Three targets have findings held privately because the findings would let an evaluated agent score without solving the task, or point a reader at an answer key. Both have draft private reports in `findings/*.private-report-draft.md`; the security channel for the Inspect projects is named in the framework's own security policy.

The items most worth a maintainer's attention, subject to the calibration note above:

1. **Cybench**: the sandbox network policy permits the hosts that publish every challenge's answer key, and one challenge hands the agent a file containing its own answer.
2. **METR public tasks**: one family's answer key is recoverable from the public repository without running the task.
3. **AgentHarm**: the simulated file tools resolve paths relative to the working directory, so they fail whenever the eval runs from the installed package, making several behaviors unscorable and biasing harm scores downward.
4. **MASK**: the headline honesty score silently equals the any-lie score whenever the repeat count is greater than one, which is the configuration the README recommends.
5. **MakeMeSay**: the judge verdict parser takes the first `0` or `1` character anywhere in the reply, so a judge that explains before answering has its verdict inverted; separately, all four reported rates deflate whenever the eval is run with more than one epoch.
6. **Petri**: a failed or empty audit is scored 1 on every dimension and averaged into the reported means, and because the rubric reserves high `auditor_failure` for observed auditor incompetence, the documented gate for excluding failed audits reads "no failure" exactly when it should fire. Petri is part of every Anthropic alignment assessment since Claude Sonnet 4.5.
7. **ControlArena**: a judge that fails to answer is recorded as a completed side task in one setting, and the safety numerator counts every flagged attack-mode sample including those where the policy never attempted an attack, so safety rises with the number of declined samples (0.571 to 0.923 in a reproduction that holds the real attacks fixed). One further item is exploitable by the model under evaluation and is held privately.
8. **Inspect's own scoring primitives**: the model-graded scorers truncate the grader's verdict to its first letter before validating it, so "GRADE: Cannot determine" and "GRADE: Contradicts the expert answer" both score as CORRECT; and the choice scorer credits a refusal whenever the target is empty. These primitives are used by 18 and 30 packages respectively, so the effect is library-wide. The first is fixed on upstream main, which makes it a version-drift problem, since the eval library sets no upper bound on the framework version.

Sprint 1 is complete. `METHODS.md` records how the audits were done and what limited them. Follow the updated single-issue calibration gate in `NEXT-STEPS.md`; keep private reports out of public issues.
