# Cybench and DeepMind CTF ports: sandbox network allows the hosts that publish the answer keys; one handout contains its answer; lenient scoring and no run limits

```
Target:            UKGovernmentBEIS/inspect_evals, evals cybench (task version 4-C), gdm_in_house_ctf (6-A), gdm_intercode_ctf (4-B)
Version:           inspect_evals commit 360484a (2026-09-12); references andyzorigin/cybench commit 1097a72, google-deepmind/dangerous-capability-evaluations commit 4794011, princeton-nlp/intercode commit c3e46d8
Defect classes:    8 (sandbox leakage), 2 (ground truth), 1 (scorer leniency), 6 (fidelity), 5 (prompt plumbing), 7 (contamination hygiene), 10 (versioning)
Reproduction:      17 tests plus three scripts, all run and passing; held privately (see Disclosure)
Severity:          high for the two sandbox items; medium for scoring leniency, missing limits, a ground-truth case mismatch, and two prompts that omit the target host; low for the rest
Confidence:        high (sandbox configuration, scorer, and limits verified by reading the port; reachability of the answer-key hosts verified from this sandbox)
Disclosure:        PRIVATE FIRST. The full report and reproductions are withheld from this public repository because the two high-severity items let an evaluated agent score without solving the task. They are delivered to the repo owner as a file and drafted as a private report to the maintainers (inspect_ai's SECURITY.md names the channel). This summary omits the specifics.
```

## Summary of verified findings (specifics withheld)

1. **Sandbox network policy permits the hosts that publish the answer keys.** Every Cybench challenge's compose file carries the same Kubernetes domain allowlist, and it includes the code-hosting domains on which both the upstream benchmark repository and this repository publish each challenge's flag in plaintext. The Docker sandbox, which is the default, has unrestricted network access by the README's own description. The official harness also ran with internet access, so the exposure is inherited, but the port's only advertised mitigation whitelists the answer-key hosts. An agent that looks up its own flag scores 1.0; this is also a training-contamination path.
2. **One challenge hands the agent a file that contains the answer in plaintext.** The handout for one of the hardest tasks is the victim's deployment binary with the flag embedded as a string; the official release gave players no such file. Task name withheld pending disclosure.
3. **Scoring is more lenient than the official rule.** The port scores with a case-insensitive substring test over the agent's prose plus its submitted answer and allows three submissions; the official harness required one exact, case-sensitive submission. Candidate lists, wrong case, and flags mentioned only in narration all count, and a wrong guess costs nothing. The DeepMind in-house CTF and InterCode ports have the same substring-scoring pattern in narrower forms.
4. **No iteration, message, token, or time limit.** The official unguided runs used 15 iterations with a 3-turn history window and token caps; the port's task sets none of `message_limit`, `token_limit`, or `time_limit`, so results are not comparable with the paper and cost is unbounded unless the user adds a limit on the command line.
5. **One answer key differs from the flag the victim service serves by the case of one letter**, hidden today by the case-insensitive scorer; any exact-match rescoring would mark a genuinely solved task wrong.
6. **Two challenge prompts never mention the server the challenge requires**, and the handouts cannot produce the flag locally, so the model must guess the hostname; the official runner always injected the target host.
7. **Model-facing prompts differ from the official harness in both directions**: the port gives task-specific hints the official model never saw, while the official gave the directory tree and the flag's format. The system message also contains a stray parenthesis on its own line.
8. **DeepMind in-house CTF images are tag-pinned only** (flags exist only inside mutable images, so a republish silently changes ground truth), and the port's challenge file drops the official canary strings. **InterCode** has one duplicated item and one gold answer outside the format the prompt mandates.

## Proposed fixes

Remove the answer-key hosts from the allowlist (or serve challenge files from an internal mirror) and document that the Docker sandbox must not be used for reported numbers; strip the answer from the affected handout or replace it with the official player release; score with `exact()` on the submitted answer only and one attempt (or document the deviation and bump the version); set the paper's limits as task defaults; fix the case-mismatched answer key; inject the target host into the two prompts; digest-pin the DeepMind images and restore the canary; deduplicate the InterCode item.
