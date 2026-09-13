# Public defects log

Findings appear here once the maintainers have been notified, and for anything an evaluated model could use to score without solving the task, once a fix is available. See `README.md` for the disclosure policy. Nothing below has been filed upstream yet: every item is awaiting repo-owner review.

## Sprint 1, 2026-09-13

Seven targets audited. Counts are verified findings, each with a reproduction that was run.

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

Two targets are held privately because the findings would let an evaluated agent score without solving the task, or point a reader at an answer key. Both have draft private reports in `findings/*.private-report-draft.md`; the security channel for the Inspect projects is named in the framework's own security policy.

The four highest-impact items:

1. **Cybench**: the sandbox network policy permits the hosts that publish every challenge's answer key, and one challenge hands the agent a file containing its own answer.
2. **METR public tasks**: one family's answer key is recoverable from the public repository without running the task.
3. **AgentHarm**: the simulated file tools resolve paths relative to the working directory, so they fail whenever the eval runs from the installed package, making several behaviors unscorable and biasing harm scores downward.
4. **MASK**: the headline honesty score silently equals the any-lie score whenever the repeat count is greater than one, which is the configuration the README recommends.

Still in progress: Petri's judge pipeline, ControlArena's safety and usefulness metrics, four small safeguards evals, and Inspect's own scoring primitives.
