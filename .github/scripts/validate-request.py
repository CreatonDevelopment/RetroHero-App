import json
import os
from pathlib import Path
import re

SOURCE_REPOSITORY = "CreatonDevelopment/RetroHero"
PUBLIC_REPOSITORY = "CreatonDevelopment/RetroHero-App"
SHA = "7ab1b301654013bcaf8a1569b86be4c0ddaf6ae7"
VERSION = "0.8.1"
TRUSTED_SENDER_ID = 42785824


def validate(event, event_name="repository_dispatch"):
    assert event.get("sender", {}).get("id") == TRUSTED_SENDER_ID, "Untrusted release sender"
    assert event.get("repository", {}).get("full_name") == PUBLIC_REPOSITORY, "Unexpected repository"
    if event_name == "repository_dispatch":
        assert event.get("action") == "retrohero_release", "Unexpected dispatch type"
        payload = event.get("client_payload", {})
        assert set(payload) == {"source_repository", "source_sha", "version", "publish", "source_run_id", "source_run_attempt"}, "Unexpected dispatch fields"
        assert payload["source_repository"] == SOURCE_REPOSITORY, "Unexpected source repository"
        assert type(payload["publish"]) is bool, "Publication mode must be a boolean"
        assert type(payload["source_run_id"]) is int and payload["source_run_id"] > 0, "Invalid source run"
        assert type(payload["source_run_attempt"]) is int and payload["source_run_attempt"] > 0, "Invalid source attempt"
    elif event_name == "workflow_dispatch":
        inputs = event.get("inputs", {})
        assert set(inputs) == {"source_sha", "version", "publish"}, "Unexpected manual inputs"
        # The event file contains strings; the workflow inputs context has typed booleans.
        assert inputs["publish"] in ("true", "false"), "Publication mode must be true or false"
        payload = {**inputs, "source_repository": SOURCE_REPOSITORY, "publish": inputs["publish"] == "true"}
    else:
        raise AssertionError("Unsupported release event")
    assert isinstance(payload["source_sha"], str) and re.fullmatch("[0-9a-f]{40}", payload["source_sha"]) and payload["source_sha"] == SHA, "Source SHA has not been reviewed"
    assert payload["version"] == VERSION, "Version has not been approved"
    return payload


if __name__ == "__main__":
    assert os.environ["GITHUB_REPOSITORY"] == PUBLIC_REPOSITORY
    assert os.environ["GITHUB_REF"] == "refs/heads/main"
    payload = validate(json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text()), os.environ["GITHUB_EVENT_NAME"])
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
        output.write(f"publish={str(payload['publish']).lower()}\n")
    print("Reviewed release request verified.")
