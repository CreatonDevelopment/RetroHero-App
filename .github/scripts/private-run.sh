#!/usr/bin/env bash
set -euo pipefail
umask 077
log=$(mktemp "$RUNNER_TEMP/private-step.XXXXXX")
summary=$(mktemp "$RUNNER_TEMP/private-summary.XXXXXX")
trap 'rm -f "$log" "$summary"' EXIT
if ! GITHUB_STEP_SUMMARY="$summary" bash -euo pipefail > "$log" 2>&1; then
  echo '::error::Trusted release check failed; source-bearing diagnostics were withheld.'
  exit 1
fi
echo 'Trusted release step passed.'
