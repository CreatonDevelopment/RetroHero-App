import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name("validate-request.py")
spec = importlib.util.spec_from_file_location("validate_request", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
SHA = "7ab1b301654013bcaf8a1569b86be4c0ddaf6ae7"


class RequestTests(unittest.TestCase):
    def event(self, event_name, *, bump="patch", publish=True):
        event = {
            "repository": {"full_name": module.PUBLIC_REPOSITORY},
            "sender": {"id": module.TRUSTED_SENDER_ID},
        }
        if event_name == "workflow_dispatch":
            event["inputs"] = {"bump": bump, "publish": str(publish).lower()}
        else:
            event.update(action="retrohero_release", client_payload={
                "source_repository": module.SOURCE_REPOSITORY,
                "source_sha": SHA,
                "bump": bump,
                "publish": publish,
                "source_run_id": 123,
                "source_run_attempt": 1,
            })
        return event

    def test_both_triggers_accept_each_bump(self):
        for event_name in ("repository_dispatch", "workflow_dispatch"):
            for bump in module.BUMPS:
                for publish in (True, False):
                    with self.subTest(event=event_name, bump=bump, publish=publish):
                        payload = module.validate(self.event(event_name, bump=bump, publish=publish), event_name, lambda: SHA)
                        self.assertEqual(payload["source_sha"], SHA)
                        self.assertEqual(payload["bump"], bump)
                        self.assertIs(payload["publish"], publish)

    def test_refuses_unknown_inputs_sender_and_repository(self):
        for event_name in ("repository_dispatch", "workflow_dispatch"):
            key = "inputs" if event_name == "workflow_dispatch" else "client_payload"
            mutations = [
                (key, "bump", "custom"),
                ("sender", "id", 1),
                ("repository", "full_name", "someone/fork"),
                (key, "extra", "ignored"),
                (key, "publish", "False"),
            ]
            if event_name == "repository_dispatch":
                mutations.extend([(key, "source_sha", "main"), (key, "source_sha", None)])
            for section, field, value in mutations:
                with self.subTest(event=event_name, field=field, value=value):
                    event = self.event(event_name)
                    event[section][field] = value
                    with self.assertRaises(AssertionError):
                        module.validate(event, event_name, lambda: SHA)

    def test_dispatch_requires_typed_identity_and_publication_mode(self):
        for field, value in (("source_repository", "someone/source"), ("source_run_id", True),
                             ("source_run_id", "123"), ("source_run_attempt", 0),
                             ("publish", "true"), ("publish", "false")):
            with self.subTest(field=field, value=value):
                event = self.event("repository_dispatch")
                event["client_payload"][field] = value
                with self.assertRaises(AssertionError):
                    module.validate(event)
        event = self.event("repository_dispatch")
        event["action"] = "untrusted"
        with self.assertRaises(AssertionError):
            module.validate(event)
        with self.assertRaises(AssertionError):
            module.validate(event, "push")

    def test_cli_emits_normalized_request_for_repository_dispatch(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            event_file, output = root / "event.json", root / "output"
            event_file.write_text(json.dumps(self.event("repository_dispatch", bump="minor", publish=False)))
            env = {
                **os.environ,
                "GITHUB_EVENT_NAME": "repository_dispatch",
                "GITHUB_EVENT_PATH": str(event_file),
                "GITHUB_OUTPUT": str(output),
                "GITHUB_REPOSITORY": module.PUBLIC_REPOSITORY,
                "GITHUB_REF": "refs/heads/main",
            }
            result = subprocess.run([sys.executable, str(SCRIPT)], env=env, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(output.read_text(), f"source_sha={SHA}\nbump=minor\npublish=false\n")


if __name__ == "__main__":
    unittest.main()
