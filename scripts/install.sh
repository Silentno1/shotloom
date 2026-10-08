#!/usr/bin/env bash
set -euo pipefail

PACKAGE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE="$PACKAGE_ROOT/skill/shotloom"
AGENT="agents"
TARGET=""
FORCE=0

usage() {
  printf '%s\n' "Usage: $0 [--agent agents|codex|claude] [--target PATH] [--force]"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent)
      [[ $# -ge 2 && -n "$2" ]] || { usage >&2; exit 2; }
      AGENT="${2:-}"
      shift 2
      ;;
    --target)
      [[ $# -ge 2 && -n "$2" ]] || { usage >&2; exit 2; }
      TARGET="${2:-}"
      shift 2
      ;;
    --force)
      FORCE=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf 'Unknown argument: %s\n' "$1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "$TARGET" ]]; then
  case "$AGENT" in
    agents) TARGET="$HOME/.agents/skills" ;;
    codex) TARGET="${CODEX_HOME:-$HOME/.codex}/skills" ;;
    claude) TARGET="$HOME/.claude/skills" ;;
    *)
      printf 'Unsupported agent target: %s\n' "$AGENT" >&2
      exit 2
      ;;
  esac
fi

DEST="$TARGET/shotloom"
[[ -f "$SOURCE/SKILL.md" ]] || { printf '%s\n' 'Skill source is missing.' >&2; exit 1; }
mkdir -p "$TARGET"
TARGET="$(cd "$TARGET" && pwd -P)"
DEST="$TARGET/shotloom"
if [[ -d "$DEST" && "$(cd "$DEST" && pwd -P)" == "$(cd "$SOURCE" && pwd -P)" ]]; then
  printf '%s\n' 'Refusing to replace the source folder itself.' >&2
  exit 1
fi

if [[ -e "$DEST" || -L "$DEST" ]]; then
  if [[ "$FORCE" -ne 1 ]]; then
    printf 'Refusing to replace existing installation: %s\n' "$DEST" >&2
    printf '%s\n' 'Run again with --force to create a backup and install.' >&2
    exit 1
  fi
fi

# Fully stage the copy before moving an existing install. A unique same-volume
# directory prevents same-second backup collisions and enables recoverable swap.
STAGE="$(mktemp -d "$TARGET/.shotloom-stage.XXXXXX")"
mkdir "$STAGE/shotloom"
if ! (tar -C "$SOURCE" --exclude='__pycache__' --exclude='*.pyc' --exclude='.DS_Store' -cf - . | tar -C "$STAGE/shotloom" -xf -); then
  printf 'Copy failed; existing install unchanged. Staging retained at %s\n' "$STAGE" >&2
  exit 1
fi
BACKUP=""
if [[ -e "$DEST" || -L "$DEST" ]]; then
  BACKUP_PARENT="$(mktemp -d "$TARGET/shotloom.backup-$(date +%Y%m%d-%H%M%S).XXXXXX")"
  BACKUP="$BACKUP_PARENT/shotloom"
  mv "$DEST" "$BACKUP"
  printf 'Backed up existing installation to %s\n' "$BACKUP"
fi
if ! mv "$STAGE/shotloom" "$DEST"; then
  if [[ -n "$BACKUP" && ! -e "$DEST" && ! -L "$DEST" ]]; then
    mv "$BACKUP" "$DEST"
    printf '%s\n' 'Previous installation restored.' >&2
  fi
  printf 'Install failed; staging retained at %s\n' "$STAGE" >&2
  exit 1
fi
rmdir "$STAGE"
printf 'Installed Shotloom to %s\n' "$DEST"
