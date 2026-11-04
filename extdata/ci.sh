#!/bin/sh
# CI helper for the extdata bundle. Used by the deploy workflows; see README.md.
#
#   ci.sh fetch     put the bundle for the current inputs in dist/: download
#                   the published release if there is one, otherwise build it
#   ci.sh publish   publish dist/ as release extdata-<hash>, unless it exists
#
# Needs `gh` with a token in GH_TOKEN; `publish` needs contents: write.
set -eu
cd "$(dirname "$0")"

hash=$(./hash.sh)
tag="extdata-$hash"
asset="extdata-$hash.tar.gz"

case "${1:-}" in
fetch)
	if [ -f dist/manifest.json ] && grep -q "\"hash\": \"$hash\"" dist/manifest.json; then
		echo "extdata $hash: already in dist/"
	elif gh release download "$tag" --pattern "$asset" --dir tmp --clobber 2>/dev/null; then
		echo "extdata $hash: downloaded release $tag"
		rm -rf dist
		mkdir -p dist
		tar -xzf "tmp/$asset" -C dist
	else
		echo "extdata $hash: no release $tag, building"
		make all
	fi
	;;
publish)
	if gh release view "$tag" >/dev/null 2>&1; then
		echo "extdata $hash: release $tag already exists"
		exit 0
	fi
	mkdir -p tmp
	tar -czf "tmp/$asset" -C dist .
	# --latest=false: these are data bundles, not app releases, and must never
	# become the repository's "Latest" release.
	gh release create "$tag" "tmp/$asset" dist/manifest.json \
		--title "extdata $hash" \
		--notes "Ontology bundle for the app, built from extdata/ (see extdata/README.md). Not an app release." \
		--latest=false
	echo "extdata $hash: published release $tag"
	;;
*)
	echo "usage: $0 fetch|publish" >&2
	exit 2
	;;
esac
