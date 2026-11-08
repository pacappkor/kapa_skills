#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
# source.md and raw annex TXT are machine-generated verbatim artifacts;
# generator --check steps validate generated content, not whitespace cleanup.
# Exclude both in every diff; authored files (including annex-md) stay checked.
set -euo pipefail
base=${1:?whitespace base required}
if [ "$base" = "$(git rev-parse HEAD)" ]; then
  echo 'Whitespace check skipped: no new commits (rewind or unchanged HEAD).'
  exit 0
fi
git diff --check "$base" HEAD -- . ':(exclude)sources/laws/*/annex/*.txt' ':(exclude)**/source.md'
