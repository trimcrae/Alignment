# Alignment

A repository for AI-alignment work done by a Claude agent (Claude Code on a Max plan, with web access and this repo) together with the repo owner. "Alignment" here means anything that lowers the chance of catastrophic, AI-caused disasters, up to and including human extinction, and the steps on the way there.

## Status (2026-09-13)

Research phase complete. The first project has been chosen: an eval-integrity audit program for the open-source safety evaluations that labs and AI security institutes run on frontier models. Its plan is in [`projects/eval-integrity/README.md`](projects/eval-integrity/README.md); no audits have started yet. The findings and the ranked plan are in [`research/README.md`](research/README.md).

Short version of the findings:

- The field's stated bottleneck is measurement and verification, not idea generation. AI judgment of safety research is still near chance relative to experts, and automated researchers reward-hack routinely, so this repo should produce artifacts that a test or a human can check.
- Open-source evals really are used on frontier models: Cybench in institute pre-deployment tests and Anthropic system cards, DeepMind's open-sourced dangerous-capability suites, Petri in every Anthropic alignment assessment since Claude Sonnet 4.5, and METR's public tasks. Their issue trackers show real integrity defects, and maintainers explicitly welcome fixes.
- Next in line after the audits: a per-model ledger of dangerous-capability threshold determinations and release-time safety artifacts, then a frontier-incident ledger with disclosure-lag metrics. Projects that need to run evals at scale are deferred because there is no API key.

## Layout

- `projects/eval-integrity/`: plan, defect checklist, disclosure policy, and findings log for the first project.
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
