import json
import os
from pathlib import Path
import re
import urllib.request

SOURCE_REPOSITORY = "CreatonDevelopment/RetroHero"
PUBLIC_REPOSITORY = "CreatonDevelopment/RetroHero-App"
TRUSTED_SENDER_ID = 42785824
BUMPS = {"patch", "minor", "major"}


def private_main_sha():
    token = os.environ.get("SOURCE_READ_TOKEN")
    assert token, "Protected source credential is missing"
    request = urllib.request.Request(
        f"https://api.github.com/repos/{SOURCE_REPOSITORY}/git/ref/heads/main",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "RetroHero-public-release",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        sha = json.load(response)["object"]["sha"]
    assert isinstance(sha, str) and re.fullmatch("[0-9a-f]{40}", sha), "Private main did not resolve to a commit"
    return sha


def validate(event, event_name="repository_dispatch", resolve_source=private_main_sha):
    assert event.get("sender", {}).get("id") == TRUSTED_SENDER_ID, "Untrusted release sender"
    assert event.get("repository", {}).get("full_name") == PUBLIC_REPOSITORY, "Unexpected repository"
    if event_name == "repository_dispatch":
        assert event.get("action") == "retrohero_release", "Unexpected dispatch type"
        payload = event.get("client_payload", {})
        assert set(payload) == {"source_repository", "source_sha", "bump", "publish", "source_run_id", "source_run_attempt"}, "Unexpected dispatch fields"
        assert payload["source_repository"] == SOURCE_REPOSITORY, "Unexpected source repository"
        assert isinstance(payload["source_sha"], str) and re.fullmatch("[0-9a-f]{40}", payload["source_sha"]), "Invalid source SHA"
        assert type(payload["publish"]) is bool, "Publication mode must be a boolean"
        assert type(payload["source_run_id"]) is int and payload["source_run_id"] > 0, "Invalid source run"
        assert type(payload["source_run_attempt"]) is int and payload["source_run_attempt"] > 0, "Invalid source attempt"
    elif event_name == "workflow_dispatch":
        inputs = event.get("inputs", {})
        assert set(inputs) == {"bump", "publish"}, "Unexpected manual inputs"
        assert inputs["publish"] in ("true", "false"), "Publication mode must be true or false"
        payload = {
            "source_repository": SOURCE_REPOSITORY,
            "source_sha": resolve_source(),
            "bump": inputs["bump"],
            "publish": inputs["publish"] == "true",
        }
    else:
        raise AssertionError("Unsupported release event")
    assert payload["bump"] in BUMPS, "Version bump must be patch, minor, or major"
    return payload


if __name__ == "__main__":
    assert os.environ["GITHUB_REPOSITORY"] == PUBLIC_REPOSITORY
    assert os.environ["GITHUB_REF"] == "refs/heads/main"
    payload = validate(json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text()), os.environ["GITHUB_EVENT_NAME"])
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
        output.write(f"source_sha={payload['source_sha']}\n")
        output.write(f"bump={payload['bump']}\n")
        output.write(f"publish={str(payload['publish']).lower()}\n")
    print("Release request verified.")
