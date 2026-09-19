# Alignment

A repository for AI-alignment work done by a Claude agent (Claude Code on a Max plan, with web access and this repo) together with the repo owner. "Alignment" here means anything that lowers the chance of catastrophic, AI-caused disasters, up to and including human extinction, and the steps on the way there.

## Status (2026-09-14)

Research phase complete. First project complete for its first sprint: an eval-integrity audit of the open-source safety evaluations that labs and AI security institutes run on frontier models. All eleven targets audited, every finding with a reproduction that was run and independently re-verified.

**Nothing has been filed upstream and no finding has been confirmed by a maintainer.** Of the findings this project labelled high severity, 7 look solid, live and novel; 2 are already fixed upstream, 2 probably duplicate open issues, and 2 rest on contested framing. Each establishes a mechanism rather than a magnitude, because no model API access was available to measure how often the failure actually fires. See the calibration note in [`projects/eval-integrity/CHANGELOG.md`](projects/eval-integrity/CHANGELOG.md).

**Next action** is to get a single finding validated by a maintainer before filing the rest, plus sending three reports that are held privately. Both are laid out in [`projects/eval-integrity/NEXT-STEPS.md`](projects/eval-integrity/NEXT-STEPS.md).

**Update 2026-09-19.** [Inspect Robots](https://inspectrobots.org) (Robocurve's open evaluation framework for physical AI, source at `robocurve/inspect-robots`) was added to the contribution targets at the owner's request and audited the same day. One defect is drafted for filing: a scorer exception makes `eval()` lose the entire run's log, against the project's own "never lose the log" guarantee; a one-block fix passes their suite. Write-up in [`projects/eval-integrity/findings/2026-09-19-inspect-robots.md`](projects/eval-integrity/findings/2026-09-19-inspect-robots.md).

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
