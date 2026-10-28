#!/bin/sh
# Print the extdata bundle's name: a short hash of the files that determine
# its contents. The bundle is rebuilt, and published under a new name,
# exactly when one of them changes. Docs and the CI helper are left out, so
# editing them does not force a rebuild.
#
# Hashes working-tree contents, so uncommitted edits count; a new file counts
# once it is tracked (`git add`).
set -eu
# The C locale, so `sort` orders the files the same on every machine: under
# en_US.UTF-8 it ignores punctuation and gives a different hash than CI.
export LC_ALL=C
cd "$(dirname "$0")"
git ls-files -z -- Makefile sources.mk annotations-to-keep.txt sparql scripts \
	| sort -z \
	| xargs -0 sha256sum \
	| sha256sum \
	| cut -c1-16
