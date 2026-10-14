import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import importlib.util

SCRIPT = Path(__file__).with_name("validate-request.py")
spec = importlib.util.spec_from_file_location("validate_request", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
SHA, VERSION, validate = module.SHA, module.VERSION, module.validate


class RequestTests(unittest.TestCase):
    def event(self, event_name, publish=True):
        event = {"repository": {"full_name": module.PUBLIC_REPOSITORY},
                 "sender": {"id": module.TRUSTED_SENDER_ID}}
        inputs = {"source_sha": SHA, "version": VERSION, "publish": publish}
        if event_name == "workflow_dispatch":
            event["inputs"] = {**inputs, "publish": str(publish).lower()}
        else:
            event.update(action="retrohero_release", client_payload={**inputs,
                "source_repository": module.SOURCE_REPOSITORY,
                "source_run_id": 123, "source_run_attempt": 1})
        return event

    def test_both_triggers_normalize_publication_mode(self):
        for event_name in ("repository_dispatch", "workflow_dispatch"):
            for publish in (True, False):
                with self.subTest(event=event_name, publish=publish):
                    payload = validate(self.event(event_name, publish), event_name)
                    self.assertIs(payload["publish"], publish)
                    self.assertEqual(payload["source_sha"], SHA)

    def test_refuses_unreviewed_source_version_sender_repository_and_extra_fields(self):
        for event_name in ("repository_dispatch", "workflow_dispatch"):
            key = "inputs" if event_name == "workflow_dispatch" else "client_payload"
            mutations = ((key, "source_sha", "a" * 40), (key, "source_sha", "main"),
                         (key, "source_sha", None), (key, "version", "0.8.2"),
                         ("sender", "id", 1), ("repository", "full_name", "someone/fork"),
                         (key, "extra", "ignored"), (key, "publish", "False"))
            for section, field, value in mutations:
                with self.subTest(event=event_name, field=field, value=value):
                    event = self.event(event_name)
                    event[section][field] = value
                    with self.assertRaises(AssertionError):
                        validate(event, event_name)

    def test_dispatch_requires_typed_identity_and_publication_mode(self):
        for field, value in (("source_repository", "someone/source"), ("source_run_id", True),
                             ("source_run_id", "123"), ("source_run_attempt", 0),
                             ("publish", "true"), ("publish", "false")):
            with self.subTest(field=field, value=value):
                event = self.event("repository_dispatch")
                event["client_payload"][field] = value
                with self.assertRaises(AssertionError):
                    validate(event)
        event = self.event("repository_dispatch")
        event["action"] = "untrusted"
        with self.assertRaises(AssertionError):
            validate(event)
        with self.assertRaises(AssertionError):
            validate(event, "push")

    def test_cli_checks_main_and_emits_false_without_source_access(self):
        for event_name in ("repository_dispatch", "workflow_dispatch"):
            for ref in ("refs/heads/main", "refs/heads/other"):
                with self.subTest(event=event_name, ref=ref), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    event_file, output = root / "event.json", root / "output"
                    event_file.write_text(json.dumps(self.event(event_name, False)))
                    env = {**os.environ, "GITHUB_EVENT_NAME": event_name,
                           "GITHUB_EVENT_PATH": str(event_file), "GITHUB_OUTPUT": str(output),
                           "GITHUB_REPOSITORY": module.PUBLIC_REPOSITORY, "GITHUB_REF": ref}
                    result = subprocess.run([sys.executable, str(SCRIPT)], env=env, capture_output=True)
                    if ref == "refs/heads/main":
                        self.assertEqual(result.returncode, 0, result.stderr)
                        self.assertEqual(output.read_text(), "publish=false\n")
                    else:
                        self.assertNotEqual(result.returncode, 0)
                        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
