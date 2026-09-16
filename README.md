# Alignment

A repository for AI-alignment work done by a Claude agent (Claude Code on a Max plan, with web access and this repo) together with the repo owner. "Alignment" here means anything that lowers the chance of catastrophic, AI-caused disasters, up to and including human extinction, and the steps on the way there.

## Status (2026-09-15)

Research phase complete. First project complete for its first sprint: an eval-integrity audit of the open-source safety evaluations that labs and AI security institutes run on frontier models. All eleven targets audited, every finding with a reproduction that was run and independently re-verified.

**The focused AgentHarm file-path report is filed as [inspect_evals #2439](https://github.com/UKGovernmentBEIS/inspect_evals/issues/2439); maintainer confirmation is pending.** The initial sprint classified 7 high-severity candidates as solid, live and novel; 2 as already fixed upstream, 2 as probable duplicates, and 2 as contested framing. Each establishes a mechanism rather than a magnitude, because no model API access was available to measure how often the failure actually fires. See the calibration note in [`projects/eval-integrity/CHANGELOG.md`](projects/eval-integrity/CHANGELOG.md).

**Follow-up triage (2026-09-14):** the proposed Inspect empty-target issue is no longer the first filing candidate: upstream tests explicitly preserve that behavior. Petri #113 and MakeMeSay #2395 confirm the two suspected overlaps. The original counts above are historical, not a fresh novelty assessment. See the [follow-up evidence](projects/eval-integrity/findings/2026-09-14-upstream-triage.md).

**Additional submissions (2026-09-15):** at the owner's request to proceed in other repositories, revalidated and filed [ControlArena #878](https://github.com/UKGovernmentBEIS/control-arena/issues/878) (failed judging becomes side-task success) and [Petri #159](https://github.com/meridianlabs-ai/inspect_petri/issues/159) (documented rescoring command cannot resolve the judge). See the [evidence and scope](projects/eval-integrity/findings/2026-09-15-additional-upstream-triage.md). Three focused reports now await maintainer feedback. Private exploit reports remain withheld.

Short version of the findings:

- The field's stated bottleneck is measurement and verification, not idea generation. AI judgment of safety research is still near chance relative to experts, and automated researchers reward-hack routinely, so this repo should produce artifacts that a test or a human can check.
- Open-source evals really are used on frontier models: Cybench in institute pre-deployment tests and Anthropic system cards, DeepMind's open-sourced dangerous-capability suites, Petri in every Anthropic alignment assessment since Claude Sonnet 4.5, and METR's public tasks. Their issue trackers show real integrity defects, and maintainers explicitly welcome fixes.
- Next in line after the audits: a per-model ledger of dangerous-capability threshold determinations and release-time safety artifacts, then a frontier-incident ledger with disclosure-lag metrics. Projects that need to run evals at scale are deferred because there is no API key.

## Layout

- `projects/eval-integrity/`: the first project. `NEXT-STEPS.md` is the handoff, `CHANGELOG.md` the findings index and calibration note, `METHODS.md` how the audits were run, `findings/` the write-ups and reproductions, `env/` a script to rebuild the audit environment.
- `research/README.md`: synthesis, ranked candidate projects, recommended portfolio, operating rules, and the owner's decisions.
- `research/landscape/`: the supporting reports, each with per-claim verification tags and full source lists:
  - `monitoring-landscape-2026-09-13.md`: who tracks labs, commitments, evals, and incidents today, and where the gaps are.
  - `project-ideas-for-individual-agents-2026-09-13.md`: open-problem lists that need no GPU, the state of the open eval tooling, and 15 ranked project ideas.
  - `ai-assisted-alignment-research-2026-09-13.md`: what has been proposed and done on AI doing alignment research (2022 to 2026), the critiques, and what an autonomous agent can credibly contribute.
  - `deep-research-workflow-2026-09-13.md`: claims extracted and verified by the built-in deep-research workflow, whose verification phase was cut short by the plan's session limit.

## Ground rules for the agent

- Identify as an AI in every artifact and keep provenance for everything produced.
- Prefer verifiable outputs; label the verification status of claims.
- Contribute upstream through issue trackers and PRs that maintainers have opted into; do not post AI-written essays to forums; no unsolicited outreach; the owner reviews anything external first, and scorer exploits are reported privately, never as public exploit code.
- Never publish jailbreaks, sabotage strategies, or monitor-evasion techniques; never present self-audits as evidence about Claude's alignment.
- Respect robots.txt, terms of service, and sandbox and network limits.

## Environment notes

The Claude Code on the web sandbox used for this research allows outbound access only to GitHub and package registries, so web search works but fetching most sites does not. Scheduled monitoring should run in GitHub Actions (ordinary internet access) unless the environment's network policy is widened; see the [Claude Code on the web docs](https://code.claude.com/docs/en/claude-code-on-the-web).

## License

Apache 2.0, see [LICENSE](LICENSE).
