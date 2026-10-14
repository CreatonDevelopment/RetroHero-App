"""Check the scoped source token without printing credentials or private responses."""
import os
import sys
import urllib.error
import urllib.request


def check(token, sha):
    request = urllib.request.Request(
        f"https://api.github.com/repos/CreatonDevelopment/RetroHero/git/commits/{sha}",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
                 "User-Agent": "RetroHero-source-access-check"},
    )
    try:
        with urllib.request.urlopen(request, timeout=20):
            pass
    except urllib.error.HTTPError as error:
        messages = {
            401: "Private-source credential is invalid or expired (HTTP 401).",
            403: "Private-source credential was denied (HTTP 403); check Contents:read and organization approval.",
            404: "Private-source credential cannot read the reviewed commit (HTTP 404); check resource owner CreatonDevelopment, selected repository RetroHero, and Contents:read.",
        }
        print("::error::" + messages.get(error.code, "Private-source API check failed; retry or check GitHub service status."))
        return 1
    except (urllib.error.URLError, TimeoutError):
        print("::error::Private-source API check could not reach GitHub; retry or check service status.")
        return 1
    print("Reviewed private-source access verified.")
    return 0


if __name__ == "__main__":
    sys.exit(check(os.environ["SOURCE_READ_TOKEN"], os.environ["SOURCE_SHA"]))
