#!/usr/bin/env bash
# Refresh the vendored skills in plugins/alchemy/skills/ from the canonical
# source repo (alchemyplatform/skills). The Claude Code plugin format requires
# skills to live inside the plugin, so we vendor them here.
set -euo pipefail

SRC_REPO="${ALCHEMY_SKILLS_REPO:-https://github.com/alchemyplatform/skills.git}"
SRC_REF="${ALCHEMY_SKILLS_REF:-main}"

# Alchemy skills to vendor into the plugin. Partner/ecosystem skills
# (e.g. skills/ecosystem/*) are intentionally excluded.
SKILLS=(agentic-gateway alchemy-api alchemy-cli alchemy-mcp)

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$ROOT/plugins/alchemy/skills"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "Cloning $SRC_REPO ($SRC_REF)..."
git clone --depth 1 --branch "$SRC_REF" "$SRC_REPO" "$TMP/skills" >/dev/null 2>&1

echo "Syncing skills into $DEST ..."
rm -rf "$DEST"
mkdir -p "$DEST"
for skill in "${SKILLS[@]}"; do
  if [ -d "$TMP/skills/skills/$skill" ]; then
    cp -R "$TMP/skills/skills/$skill" "$DEST/"
    echo "  + $skill"
  else
    echo "  ! missing in source: $skill" >&2
  fi
done

echo "Done. Vendored skills:"
ls -1 "$DEST"
