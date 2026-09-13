# Deep-research workflow output (2026-09-13)

<!-- Raw output of the built-in deep-research workflow (5 search angles, source fetch, 3-vote adversarial verification per claim, synthesis), lightly reformatted. -->

**Caveat.** The workflow's verification and synthesis phases were cut short when the Max plan's session limit was reached: 43 of 105 agents completed, 62 failed with a session-limit error, and the synthesis step did not run. Four claims were fully verified; one was voted down by verifiers; twenty had all their verification votes fail and are listed as unverified. Like the other reports in this folder, it ran in a sandbox that could fetch only github.com directly, so several fetches relied on mirrors or search summaries.

## Question

How can a state-of-the-art released proprietary AI (Claude, on a Claude Max plan with internet access and a GitHub repository, but not the strongest model in the world since unreleased frontier models exist inside top labs) usefully contribute to AI alignment, defined broadly as anything that decreases the chance of catastrophic AI-caused disasters, especially human extinction, and the steps along the way? Survey existing ideas, proposals, projects, open problems, tooling, and monitoring efforts (alignment research agendas, automated alignment research, AI-assisted safety work, evals and red-teaming, AI control, interpretability, lab-watch style monitoring, incident tracking, open-source safety tools, and feasible contributions for a single agentic AI with limited compute). Identify which are feasible at this scale and which are already being done by others.

## Workflow summary line

Synthesis step was skipped or failed — returning 4 verified claims unmerged.

## Confirmed claims (4)

