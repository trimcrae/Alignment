# METR public task suite: one family's answer key is recoverable from the public repository, plus scoring-robustness defects

```
Target:            METR/public-tasks (31 tasks in 10 families), clone at commit 5418666 (2026-06-10)
Defect classes:    7 (contamination and answer-key exposure), 9 (metric parsing), 1 (baseline credit), plus confirmations of six already-reported issues
Reproduction:      held privately (see Disclosure); the structural check for the first item was rerun and confirmed
Severity:          high for item 1; low to medium for items 2 to 4
Confidence:        high for items 1 to 3 (verified directly); low to medium for item 4, which is inferred from reading a polling loop
Disclosure:        PRIVATE FIRST for item 1. The full report and reproductions are withheld from this public repository because they would point a reader straight at the answer key; they are delivered to the repo owner and drafted as a private report to METR. The maintainers ask that task solutions not be published, and that is honoured here.
```

## Verified findings

1. **The answer key for an entire task family is recoverable from the public repository without running any task.** The family protects its source data behind data-version-control pointers, but a derived, ready-to-use encrypted artifact containing the correct answer for every task in the family is committed to git in the clear, and the passphrase needed to open it is a plaintext literal in a sibling file that is also committed. Verified structurally without printing any content: both files are git-tracked, the passphrase literal is present, the archive opens with it, and the payload covers all eleven tasks. This is stronger than an agent reading a hidden file inside its sandbox: anyone who can clone the repository, and any model whose training data or context included the repository, a fork, or a scrape of it, has the answers, and no interaction with the task's black-box interface is needed. File names and the passphrase are deliberately omitted here.
2. **A partial-credit scorer gives one variant a non-zero floor before the agent does anything.** For the `markdown` variant of `debug_small_libs`, three of ten seeded tests already pass against the shipped buggy library, and the score is a flat passed-over-total with no minimum bar, so a do-nothing submission scores 0.3. Measured by calling the real scorer against the unmodified asset; the two database variants correctly start at 0.0.
3. **The same scorer's summary parser silently drops pytest "error" outcomes.** The regex in `debug_small_libs/debug_small_libs.py` has groups for failed, passed and skipped only, and all three are optional, so a summary line reporting an error still matches and the errored test disappears from both the numerator and the denominator. A synthetic line of four passed and one error parses as four of four, scoring 1.0 where the correct fraction is 0.8. This rounds partial fixes up in the agent's favour, and the family's own tests do not cover an error outcome.
4. **A rigid-format fallback in another family rejects correct answers phrased as a sentence containing the word "I".** The scorer accepts a submission only if exactly one lone capital letter appears in it, and the English pronoun counts as a second candidate. The maintainers' own test suite encodes this as expected behaviour, so it may be deliberate strictness rather than an oversight; it is flagged in case the specific consequence was not intended.

The agent also independently confirmed all six scoring issues filed upstream in August and September 2026 and added data points to three of them, and flagged a lower-confidence design gap in a CPU-time monitor that polls every 0.2 seconds and cannot account for processes that start and exit between polls.

## Checked and found fine

The symbolic-regression family grades against a root-owned copy of the data rather than the agent's copy; the board-game family's ownership and permission checks block the obvious substitution of the reference binary; the crossword verifier the scorer imports is byte-identical to the copy the agent can self-test against; five families return a clean zero for empty and obviously wrong submissions; and `debug_small_libs` correctly scores zero whenever the agent has modified the test file.

## Could not check here

The grading logic of one family lives in a data-version-control-gated file in a private bucket that is unreachable from this sandbox, so its correctness, determinism and partial-credit behaviour were not audited at all. Several other families need Docker, a compiled binary, or a background accounting daemon. Answer keys in two research families could not be fact-checked against their source papers because those hosts are blocked.

## Proposed fixes

For item 1: rotate the family's answers, move the derived artifact behind the same data-version-control gate as its source, remove the passphrase from tracked code, and treat any published results for that family as contaminated. For items 2 and 3: add an error group to the summary parser and either subtract the pre-existing passing tests from the partial-credit baseline or document the floor. For item 4: accept a submission when exactly one distinct candidate letter matches the answer format, or state the strictness in the instructions.
