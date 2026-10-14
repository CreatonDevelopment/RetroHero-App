#!/usr/bin/env bash
set -euo pipefail
umask 077
log=$(mktemp "$RUNNER_TEMP/private-step.XXXXXX")
summary=$(mktemp "$RUNNER_TEMP/private-summary.XXXXXX")
trap 'rm -f "$log" "$summary"' EXIT
source_root="$GITHUB_WORKSPACE/source"
if [[ ! "$PWD" -ef "$source_root" ]]; then
  echo '::error::Private release commands must run from the reviewed source checkout.'
  exit 1
fi
# Existing source scripts resolve compiler helpers from GITHUB_WORKSPACE
# and compare package identities against the reviewed private GITHUB_SHA.
# Keep the public orchestration workspace outside this private command process.
if ! GITHUB_WORKSPACE="$source_root" GITHUB_SHA="$APPROVED_SOURCE_SHA" GITHUB_STEP_SUMMARY="$summary" bash -euo pipefail > "$log" 2>&1; then
  echo '::error::Trusted release check failed; source-bearing diagnostics were withheld.'
  exit 1
fi
echo 'Trusted release step passed.'
