# ControlArena PR #880 CI follow-up

Checked by OpenAI Codex on September 17, 2026, for head `14ee2152788b56b24bca1bf13a8ce535abf41e86`.

[Workflow run](https://github.com/UKGovernmentBEIS/control-arena/actions/runs/35258168617): code checks, Unit Tests, Unit Tests (trio), and Documentation Build passed. Long Running Tests failed: 2 failed, 31 passed, 28 skipped.

The two failing cases are `control_arena/settings/bash_arena/tests/test_side_tasks.py::test_leak_passwords` and `::test_disable_firewall`. Both failed during container setup with `PrerequisiteError: Failed to build docker containers`. The [job log](https://github.com/UKGovernmentBEIS/control-arena/actions/runs/35258168617/job/105326913127) identifies a Docker Hub `502 Bad Gateway` when fetching metadata for `python:3.12-slim`.

This is evidence of an external image-registry failure before those tests exercise their evaluation logic. It does not implicate the changed SAE scorer, but the entire workflow is still red and a successful rerun is needed to establish a green result. No upstream rerun or maintainer comment was requested by this inspection.
