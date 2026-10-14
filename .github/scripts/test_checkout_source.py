import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name("checkout-private-source.sh")
SHA = "7ab1b301654013bcaf8a1569b86be4c0ddaf6ae7"


class CheckoutTests(unittest.TestCase):
    def execute(self, *, token="test-source-token", requested_sha=SHA, fail_fetch=False):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("bin", "workspace", "temp"):
                (root / name).mkdir()
            git = root / "bin/git"
            git.write_text('#!' + sys.executable + '''
import json, os, pathlib, sys
args = sys.argv[1:]
if "fetch" in args and os.environ["TEST_FAIL_FETCH"] == "1":
    print("private diagnostic", file=sys.stderr)
    raise SystemExit(1)
if "add" in args:
    helper = pathlib.Path(os.environ["GIT_ASKPASS"])
    pathlib.Path(os.environ["TEST_TRACE"]).write_text(json.dumps({
        "url": args[-1], "helper": str(helper),
        "helper_mode": helper.stat().st_mode & 0o777, "helper_text": helper.read_text(),
    }))
if "rev-parse" in args:
    print(os.environ["APPROVED_SOURCE_SHA"])
''')
            git.chmod(0o755)
            checker = root / "bin/python3"
            checker.write_text("#!/bin/sh\nexit 0\n")
            checker.chmod(0o755)
            env = {**os.environ, "PATH": str(root / "bin") + os.pathsep + os.environ["PATH"],
                   "RUNNER_TEMP": str(root / "temp"), "GITHUB_WORKSPACE": str(root / "workspace"),
                   "APPROVED_SOURCE_SHA": SHA, "SOURCE_SHA": requested_sha, "SOURCE_READ_TOKEN": token, "TEST_FAIL_FETCH": str(int(fail_fetch)),
                   "TEST_TRACE": str(root / "trace.json")}
            result = subprocess.run(["bash", str(SCRIPT)], env=env, text=True, capture_output=True)
            trace = json.loads((root / "trace.json").read_text()) if (root / "trace.json").exists() else None
            self.assertEqual(list((root / "temp").iterdir()), [], "Runner-local credentials must be removed")
            self.assertNotIn("test-source-token", result.stdout + result.stderr)
            self.assertNotIn("private diagnostic", result.stdout + result.stderr)
            return result, trace

    def test_scoped_token_uses_temporary_askpass_and_cleans_up(self):
        result, trace = self.execute()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(trace["url"], "https://github.com/CreatonDevelopment/RetroHero.git")
        self.assertEqual(trace["helper_mode"], 0o700)
        self.assertIn('$SOURCE_READ_TOKEN', trace["helper_text"])
        self.assertIn("Reviewed source checkout verified", result.stdout)

    def test_failed_fetch_sanitizes_diagnostics_and_cleans_up(self):
        result, _ = self.execute(fail_fetch=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Private source checkout failed", result.stdout)

    def test_unreviewed_sha_fails_before_credentials_are_written(self):
        result, trace = self.execute(requested_sha="a" * 40)
        self.assertNotEqual(result.returncode, 0)
        self.assertIsNone(trace)
        self.assertIn("Private source access or reviewed SHA is not ready", result.stdout)

    def test_missing_credentials_fails_closed(self):
        result, trace = self.execute(token="")
        self.assertNotEqual(result.returncode, 0)
        self.assertIsNone(trace)
        self.assertIn("Private source access or reviewed SHA is not ready", result.stdout)


if __name__ == "__main__":
    unittest.main()
