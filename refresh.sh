#!/bin/bash
# Catalyst Watch — rebuild + deploy.
# Run AFTER data/catalysts.json has been updated (Claude does the research step).
# Usage:  bash refresh.sh
set -e
cd "$(dirname "$0")"
python3 build.py
git add -A
if git diff --cached --quiet; then
  echo "No changes to deploy."
  exit 0
fi
git commit -m "Refresh catalysts ($(date +%Y-%m-%d))"
git push origin main
echo "Pushed — GitHub Pages will redeploy https://everweston.github.io/catalyst-watch/ in ~1 min."
