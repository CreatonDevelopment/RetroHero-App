#!/usr/bin/env bash
set -euo pipefail
umask 077
if [[ "$SOURCE_SHA" != "$APPROVED_SOURCE_SHA" || ! "$SOURCE_SHA" =~ ^[0-9a-f]{40}$ || -z "$SOURCE_READ_TOKEN" ]]; then
  echo '::error::Private source access or reviewed SHA is not ready.'
  exit 1
fi
python3 "$(dirname "$0")/check-source-access.py"
log=$(mktemp "$RUNNER_TEMP/private-checkout.XXXXXX")
askpass=$(mktemp "$RUNNER_TEMP/private-askpass.XXXXXX")
trap 'rm -f "$log" "$askpass"' EXIT
cat > "$askpass" <<'ASKPASS'
#!/bin/sh
case "$1" in
  *Username*) printf '%s\n' x-access-token ;;
  *Password*) printf '%s\n' "$SOURCE_READ_TOKEN" ;;
  *) exit 1 ;;
esac
ASKPASS
chmod 700 "$askpass"
if ! (
  export GIT_ASKPASS="$askpass" GIT_TERMINAL_PROMPT=0
  git init --quiet "$GITHUB_WORKSPACE/source" &&
  git -C "$GITHUB_WORKSPACE/source" remote add origin https://github.com/CreatonDevelopment/RetroHero.git &&
  git -C "$GITHUB_WORKSPACE/source" fetch --quiet --no-tags --depth=1 origin "$SOURCE_SHA" &&
  git -C "$GITHUB_WORKSPACE/source" checkout --quiet --detach FETCH_HEAD &&
  [[ "$(git -C "$GITHUB_WORKSPACE/source" rev-parse HEAD)" == "$APPROVED_SOURCE_SHA" ]]
) > "$log" 2>&1; then
  echo '::error::Private source checkout failed; diagnostics remain runner-local.'
  exit 1
fi
echo 'Reviewed source checkout verified.'
