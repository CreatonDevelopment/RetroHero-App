import json,os,pathlib,re
SHA="7ab1b301654013bcaf8a1569b86be4c0ddaf6ae7"
def validate(event):
    assert event.get("action")=="retrohero_release"
    assert event.get("sender",{}).get("id")==42785824
    assert event.get("repository",{}).get("full_name")=="CreatonDevelopment/RetroHero-App"
    payload=event.get("client_payload",{})
    assert set(payload)=={"source_repository","source_sha","version","publish","source_run_id","source_run_attempt"}
    assert payload["source_repository"]=="CreatonDevelopment/RetroHero"
    assert re.fullmatch("[0-9a-f]{40}",payload["source_sha"]) and payload["source_sha"]==SHA
    assert payload["version"]=="0.8.1"
    assert type(payload["publish"]) is bool
    assert type(payload["source_run_id"]) is int and payload["source_run_id"]>0
    assert type(payload["source_run_attempt"]) is int and payload["source_run_attempt"]>0
    return payload
if __name__=="__main__":
    assert os.environ["GITHUB_EVENT_NAME"]=="repository_dispatch"
    assert os.environ["GITHUB_REPOSITORY"]=="CreatonDevelopment/RetroHero-App"
    assert os.environ["GITHUB_REF"]=="refs/heads/main"
    validate(json.loads(pathlib.Path(os.environ["GITHUB_EVENT_PATH"]).read_text()))
    print("Reviewed dispatch metadata verified.")
