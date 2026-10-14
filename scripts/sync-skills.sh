#!/usr/bin/env bash
# Refresh the vendored skills in plugins/alchemy/skills/ from the canonical
# source repo (alchemyplatform/skills). The Claude Code plugin format requires
# skills to live inside the plugin, so we vendor them here.
#
# The source commit is pinned in scripts/skills-source.lock. Skills are copied
# into a staging directory, rewritten for Claude Code by
# scripts/claude_overrides.py, and only then swapped into place.
#
#   ./scripts/sync-skills.sh            vendor the pinned commit
#   ./scripts/sync-skills.sh --update   resolve the source ref (default: main),
#                                       vendor it, and rewrite the lock file
set -euo pipefail

SRC_REPO="${ALCHEMY_SKILLS_REPO:-https://github.com/alchemyplatform/skills.git}"
SRC_REF="${ALCHEMY_SKILLS_REF:-main}"

# Alchemy skills to vendor into the plugin. alchemy-cli and agentic-gateway are
# intentionally excluded (they cover sends, swaps, bridges and payments), as are
# partner/ecosystem skills (e.g. skills/ecosystem/*).
SKILLS=(alchemy-api alchemy-mcp)

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOCK="$ROOT/scripts/skills-source.lock"
PLUGIN_DIR="$ROOT/plugins/alchemy"
DEST="$PLUGIN_DIR/skills"

UPDATE=0
case "${1:-}" in
  "") ;;
  --update) UPDATE=1 ;;
  *)
    echo "usage: $0 [--update]" >&2
    exit 2
    ;;
esac

TMP="$(mktemp -d)"
STAGING=""
BACKUP=""

cleanup() {
  status=$?
  trap - EXIT
  if [ "$status" -ne 0 ] && [ -n "$BACKUP" ] && [ -e "$BACKUP" ]; then
    rm -rf "$DEST"
    mv "$BACKUP" "$DEST"
    echo "Restored the previous $DEST" >&2
  fi
  [ -z "$STAGING" ] || rm -rf "$STAGING"
  rm -rf "$TMP"
  exit "$status"
}
trap cleanup EXIT
trap 'exit 130' INT TERM HUP

CLONE="$TMP/skills"

if [ "$UPDATE" -eq 1 ]; then
  echo "Cloning $SRC_REPO ($SRC_REF)..."
  git clone --quiet --branch "$SRC_REF" "$SRC_REPO" "$CLONE"
  SHA="$(git -C "$CLONE" rev-parse HEAD)"
else
  SHA="$(tr -d '[:space:]' < "$LOCK")"
  if ! [[ "$SHA" =~ ^[0-9a-f]{40}$ ]]; then
    echo "error: $LOCK must contain one full 40-character commit SHA" >&2
    exit 1
  fi
  echo "Cloning $SRC_REPO and checking out $SHA..."
  git clone --quiet "$SRC_REPO" "$CLONE"
  git -C "$CLONE" checkout --quiet --detach "$SHA"
  if [ "$(git -C "$CLONE" rev-parse HEAD)" != "$SHA" ]; then
    echo "error: checked out commit does not match $SHA" >&2
    exit 1
  fi
fi

# Staging lives next to the destination so the final move is a rename.
STAGING="$(mktemp -d "$PLUGIN_DIR/.skills-staging.XXXXXX")"
chmod 755 "$STAGING"

echo "Staging skills from $SHA ..."
for skill in "${SKILLS[@]}"; do
  if [ ! -d "$CLONE/skills/$skill" ]; then
    echo "error: skill missing in source: $skill" >&2
    exit 1
  fi
  cp -R "$CLONE/skills/$skill" "$STAGING/"
  echo "  + $skill"
done

echo "Applying Claude Code overrides ..."
python3 "$ROOT/scripts/claude_overrides.py" "$STAGING"

printf '%s\n' "$SHA" > "$STAGING/.source-commit"
if [ "$UPDATE" -eq 1 ]; then
  printf '%s\n' "$SHA" > "$TMP/skills-source.lock"
fi

# Swap in the validated tree. This is not atomic: there is a brief window
# between the two renames where $DEST does not exist. If the second rename
# fails, the cleanup trap restores the previous directory from the backup.
if [ -e "$DEST" ]; then
  BACKUP="$PLUGIN_DIR/.skills-backup.$$"
  rm -rf "$BACKUP"
  mv "$DEST" "$BACKUP"
fi
mv "$STAGING" "$DEST"
STAGING=""
if [ -n "$BACKUP" ]; then
  OLD="$BACKUP"
  BACKUP=""
  rm -rf "$OLD"
fi

if [ "$UPDATE" -eq 1 ]; then
  mv "$TMP/skills-source.lock" "$LOCK"
  echo "Pinned source commit updated: $SHA"
fi

echo "Done. Vendored skills (source $SHA):"
ls -1 "$DEST"
