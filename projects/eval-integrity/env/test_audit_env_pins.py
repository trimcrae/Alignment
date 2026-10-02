"""AI-authored by OpenAI Codex, usage-sprint-2026-10-01.

Offline method: execute the actual Bash clone helper from the setup script,
not the installation/evaluation tail. Real temporary Git repos use file-only
transport. The original committed helper is run separately as a defect witness.
No upstream checkout, uv, model, dataset or API execution occurs.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
SETUP = ROOT / "projects/eval-integrity/env/setup-audit-env.sh"
BASE = "c79d38e9e49d9c2fd133b6c4faf6412760089afe"
NATIVE_PATH = "projects/eval-integrity/env/setup-audit-env.sh"
ORIGINAL = subprocess.run(
    ["git", "-C", str(ROOT), "show", f"{BASE}:{NATIVE_PATH}"],
    check=True, text=True, capture_output=True,
).stdout
CURRENT = SETUP.read_text()
REPO = "fixture/audit"
URL = f"https://github.com/{REPO}"
REAL_GIT = shutil.which("git")
assert REAL_GIT


def helper(source: str) -> str:
    start = source.index("clone() {")
    end = source.index("\n# Audit targets", start)
    return source[start:end]


def snapshot(path: Path) -> dict[str, tuple[str, int]]:
    """Bind every file byte/mode, symlink target and directory in this tree."""
    result = {}
    for item in [path, *sorted(path.rglob("*"))]:
        key = str(item.relative_to(path)) if item != path else "."
        mode = item.lstat().st_mode
        if item.is_symlink():
            result[key] = (f"link:{os.readlink(item)}", mode)
        elif item.is_file():
            result[key] = (hashlib.sha256(item.read_bytes()).hexdigest(), mode)
        else:
            result[key] = ("directory", mode)
    return result


class Fixture(unittest.TestCase):
    source = CURRENT

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="audit pin test ")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.seed = self.root / "seed"
        self.target = self.root / "target"
        self.config = self.root / "gitconfig"
        self.env = dict(os.environ)
        self.env.update({
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": str(self.config),
            "GIT_ALLOW_PROTOCOL": "file", "GIT_TERMINAL_PROMPT": "0",
            "GIT_AUTHOR_NAME": "Offline fixture", "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
            "GIT_COMMITTER_NAME": "Offline fixture", "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
        })
        for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR",
                    "GIT_CONFIG_COUNT", "GIT_CONFIG_PARAMETERS"):
            self.env.pop(key, None)
        self.git("init", "-q", "--initial-branch=main", str(self.seed))
        (self.seed / "tracked").write_text("first\n")
        self.git("-C", str(self.seed), "add", "tracked")
        self.git("-C", str(self.seed), "commit", "-qm", "first")
        self.first = self.git("-C", str(self.seed), "rev-parse", "HEAD").stdout.strip()
        (self.seed / "tracked").write_text("second\n")
        self.git("-C", str(self.seed), "commit", "-qam", "second")
        self.second = self.git("-C", str(self.seed), "rev-parse", "HEAD").stdout.strip()
        self.git("config", "--global", f"url.{self.seed.as_uri()}.insteadOf", URL)
        self.sentinel = self.root / "unrelated-save"
        self.sentinel.write_bytes(b"private synthetic sentinel\x00\xff")

    def git(self, *args):
        return subprocess.run([REAL_GIT, *args], env=self.env, check=True,
                              text=True, capture_output=True)

    def existing(self, pin=None):
        self.git("clone", "-q", URL, str(self.target))
        if pin is not None:
            self.git("-C", str(self.target), "checkout", "-q", "--detach", pin)

    def run_helper(self, pin=None, target=None, source=None, env=None):
        body = "set -euo pipefail\n" + helper(source or self.source) + '\nclone "$@"\n'
        return subprocess.run(["bash", "-c", body, "fixture", REPO,
                               pin or self.first[:7], str(target or self.target)],
                              env=env or self.env, text=True, capture_output=True, timeout=20)

    def check_unchanged(self, before, path=None):
        self.assertEqual(snapshot(path or self.target), before)
        self.assertEqual(self.sentinel.read_bytes(), b"private synthetic sentinel\x00\xff")

    def refuse_existing(self, pin=None):
        before = snapshot(self.target)
        result = self.run_helper(pin)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("verified ", result.stdout)
        self.check_unchanged(before)
        return result


class OriginalWitness(Fixture):
    source = ORIGINAL

    def test_baseline_existing_wrong_head_succeeds_without_pin(self):
        self.existing()
        before = snapshot(self.target)
        result = self.run_helper()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("skip ", result.stdout)
        self.assertEqual(self.git("-C", str(self.target), "rev-parse", "HEAD").stdout.strip(), self.second)
        self.assertNotEqual(self.first, self.second)
        self.check_unchanged(before)
        print("BASELINE WITNESS: original helper returned success at the wrong HEAD")

    def test_baseline_missing_pin_warning_still_succeeds(self):
        result = self.run_helper("0" * 40)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("WARNING: could not check out", result.stdout)
        self.assertEqual(self.git("-C", str(self.target), "rev-parse", "HEAD").stdout.strip(), self.second)
        print("BASELINE WITNESS: original helper returned success after pin checkout failure")


class RepairedChecks(Fixture):
    def test_original_and_repaired_tail_and_all_fifteen_pins_unchanged(self):
        self.assertEqual(CURRENT[CURRENT.index("\n# Audit targets"):],
                         ORIGINAL[ORIGINAL.index("\n# Audit targets"):])
        self.assertEqual(CURRENT[:CURRENT.index("clone() {")],
                         ORIGINAL[:ORIGINAL.index("clone() {")])
        pins = [line for line in CURRENT.splitlines() if line.startswith("clone ")]
        self.assertEqual(len(pins), 15)

    def test_original_source_git_blob_is_exactly_bound(self):
        raw = ORIGINAL.encode()
        blob = hashlib.sha1(f"blob {len(raw)}".encode() + bytes([0]) + raw).hexdigest()
        self.assertEqual(blob, "b976c94e104274876257832224bb7bf53995f0e8")

    def test_full_scripts_have_actual_bash_syntax(self):
        for source in (ORIGINAL, CURRENT):
            result = subprocess.run(["bash", "-n"], input=source, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_fresh_short_pin_detaches_at_expected_commit_then_repeat_is_read_only(self):
        result = self.run_helper()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.git("-C", str(self.target), "rev-parse", "HEAD").stdout.strip(), self.first)
        self.assertEqual(self.git("-C", str(self.target), "rev-parse", "--abbrev-ref", "HEAD").stdout.strip(), "HEAD")
        before = snapshot(self.target)
        repeated = self.run_helper()
        self.assertEqual(repeated.returncode, 0, repeated.stderr)
        self.assertIn("verified ", repeated.stdout)
        self.check_unchanged(before)

    def test_fresh_full_pin_with_spaces_in_target(self):
        target = self.root / "checkout with spaces"
        result = self.run_helper(self.first, target)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.git("-C", str(target), "rev-parse", "HEAD").stdout.strip(), self.first)

    def test_existing_correct_attached_head_is_read_only(self):
        self.existing()
        before = snapshot(self.target)
        result = self.run_helper(self.second)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.check_unchanged(before)
        self.assertEqual(self.git("-C", str(self.target), "symbolic-ref", "HEAD").stdout.strip(), "refs/heads/main")

    def test_wrong_head_refused_without_reset(self):
        self.existing()
        result = self.refuse_existing()
        self.assertIn("wrong HEAD", result.stderr)

    def test_hex_named_branch_cannot_shadow_existing_commit_pin(self):
        self.existing()
        self.git("-C", str(self.target), "branch", self.first[:7], self.second)
        result = self.refuse_existing()
        self.assertIn("resolved to another revision", result.stderr)

    def test_hex_named_tag_cannot_shadow_fresh_commit_pin(self):
        self.git("-C", str(self.seed), "tag", self.first[:7], self.second)
        result = self.run_helper()
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("resolved to another revision", result.stderr)
        self.assertEqual(self.git("-C", str(self.target), "rev-parse", "HEAD").stdout.strip(), self.second)

    def test_wrong_origin_refused_without_rewrite(self):
        self.existing(self.first)
        self.git("-C", str(self.target), "remote", "set-url", "origin", "https://github.com/fixture/other")
        self.assertIn("wrong origin", self.refuse_existing().stderr)

    def test_missing_origin_refused(self):
        self.existing(self.first)
        self.git("-C", str(self.target), "remote", "remove", "origin")
        self.assertIn("no origin", self.refuse_existing().stderr)

    def test_unstaged_changes_refused(self):
        self.existing(self.first)
        (self.target / "tracked").write_text("keep this unstaged\n")
        self.assertIn("dirty checkout", self.refuse_existing().stderr)

    def test_staged_changes_refused_and_index_bytes_preserved(self):
        self.existing(self.first)
        (self.target / "tracked").write_text("keep this staged\n")
        self.git("-C", str(self.target), "add", "tracked")
        self.assertIn("dirty checkout", self.refuse_existing().stderr)

    def test_untracked_file_refused_and_preserved(self):
        self.existing(self.first)
        (self.target / "notes").write_text("keep private notes\n")
        self.assertIn("dirty checkout", self.refuse_existing().stderr)

    def test_existing_pin_missing_refused_without_fetch_or_write(self):
        self.existing(self.first)
        self.assertIn("pin ", self.refuse_existing("0" * 40).stderr)

    def test_existing_directory_outside_repo_refused(self):
        self.target.mkdir()
        (self.target / "private").write_text("keep")
        self.assertIn("not a direct Git checkout", self.refuse_existing().stderr)

    def test_existing_nested_directory_is_not_parent_repo(self):
        self.existing(self.first)
        nested = self.target / "nested"
        nested.mkdir()
        before = snapshot(self.target)
        result = self.run_helper(target=nested)
        self.assertNotEqual(result.returncode, 0)
        self.check_unchanged(before)

    def test_existing_regular_file_refused(self):
        self.target.write_text("keep file")
        before = snapshot(self.target)
        result = self.run_helper()
        self.assertNotEqual(result.returncode, 0)
        self.check_unchanged(before)

    def test_symlink_to_checkout_refused_without_modifying_referent(self):
        self.existing(self.first)
        link = self.root / "checkout link"
        link.symlink_to(self.target, target_is_directory=True)
        before = snapshot(self.target)
        result = self.run_helper(target=link)
        self.assertNotEqual(result.returncode, 0)
        self.check_unchanged(before)
        self.assertEqual(os.readlink(link), str(self.target))

    def test_dangling_symlink_refused(self):
        self.target.symlink_to(self.root / "absent", target_is_directory=True)
        before = snapshot(self.target)
        result = self.run_helper()
        self.assertNotEqual(result.returncode, 0)
        self.check_unchanged(before)

    def test_worktree_git_file_at_correct_pin_is_read_only(self):
        self.git("-C", str(self.seed), "remote", "add", "origin", URL)
        self.git("-C", str(self.seed), "worktree", "add", "-q", "--detach", str(self.target), self.first)
        before = snapshot(self.target)
        common_before = snapshot(self.seed)
        result = self.run_helper()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.check_unchanged(before)
        self.assertEqual(snapshot(self.seed), common_before)

    def test_missing_fresh_pin_is_fatal(self):
        result = self.run_helper("0" * 40)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("WARNING:", result.stdout)
        self.assertEqual(self.git("-C", str(self.target), "rev-parse", "HEAD").stdout.strip(), self.second)

    def test_invalid_ref_name_refused_before_clone(self):
        result = self.run_helper("main")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.target.exists())
        self.assertIn("invalid commit pin", result.stderr)

    def test_failed_checkout_is_fatal_even_inside_conditional_invocation(self):
        wrapper_dir = self.root / "bin"
        wrapper_dir.mkdir()
        wrapper = wrapper_dir / "git"
        wrapper.write_text("#!/usr/bin/env bash\n"
                           'if [[ "$1" == "-C" && "$3" == "checkout" ]]; then exit 66; fi\n'
                           f"exec {shlex.quote(REAL_GIT)} \"$@\"\n")
        wrapper.chmod(0o755)
        env = dict(self.env)
        env["PATH"] = str(wrapper_dir) + os.pathsep + env["PATH"]
        body = ("set -euo pipefail\n" + helper(CURRENT) +
                '\nif clone "$@"; then echo UNEXPECTED_SUCCESS; exit 99; else exit 0; fi\n')
        result = subprocess.run(["bash", "-c", body, "fixture", REPO, self.first,
                                 str(self.target)], env=env, text=True, capture_output=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("UNEXPECTED_SUCCESS", result.stdout)
        self.assertIn("could not check out pin", result.stderr)


if __name__ == "__main__":
    print("OFFLINE ONLY: actual Bash/Git temporary fixtures; no upstream/model/uv execution")
    unittest.main(verbosity=2)
