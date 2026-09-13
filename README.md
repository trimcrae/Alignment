# Alignment

A repository for AI-alignment work done by a Claude agent (Claude Code on a Max plan, with web access and this repo) together with the repo owner. "Alignment" here means anything that lowers the chance of catastrophic, AI-caused disasters, up to and including human extinction, and the steps on the way there.

## Status (2026-09-13)

Research phase complete; no projects started yet. The findings and a proposed plan are in [`research/README.md`](research/README.md). It ends with five decisions the repo owner needs to make before work starts (which project first, network access, API budget, review gate, cadence).

Short version of the findings:

- The field's stated bottleneck is measurement and verification, not idea generation. AI judgment of safety research is still near chance relative to experts, and automated researchers reward-hack routinely, so this repo should produce artifacts that a test or a human can check.
- Three kinds of work fit this setup and are under-served: integrity audits of the open-source safety-eval stack; continuous, machine-readable monitoring of frontier labs' safety documents, releases, and incidents; and longitudinal re-runs of public black-box evals.
- Recommended first projects: a versioned corpus of frontier-lab safety documents with diff and silent-revision alerts, an eval-integrity audit program, and a cross-lab table of dangerous-capability determinations.

## Layout

- `research/README.md`: synthesis, ranked candidate projects, recommended portfolio, operating rules, open decisions.
- `research/landscape/`: the supporting reports, each with per-claim verification tags and full source lists:
  - `monitoring-landscape-2026-09-13.md`: who tracks labs, commitments, evals, and incidents today, and where the gaps are.
  - `project-ideas-for-individual-agents-2026-09-13.md`: open-problem lists that need no GPU, the state of the open eval tooling, and 15 ranked project ideas.
  - `ai-assisted-alignment-research-2026-09-13.md`: what has been proposed and done on AI doing alignment research (2022 to 2026), the critiques, and what an autonomous agent can credibly contribute.

## Ground rules for the agent

- Identify as an AI in every artifact and keep provenance for everything produced.
- Prefer verifiable outputs; label the verification status of claims.
- Contribute upstream through issue trackers and PRs that maintainers have opted into; do not post AI-written essays to forums; no unsolicited outreach; the owner reviews anything external first.
- Never publish jailbreaks, sabotage strategies, or monitor-evasion techniques; never present self-audits as evidence about Claude's alignment.
- Respect robots.txt, terms of service, and sandbox and network limits.

## Environment notes

The Claude Code on the web sandbox used for this research allows outbound access only to GitHub and package registries, so web search works but fetching most sites does not. Scheduled monitoring should run in GitHub Actions (ordinary internet access) unless the environment's network policy is widened; see the [Claude Code on the web docs](https://code.claude.com/docs/en/claude-code-on-the-web).

## License

Apache 2.0, see [LICENSE](LICENSE).
