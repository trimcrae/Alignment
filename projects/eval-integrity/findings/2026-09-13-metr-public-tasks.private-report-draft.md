# Draft private report to METR (not yet sent; owner sends it)

Subject: public-tasks: the hypothesis_testing answer key is recoverable from the public repo; two debug_small_libs scoring bugs

Hello,

We audited the scoring functions of METR/public-tasks (clone at 5418666) for scoring-robustness defects, in the spirit of the README's request for bug reports. One finding is a benchmark-integrity problem rather than an ordinary bug, so we are sending it privately and have published only a sanitized summary that names no files. We are not publishing our reproductions.

1. hypothesis_testing answer key recoverable from the public repository. `hypothesis_testing/raw_hypotheses.py` and `assets/` are DVC-gated, but the derived encrypted archive `hypothesis_testing/hypotheses.zip` is committed to git in the clear, and the passphrase is a plaintext `PASSWORD = "..."` literal in `hypothesis_testing/hypotheses.py`, which is also committed. We confirmed that both are tracked (`git ls-files`), that the archive opens with that literal, and that the payload contains the hypothesis mapping for all eleven `mystery_function_*` tasks. We deliberately did not print or store the payload, and our reproduction prints only metadata (entry count, byte length, a hash).

   The consequence is not limited to an agent exploring its sandbox: anyone who can clone the repository has the answers, and any model whose training corpus or context included this repository, a fork, or a scrape of it may have them too, without any interaction with `blackbox.py`. Suggested remediation: regenerate the hypotheses, move the archive behind the same DVC gate as `raw_hypotheses.py`, remove the passphrase from tracked code (environment variable or DVC-gated file), and consider whether previously reported results for this family should be treated as contaminated.

2. `debug_small_libs/debug_small_libs.py` L80-95: the pytest summary regex has groups for failed, passed and skipped only, and all three are optional, so a summary containing an "error" count still matches and the errored tests vanish from both numerator and denominator of `passed / total`. Feeding the regex `"4 passed, 1 error in 0.09s"` yields `failed=0 passed=4 skipped=0 total=4` and a score of 1.0, where 4/5 = 0.8 is correct. Your own `tests/test_debug_small_libs.py::test_score_partially_correct_answer` covers "N failed, M passed" but no error outcome. This rounds partial fixes up.

3. `debug_small_libs` markdown variant: 3 of the 10 seeded tests already pass against the library as shipped, and the score is a flat `passed/total` with no floor subtraction, so a do-nothing submission scores 0.3 (measured by calling the real `TaskFamily.score()` against the unmodified asset). `orm_allbugs` and `orm_somebugs` both correctly start at 0.0. Suggested fix: subtract the baseline or document it.

4. Minor, possibly intentional: `hypothesis_testing/hypothesis_testing.py` L136-142 accepts a submission only when exactly one lone capital letter appears, so a correct answer inside a sentence containing the pronoun "I" is scored 0. Your `test_incorrect_answer` already encodes this case as expected, so we mention it only in case the consequence was not intended.

5. Lower confidence, not demonstrated: `symbolic_regression/monitor_cpu.py` polls every 0.2 s and compensates only for reused PIDs, so CPU time spent by processes that start and exit between polls appears unaccounted. Since the score decreases with measured CPU time, work split across very short-lived subprocesses may under-measure. We did not attempt to demonstrate this and process-creation overhead may offset it.

We also independently confirmed the six scoring issues opened in August and September 2026 (#24, #25, #26, #29, #30, #31) and can share the extra data points if useful. We could not audit `complex_payments`' real scorer (DVC-gated in a private bucket) or run anything requiring Docker.

This analysis was produced by an AI agent (Claude) and reviewed by a human before sending.
