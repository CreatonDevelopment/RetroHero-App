import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).with_name("private-run.sh").resolve()


class PrivateRunTests(unittest.TestCase):
    def execute(self, command, *, source_cwd=True):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            source = root / "source"
            (source / "scripts/muos").mkdir(parents=True)
            (source / "scripts/muos/zig-cc.py").write_text("# Compiler wrapper fixture\n")
            temp = root / "temp"
            temp.mkdir()
            real_summary = root / "summary"
            env = {**os.environ, "GITHUB_WORKSPACE": str(root), "RUNNER_TEMP": str(temp),
                   "GITHUB_STEP_SUMMARY": str(real_summary), "APPROVED_SOURCE_SHA": "a" * 40,
                   "GITHUB_SHA": "b" * 40}
            result = subprocess.run(["bash", str(SCRIPT)], input=command, cwd=source if source_cwd else root,
                                    env=env, text=True, capture_output=True)
            self.assertFalse(real_summary.exists(), "Source summaries must stay private")
            self.assertEqual(list(temp.iterdir()), [], "Private diagnostics must be removed")
            self.assertNotIn("private diagnostic", result.stdout + result.stderr)
            return result

    def test_existing_compiler_helper_resolves_inside_source_checkout(self):
        result = self.execute('test "$GITHUB_WORKSPACE" = "$PWD"\ntest -f "$GITHUB_WORKSPACE/scripts/muos/zig-cc.py"\necho "private diagnostic"\necho "private diagnostic" > "$GITHUB_STEP_SUMMARY"\n')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Trusted release step passed", result.stdout)

    def test_miyoo_package_identity_uses_private_sha_instead_of_orchestration_sha(self):
        result = self.execute('test "$GITHUB_SHA" = "$APPROVED_SOURCE_SHA"\n')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_private_command_failure_remains_sanitized(self):
        result = self.execute('echo "private diagnostic" >&2\nexit 1\n')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("diagnostics were withheld", result.stdout)

    def test_public_workspace_cannot_run_private_commands(self):
        result = self.execute('echo "private diagnostic"\n', source_cwd=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("reviewed source checkout", result.stdout)


if __name__ == "__main__":
    unittest.main()
