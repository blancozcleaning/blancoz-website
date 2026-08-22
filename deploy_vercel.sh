#!/usr/bin/env bash
# Publish the built site to Vercel production.
#
# ~/code/blancoz-vercel-deploy is a staging copy, not a checkout. Copying files
# INTO it does not remove files that have since been deleted from the build, so
# renamed or dropped images linger there and stay publicly reachable long after
# GitHub Pages has correctly 404'd them. This script mirrors instead of copying:
# anything in the staging img/ that is no longer in the build is removed first.
#
# VERCEL_API_KEY is injected into the environment by the platform. It is passed
# by reference below and never printed.
set -euo pipefail

BUILD="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STAGE="$HOME/code/blancoz-vercel-deploy"

[ -f "$BUILD/index.html" ] || { echo "no build at $BUILD/index.html"; exit 1; }
[ -d "$STAGE/.vercel" ]    || { echo "no vercel project at $STAGE"; exit 1; }
[ -n "${VERCEL_API_KEY:-}" ] || { echo "VERCEL_API_KEY not set in this environment"; exit 1; }

mkdir -p "$STAGE/img"

# Drop staged images that the current build no longer produces.
orphans=$(comm -23 <(ls "$STAGE/img" | sort) <(ls "$BUILD/img" | sort) || true)
if [ -n "$orphans" ]; then
  echo "removing stale staged images:"
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    echo "  - $f"
    find "$STAGE/img" -maxdepth 1 -name "$f" -type f -delete
  done <<< "$orphans"
fi

cp -f "$BUILD/index.html"  "$STAGE/index.html"
cp -f "$BUILD/robots.txt"  "$STAGE/robots.txt"  2>/dev/null || true
cp -f "$BUILD/sitemap.xml" "$STAGE/sitemap.xml" 2>/dev/null || true
cp -rf "$BUILD/img/." "$STAGE/img/"

echo "staged $(ls "$STAGE/img" | wc -l) images (build has $(ls "$BUILD/img" | wc -l))"

cd "$STAGE"
npx --yes vercel@latest deploy --prod --yes --archive=tgz \
  --scope blancoz-cleaning --token "$VERCEL_API_KEY"
