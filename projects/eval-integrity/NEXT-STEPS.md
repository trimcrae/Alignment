# Next steps

Written 2026-09-14 at the end of the first working session, for whoever picks this up next. Sprint 1 (the audit) is done. Nothing has been sent to any maintainer, and no finding has been confirmed by anyone outside this repo.

## Read this first: the claim was overstated, and has been corrected

The first write-up of sprint 1 led with "13 high-severity findings". That number is technically what the severity rubric produced, but as a headline it oversells the result, and the repo owner was right to challenge it. The honest breakdown of those 13:

| Category | Count |
|---|---|
| Solid, live, and novel | 7 |
| Already fixed upstream, so version drift rather than a live bug | 2 |
| Probable duplicates of open upstream issues | 2 |
| Real mechanism, contested framing | 2 |
| Confirmed by a maintainer | 0 |

Two further caveats that matter more than the count. First, every finding establishes a **mechanism**, not a **magnitude**: without model API access nobody measured how often a real grader writes a malformed verdict or how often a judge refuses, and a mechanism that fires once in a thousand samples is a footnote while the same mechanism at one in ten moves published numbers. Second, verification discarded three claims during the sprint (one hypothesis of the auditing agent's own about shared metadata, and two subagent claims), so the process has a demonstrated error rate and the surviving set probably still contains mistakes. Treat the findings as candidates until a maintainer says otherwise.

## Step 1. Get one finding validated before spending anyone's attention on the rest

This is the highest-value next action and it is cheap. Do not file thirteen issues.

File exactly one, chosen to be unambiguous, still live upstream, and checkable by a maintainer in under a minute: **Inspect's `choice()` scorer credits a refusal when the target is empty**. It is two lines of cause, it is present on upstream main as well as the audited build, it contains no exploit content, and the reproduction is three assertions. The draft is in `findings/2026-09-13-inspect-core.upstream-issue-draft.md`, issue A, first paragraph; split that paragraph out and file it alone.

Then wait for the response, and use it to calibrate:

- **Confirmed and fixed** → the severity bar is roughly right. File the rest in the order given in step 3.
- **Confirmed but "working as intended"** → the bar is too generous. Re-triage everything labelled high, demote anything resting on a documented-but-surprising behaviour, and file only what survives.
- **Dismissed as wrong** → stop filing. Re-verify the remaining findings against a maintainer's reasoning before going further, because the same error probably recurs.

## Step 2. Send the three private reports

These are held back because they would let an evaluated model score without doing the task, or point a reader at an answer key. Each has a drafted report in `findings/*.private-report-draft.md`. The repo owner sends them; the agent does not contact anyone.

| Target | Channel | Draft |
|---|---|---|
| Cybench and the DeepMind CTF ports | security@meridianlabs.ai, the address in the Inspect security policy | `findings/2026-09-13-cybench-gdm-ctf-ports.private-report-draft.md` |
| METR public task suite | METR directly; no published security address was found, so ask them for one or use a maintainer contact | `findings/2026-09-13-metr-public-tasks.private-report-draft.md` |
| ControlArena | security@meridianlabs.ai for the Inspect-side pieces; the UK AI Security Institute and Redwood Research jointly maintain the library | `findings/2026-09-13-control-arena.private-report-draft.md` |

**The three full private reports are not in this repository, by design, and they are not on any disk that survives.** They exist only as the three files delivered into the conversation on 2026-09-13, captioned as withheld from the public repo. Retrieve them from there. If they are lost, the sanitized summaries in `findings/` plus a rerun of the reproductions can rebuild them, but that costs a session.

## Step 3. Filing order for the public findings, once step 1 says the bar is calibrated

Highest signal first, and one issue per repository per topic rather than one giant issue.

1. Inspect core, the remaining items in issue A, plus issue B asking which released versions carry the already-fixed defects, plus issue C asking the eval library to pin an upper bound. Drafts in `findings/2026-09-13-inspect-core.upstream-issue-draft.md`.
2. Petri's empty-transcript scoring. Check first whether it duplicates the open issue that could not be read from the sandbox; if it does, add the aggregate effect and the polarity argument as a comment on that issue instead of opening a new one. Draft in `findings/2026-09-13-petri-judge.upstream-issue-draft.md`.
3. AgentHarm's working-directory-relative tool paths. Draft in `findings/2026-09-13-agentharm.upstream-issue-draft.md`.
4. MASK's honesty metric. Draft in `findings/2026-09-13-mask-port.upstream-issue-draft.md`.
5. ControlArena's public items. Draft inside the private report; split the non-exploit items out.
6. The small-safeguards set. The MakeMeSay parser item belongs as a comment on the existing open issue, not a new one. Draft in `findings/2026-09-13-small-safeguards.upstream-issue-draft.md`.
7. StrongREJECT, SAD and WMDP, agentic misalignment, the DeepMind stealth suites. Lower severity, file last or fold into a PR.

Every artifact must keep the line saying it was produced by an AI agent and reviewed by a human. The eval library's contributor guide requires human review of agent-written code before submission, so the owner reviews each issue and PR before it goes out.

## Step 4. What the wider network access of a computer-use session unlocks

Roughly in order of value.

- **Read the two upstream issues the sandbox could not reach.** This decides whether the Petri and MakeMeSay findings are novel or duplicates, which changes both the count above and the filing plan.
- **Verify the paper-fidelity findings against the papers themselves.** Several rest on reference code standing in for a paper that was unreachable. The StrongREJECT, MASK, WMDP, CoCoNot and InstrumentalEval findings all have a "could not read the paper" caveat.
- **Run the dataset-dependent checks.** With Hugging Face reachable, the MASK, AgentHarm and CoCoNot loaders run, which tests sample counts, label quality and duplicate detection that are currently unverified.
- **Try to measure a magnitude, not just a mechanism.** Even a hundred samples through one open eval with a real grader would turn "a malformed verdict inverts the score" into a rate. This is the single biggest gap in the whole sprint. It needs model access, which the owner has said is not available as an API key, so consider whether a small number of manual runs can substitute.
- **Docker, if the session has a daemon.** That unlocks the container-based scorers: the Cybench and DeepMind CTF sandbox claims, the METR task families, and most ControlArena settings, all of which are currently static analysis only.

## Step 5. Only after the above, consider sprint 2

Do not start a second audit sprint before at least one finding has landed. If and when it has, the ranked plan in `../../research/README.md` section 5 puts the per-model dangerous-capability determinations ledger and the release-artifact ledger next, both of which need the wider network access anyway.

## Environment notes for the next session

- `env/setup-audit-env.sh` rebuilds the audit environment with every clone pinned to the commit the findings were verified against. The original environment was in an ephemeral scratchpad and is gone.
- The standard sandbox reaches only GitHub and package registries. Web search works; direct fetches of lab sites, papers and forums do not.
- There is no Docker daemon and no Hugging Face access in the standard sandbox, and no model API key at all.
- Usage limits ended the first session's fan-out abruptly and killed four agents mid-run. Prefer a small number of focused agents; `METHODS.md` records that nine focused agents produced more verified output per token than the large research fan-out earlier in the session.
