# How these audits were done

Written 2026-09-13 after sprint 1, so the process can be repeated or criticised.

## Shape of the work

Eleven targets, one agent per target, each given the same brief: the defect checklist in `README.md`, the location of the target and of a reference implementation, and instructions to write a minimal reproduction for every suspected defect and to run it. Each agent returned a report; I then verified the load-bearing claims myself by reading the cited source and rerunning the reproductions before anything was recorded. Agents ran in parallel, which is what made eleven targets feasible in one session.

## What made findings hold up

- **A reference to diff against.** The strongest findings came from comparing a port with the implementation or paper it claims to follow: a metric formula, a judge parser, a sampling parameter. Where no reference existed, the project's own documentation served, and several findings are code contradicting its own docstring.
- **Reproductions that assert observed behaviour.** Writing the test so it passes against the current code means it doubles as a tripwire: it fails when the defect is fixed. Where the reference behaviour was asserted instead, a failing test is the finding.
- **Mocked model outputs.** Almost every judge and grader defect was reproducible with a scripted completion, so no API budget was needed. What this cannot measure is frequency: we establish that a malformed grader reply inverts a verdict, not how often real graders produce one.
- **Verifying before recording.** One of my own hypotheses was disproved this way, and two agent claims needed correcting. The verification step is not a formality.

## What limited the work

No Docker daemon, so container-based scorers got static analysis only. No Hugging Face access, so dataset ground truth was unchecked. No model API, so no end-to-end run and no frequency estimates. Papers and most non-code sites were unreachable, so paper fidelity was judged against reference code where possible. Agents hit a usage limit partway through, which killed four mid-run and required relaunching them on a different model.

## Disclosure

Anything an evaluated model could use to score without doing the task, and anything that points at an answer key, goes to the maintainers privately first and is summarised publicly without specifics. Everything else becomes a public issue with a reproduction. Every artifact says it was produced by an AI agent and reviewed by a human, which the eval library's contributor guide requires in any case.

## What I would do differently

Start from the reference implementation rather than the port, because the diff drives the findings. Ask each agent for a coverage list, not only findings, since "checked and found fine" is what makes the report auditable. And schedule around the usage limit: nine focused agents produced more verified output than the large research fan-out earlier in the session.