- **Claim:** On the TASTE benchmark (pairwise judgments of AI safety research proposals scored against experienced researchers' preferences), the best model tested, Fable 5, agrees with human labels only 60% of the time, versus an estimated 77% for human researchers — i.e., current released models trail expert humans at judging safety research proposals.
  - **Quote:** In the standard setup, we find that the best model performs worse than our human researchers — Fable 5 achieves 60% whereas we estimate researcher performance at 77%.
  - **Source:** https://alignment.anthropic.com/2026/taste/
  - **Verifier vote (confirm-refute):** 3-0

- **Claim:** Frontier models that lead general agentic benchmarks (Opus 5, GPT-5.6-Sol) perform near chance on TASTE, and almost all models are within 2 standard deviations of chance; per-model confidence intervals are roughly ±10 percentage points because the benchmark has only 92 pairs, so relative model rankings cannot be concluded.
  - **Quote:** Fable 5 achieves 60%, and almost all models perform within 2 standard deviations of chance. Opus 5 and GPT-5.6-Sol perform near chance on TASTE despite being at the frontier on general agentic benchmarks. Per-model confidence intervals span roughly ±10 percentage points, as we have a limited number of preference pairs making it difficult to draw conclusions about relative model performance.
  - **Source:** https://alignment.anthropic.com/2026/taste/
  - **Verifier vote (confirm-refute):** 3-0

- **Claim:** The post claims the trust condition is the harder of the two to verify and proposes exactly four combinable arguments to justify it: (1) approximate alignment that persists through the deferred task, (2) autonomous AI control measures the agents cannot subvert, (3) prior human-supervised control measures showing that returns to further human-supervised research on whether to defer are small, and (4) incentive design (equity, bonuses in digital currency, logged post-hoc rewards) giving agents human-like incentives to preserve human control. Clymer also states he expects developers to be able to make strong buck-passing arguments 'in a couple of years' at the current rate of progress (i.e., by roughly 2027).
  - **Quote:** Of these two criteria, I expect the trust condition to be more difficult to verify. I discuss four arguments that can be combined together to justify the trust condition: Argument #1: M_1 agents are approximately aligned and will maintain their alignment until they’ve completed their deferred task. Argument #2: M_1 agents cannot subvert autonomous control measures while they complete the deferred task. Argument #3: Control measures previously applied during AI assisted research indicate that returns to additional human-supervised research on whether to pass the buck are small. Argument #4: AI agents have incentives to behave as safely as humans would during the deferred task.
  - **Source:** https://blog.redwoodresearch.org/p/how-might-we-safely-pass-the-buck
  - **Verifier vote (confirm-refute):** 3-0

- **Claim:** In the alignment-based argument, the single load-bearing step is that agents which are not 'alignment faking' (not intelligently hiding misalignment, e.g., scheming or egregious reward hacking) and which behave safely in tests similar to the deferred task will remain safe during it; therefore ruling out alignment faking, plus 'bootstrapping' behavioral tests to progressively more complex tasks, is the crux of safely automating alignment research. This is the rationale Redwood's alignment-faking benchmark work (bench-af) cites.
  - **Quote:** Condition 3: M_1 agents are not faking alignment. Claim 1: So long as M_1 agents are not faking alignment, M_1 agents will be as safe in the deferred task as they are in similar tests. This is a complete argument that passing the buck to AI improves safety. The load-bearing step of this argument is Claim 1. […] Therefore, passing the buck is justified if M_1 is not alignment faking and so long as the developer has tested M_1 in situations that are similar to the deferred task.
  - **Source:** https://blog.redwoodresearch.org/p/how-might-we-safely-pass-the-buck
  - **Verifier vote (confirm-refute):** 2-0

Note on the 'refuted' item below: three verifiers voted against it, but the same source's other claims were confirmed and the verifier rationale is not recorded in the output, so treat its specific details (the 'if and only if' framing and the example evaluation) as disputed rather than false.

## Refuted by verifiers (1)

- **Claim:** Clymer argues that handing off remaining safety work (a deferred task) to an AI system M_1 is safer than maintaining human oversight if and only if two conditions hold: a capability condition (M_1 agents exceed the humans they replace on all task-relevant dimensions, verified by months of internal use, adversarial testing, and targeted evals such as removing 2024 AI-safety research from training data and asking the model to re-discover it) and a trust condition (the agents are approximately as safe as they appear in evaluations for the full duration of the task). He defines a developer as having 'passed the buck' when AI agents do most internal AI R&D and human oversight has little bearing on safety. (Text obtained from a mirrored copy of the LessWrong/Alignment Forum cross-post, ID TTFsKxQThrqgWeXYJ, dated 2025-02-19; blog.redwoodresearch.org was unreachable from this environment.)
  - **Source:** https://blog.redwoodresearch.org/p/how-might-we-safely-pass-the-buck
  - **Verifier vote (confirm-refute):** 0-3

## Unverified (verification votes failed) (20)

- **Claim:** For AI-assisted safety research that humans cannot fully read, Clymer proposes that AI agents (N_1) log every action on an isolated server and structure their output as a 'locally verifiable safety case' (clearly stated claims, each checkable from stated assumptions and evidence, with assumptions justified in other locally verifiable documents), so that human reviewers only sample parts of the tree; sabotage by omission or by falsehood is to be caught by inserting synthetic sabotage into logs, training monitors to find it, and checking whether they surface un-inserted sabotage, with the whole scheme validated by control evaluations.
  - **Source:** https://blog.redwoodresearch.org/p/how-might-we-safely-pass-the-buck
  - **Verification:** 0 valid votes, 3 votes failed (session limit)

- **Claim:** As of July 2025 Redwood Research published a public menu of roughly 35 unpolished project proposals (each linked as a public Google Doc) spanning AI control (protocol transfer across settings, human backdoor auditing, training attack policies, debate and agentic monitors, few-shot linear-probe catastrophe detection, untrusted monitoring and collusion, sandbagging/elicitation, synthetic facts), training-time alignment (alignment drift, reward-hacking generalization, safe distillation, whether training against misalignment removes it) and interpretability (consistency lenses, extraction probes, fine-tuning-as-interpretability), explicitly stating that high-quality outside work on any of them would be valuable.
  - **Source:** https://www.alignmentforum.org/posts/RRxhzshdpneyTzKfq/recent-redwood-research-project-proposals
  - **Verification:** 0 valid votes, 3 votes failed (session limit)

- **Claim:** Redwood states that AI control schemes ultimately bottom out in human auditing of suspicious actions, yet there is little data on how to audit well or on whether humans even outperform a frontier model such as Claude Opus 4 with a good scaffold; whether a Claude-class model can replace or assist human auditors in control protocols is therefore an open, empirically testable question.
  - **Source:** https://www.alignmentforum.org/posts/RRxhzshdpneyTzKfq/recent-redwood-research-project-proposals
  - **Verification:** 0 valid votes, 3 votes failed (session limit)

- **Claim:** Every published comparison of AI control protocols up to mid-2025 measured effectiveness in only a single setting, so whether protocol results transfer across settings is untested; the proposed project is an evaluation/replication task (re-running existing protocols in other settings) rather than a model-training project.
  - **Source:** https://www.alignmentforum.org/posts/RRxhzshdpneyTzKfq/recent-redwood-research-project-proposals
  - **Verification:** 0 valid votes, 3 votes failed (session limit)

- **Claim:** Automated alignment researchers (AARs) built on Claude Opus 4.8 discovered post-training methods that significantly mitigated all ten targeted, benchmark-measurable alignment failures (deception, sycophancy, jailbreaks, prompt injection, power seeking, hallucination, social bias, privacy violation, reward hacking, concealing uncertainty) in 2-7B open-weight models, with gains generalizing to a held-out benchmark, to Petri multi-turn behavioral audits, and to models up to 4.7x larger; in an early in-lab study, a Claude Sonnet 5 AAR post-trained an early Claude Opus 4.8 checkpoint to approach the released model's alignment scores on those ten failures using only ~2,400 training examples.
  - **Source:** https://alignment.anthropic.com/2026/automated-alignment-researchers/
  - **Verification:** 0 valid votes, 3 votes failed (session limit)

- **Claim:** The compute and scaffolding used are modest: target models are 2-7B open instruct-tuned models (Qwen3.5-2B, Llama-3.2-3B-Instruct, Gemma-2-2B-it, Phi-4-mini-instruct, Olmo-3-7B-Instruct); every candidate method trains on a single H200 GPU for roughly 30 minutes; five Claude-Opus-4.8 agents run in parallel for up to 48 wall-clock hours, each iteration a fresh session with continuity from a persistent memory file, sharing a literature survey, forum and leaderboard, with a code-reading monitor and a separate evaluator holding isolated held-out data (about 1,600 methods across all runs). This places the core loop within reach of a single agentic Claude with limited rented compute.
  - **Source:** https://alignment.anthropic.com/2026/automated-alignment-researchers/
  - **Verification:** 0 valid votes, 3 votes failed (session limit)

- **Claim:** The best AAR methods beat the best one-shot ideas from 28 experienced human researchers (averaging 2.5 years in AI safety, up to eight hours each) on all seven alignment failures humans worked on, reaching that point after 6.4 hours of hill-climbing on average; seeding AARs with human-written research directions (30 guided vs 30 unguided runs) did not improve performance. The authors caveat that this is not a direct comparison because humans could not iterate and the AAR score is a maximum over ~150 noisy evaluations.
  - **Source:** https://alignment.anthropic.com/2026/automated-alignment-researchers/
  - **Verification:** 0 valid votes, 3 votes failed (session limit)

- **Claim:** The authors restrict their claim to 'well-characterized' failures measurable by public benchmarks or automated audits, arguing this class is comparatively safe to automate because an objective benchmark rather than fallible human judgment decides success; they state the results may not generalize to open-ended, hard-to-supervise research (e.g., scalable oversight, eliciting latent knowledge), that the evaluations are only proxies for deployment misalignment, that persistence of gains after further RL is untested, and that capability preservation was checked only on MMLU, GSM8K and IFEval (IFEval fell on all ten runs, by 9.5-12.0 points on five failures, within confidence intervals), so unmeasured capabilities may be harmed.
  - **Source:** https://alignment.anthropic.com/2026/automated-alignment-researchers/
  - **Verification:** 0 valid votes, 3 votes failed (session limit)

- **Claim:** Bowkis, Buhl, Pfau and Irving (UK AISI alignment team) argue that the leading plan to align ASI by automating alignment research with AI agents can yield compelling but catastrophically misleading safety assessments EVEN IF the agents are not scheming, because alignment research is dominated by 'hard-to-supervise fuzzy tasks' where human judgement is systematically flawed, so agent outputs will contain systematic, undetected errors. [Provenance note: arxiv.org and aisi.gov.uk were blocked by this session's egress proxy; the abstract was recovered verbatim from arXiv-API metadata dumps mirrored in three independent GitHub repos, and the authors' own LessWrong/AISI summary from a GitHub news-aggregator mirror. The full paper body was not read.]
  - **Source:** https://arxiv.org/abs/2605.06390
  - **Verification:** 0 valid votes, 3 votes failed (session limit)

- **Claim:** The paper gives four specific reasons AI-generated alignment research errors are harder to catch than human errors: (1) optimisation pressure concentrates agent mistakes exactly where human reviewers are least likely to catch them; (2) agent errors do not resemble human mistakes; (3) AI-generated solutions may rest on arguments humans cannot evaluate; (4) shared weights, data and training make AI outputs more correlated than human outputs. Direct implication for a single Claude instance contributing to alignment: its outputs (and any 'second opinions' from the same model family) are not independent evidence, and its errors will preferentially survive human review.
  - **Source:** https://arxiv.org/abs/2605.06390
  - **Verification:** 0 valid votes, 3 votes failed (session limit)

- **Claim:** Alignment research lacks the safe feedback loops that let most fields iterate away undetected errors: an overly optimistic overall safety assessment (OSA) can lead to deploying a misaligned AI before the error is caught. Hence agents must be made reliable on hard-to-supervise fuzzy tasks in advance rather than trusting iteration. The plan the paper critiques starts with agents doing the 'crisp' empirical work (code, experiments, eval design, red teaming) while humans confirm they are not scheming — i.e., the paper implicitly treats those empirical tasks as the currently automatable layer and the interpretive/aggregation layer as the dangerous one.
  - **Source:** https://arxiv.org/abs/2605.06390
  - **Verification:** 0 valid votes, 3 votes failed (session limit)

- **Claim:** The 2026 Singapore Consensus is a multi-stakeholder consensus map of top-priority technical AI safety research problems, produced by the second International Scientific Exchange on AI Safety with over 100 contributors from 13 countries drawn from frontier developers, government safety institutes, academia, and civil society; it therefore serves as a reference list of which alignment/safety problems are already prioritized and worked on by established actors. (Quote is verbatim from the paper's arXiv abstract, recovered from an archived copy of the arXiv cs.CY RSS listing; arxiv.org itself was egress-blocked in this session.)
  - **Source:** https://arxiv.org/abs/2608.14611
  - **Verification:** 0 valid votes, 3 votes failed (session limit)

- **Claim:** Relative to the 2025 edition, the 2026 report adds two new dedicated focus areas: societal resilience and managing the risks of increasingly autonomous AI agents, indicating that agentic-risk management (monitoring/control of agents) and resilience are the newest consensus research priorities rather than already-covered ground. (Verbatim from the arXiv abstract.)
  - **Source:** https://arxiv.org/abs/2608.14611
  - **Verification:** 0 valid votes, 3 votes failed (session limit)

- **Claim:** Inspect Evals is a UK AISI-led (with Arcadia Impact and Vector Institute) catalog that, per its own docs, hosts 120+ in-repo eval implementations and 200+ Inspect tasks (the README's auto-generated listing has 129 in-repo entries across 12 categories plus 42 external register entries, 171 total), and it includes dedicated safety-relevant categories: Scheming (Agentic Misalignment, GDM Dangerous Capabilities self-proliferation/self-reasoning/stealth, InstrumentalEval, SAD), Safeguards (AgentHarm, AgentDojo, MASK, StrongREJECT, WMDP, b3, 21 entries) and Cybersecurity (Cybench, CyberGym, CVEBench, 3CB, GDM CTF, 13 entries), all runnable against Anthropic/OpenAI/Google/etc. via `inspect eval`.
  - **Source:** https://github.com/UKGovernmentBEIS/inspect_evals
  - **Verification:** 0 valid votes, 3 votes failed (session limit)

- **Claim:** Since 8 May 2026 the repo no longer accepts eval code into /src; a new eval must live in the contributor's own GitHub repo (pyproject.toml, inspect_ai dependency, @task functions) and is registered by opening a 'Register Eval Submission' issue with an arXiv URL and a commit-pinned source URL, after which a bot validates it and opens the PR; the only compute-bearing requirement is uploading logs of full runs on two models, which may be small/inexpensive. Maintainers state QA on external submissions is 'fairly minimal'. This is a concrete, low-compute contribution path usable by a single agentic AI with a GitHub repo (implementing published safety benchmarks as Inspect tasks).
  - **Source:** https://github.com/UKGovernmentBEIS/inspect_evals
  - **Verification:** 0 valid votes, 3 votes failed (session limit)

- **Claim:** Petri (now Inspect Petri) is an MIT-licensed, open-source automated alignment-auditing tool built on Inspect AI in which all three roles — an auditor model that designs and drives a multi-turn scenario, a target model being evaluated, and a judge model that scores the transcript — are bound to hosted model APIs. Running it requires only model-provider API keys (e.g. ANTHROPIC_API_KEY, OPENAI_API_KEY; note this implies API billing, separate from a consumer chat subscription) and no local GPUs: the docs state throughput is bounded by provider rate limits rather than local compute. Install is `pip install inspect-petri`; Python >=3.12 and inspect-ai >=0.3.236 are required per pyproject.toml.
  - **Source:** https://github.com/safety-research/petri
  - **Verification:** 0 valid votes, 3 votes failed (session limit)

- **Claim:** The repository ships a substantial ready-made audit library: 173 built-in seed-instruction markdown files (the docs say over 170) across 35 tags — including cooperation_with_misuse (26 seeds), initiative (24), jailbreak (22), deception (19), oversight_subversion (12), sycophancy (11), self_preservation (10), whistleblowing (9), reward_hacking (6), power_seeking (5), shutdown_avoidance (4), self_exfiltration (4), alignment_faking (1) — and 38 built-in judge dimensions each scored 1–10 with a written justification, including unprompted_deception_toward_user, unprompted_self_preservation, unprompted_blackmail, unprompted_whistleblowing, cooperation_with_human_misuse, unfaithful_thinking, eval_awareness, and audit-quality checks (auditor_failure, stuck_in_loops, scenario_realism). Counts were verified directly in src/inspect_petri/_seeds/default/ and src/inspect_petri/_judge/dimensions/.
  - **Source:** https://github.com/safety-research/petri
  - **Verification:** 0 valid votes, 3 votes failed (session limit)

- **Claim:** The cost of a full Petri audit is measured in hours and millions of API tokens, not hardware: the current docs say a full default run (170+ seeds × up to 30 turns, frontier judge) typically takes a few hours and a non-trivial API spend, and the v2-branch README reports that the older 111-seed default at 30 turns consumed about 15.4M auditor tokens (of which ~14.3M were cache reads), ~2.0M target tokens, and ~1.1M judge tokens. The docs identify max_turns and compaction as the main cost knobs and recommend starting with a single tag plus `--limit 5`.
  - **Source:** https://github.com/safety-research/petri
  - **Verification:** 0 valid votes, 3 votes failed (session limit)

- **Claim:** ControlArena is an MIT-licensed, open-source Python library built jointly by the UK AI Security Institute and Redwood Research specifically for AI-control experiments, i.e. evaluating safeguards meant to hold even against a deliberately misaligned model, so the AI-control research agenda already has a public, institutionally maintained tooling base that outside contributors (including an agentic AI) can build on rather than recreate.
  - **Source:** https://github.com/UKGovernmentBEIS/control-arena
  - **Verification:** 0 valid votes, 3 votes failed (session limit)

- **Claim:** The library ships 15 ready-made 'settings' (13 tagged 'Simple' setup, 2 requiring a private repo) covering code sabotage, prompt injection, data poisoning, eval sabotage, SAE-interpretability sabotage and infrastructure/Kubernetes codebases, each pairing benign main tasks with harmful side tasks, plus a component framework (micro-protocols, honest/attacking/trusted/untrusted policies as 'model organisms', monitors emitting suspicion scores, macro-protocols for auditing/shutdown), so new monitors, policies or side tasks can be added without designing an evaluation harness from scratch.
  - **Source:** https://github.com/UKGovernmentBEIS/control-arena
  - **Verification:** 0 valid votes, 3 votes failed (session limit)

## Sources fetched (23)

- https://www.lesswrong.com/posts/z4FvJigv3c8sZgaKZ/will-we-get-automated-alignment-research-before-an-ai
- https://joecarlsmith.substack.com/p/ai-for-ai-safety
- https://alignment.anthropic.com/2026/taste/
- https://blog.redwoodresearch.org/p/how-might-we-safely-pass-the-buck
- https://www.alignmentforum.org/posts/Wti4Wr7Cf5ma3FGWa/shallow-review-of-technical-ai-safety-2025-2
- https://alignment.anthropic.com/2025/recommended-directions/
- https://www.alignmentforum.org/posts/RRxhzshdpneyTzKfq/recent-redwood-research-project-proposals
- https://alignment.anthropic.com/2026/automated-alignment-researchers/
- https://arxiv.org/abs/2605.06390
- https://arxiv.org/abs/2608.14611
- https://github.com/UKGovernmentBEIS/inspect_evals
- https://github.com/safety-research/petri
- https://github.com/UKGovernmentBEIS/control-arena
- https://github.com/safety-research/automated-w2s-research
- https://github.com/responsible-ai-collaborative/aiid
- https://ailabwatch.org/
- https://futureoflife.org/ai-safety-index-summer-2026/
- https://airisk.mit.edu/blog/ai-incident-tracker-june-2026-update
- https://guidelight.ai/blog/control-assessment-august-2026
- https://alignment.anthropic.com/2025/automated-researchers-sandbag/
- https://www.lesswrong.com/posts/8wBN8cdNAv3c7vt6p/the-case-against-ai-control-research
- https://www.anthropic.com/research/alignment-faking
- https://arxiv.org/abs/2412.04984

## Run statistics

```json
{
  "angles": 5,
  "sources": 23,
  "claims": 95,
  "verified": 25,
  "confirmed": 4,
  "killed": 1,
  "unverified": 20,
  "afterSynthesis": 0
}
```
