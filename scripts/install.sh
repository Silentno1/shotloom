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
TARGET_PARENT="$(dirname "$TARGET")"
if [[ "$TARGET_PARENT" == "$TARGET" ]]; then
  printf '%s\n' 'Use a dedicated skills directory, not a filesystem root.' >&2
  exit 1
fi
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

# Keep every inactive SKILL.md outside the discovery root, including failed
# copies. A hidden folder inside TARGET is still discoverable by some agents.
STATE_ROOT="$TARGET_PARENT/.$(basename "$TARGET").shotloom-installer"
if [[ -L "$STATE_ROOT" ]]; then
  printf 'Refusing linked installer storage: %s\n' "$STATE_ROOT" >&2
  exit 1
fi
mkdir -p "$STATE_ROOT"
device_id() {
  stat -c '%d' "$1" 2>/dev/null || stat -f '%d' "$1"
}
# Do not let mv turn the recoverable rename into a partial cross-volume copy.
TARGET_DEVICE="$(device_id "$TARGET")"
STATE_DEVICE="$(device_id "$STATE_ROOT")"
if [[ "$TARGET_DEVICE" != "$STATE_DEVICE" ]]; then
  printf '%s\n' 'Skills directory and installer storage must be on the same filesystem; use a dedicated directory below the mount root.' >&2
  exit 1
fi
STAGE="$(mktemp -d "$STATE_ROOT/stage-XXXXXX")"
mkdir "$STAGE/shotloom"
if ! (tar -C "$SOURCE" --exclude='__pycache__' --exclude='*.pyc' --exclude='.DS_Store' -cf - . | tar -C "$STAGE/shotloom" -xf -); then
  printf 'Copy failed; existing install unchanged. Staging retained at %s\n' "$STAGE" >&2
  exit 1
fi
BACKUP=""
if [[ -e "$DEST" || -L "$DEST" ]]; then
  BACKUP_PARENT="$(mktemp -d "$STATE_ROOT/backup-$(date +%Y%m%d-%H%M%S).XXXXXX")"
  BACKUP="$BACKUP_PARENT/shotloom"
  if ! mv "$DEST" "$BACKUP"; then
    printf 'Backup move failed; existing install unchanged. Staging retained at %s\n' "$STAGE" >&2
    exit 1
  fi
  printf 'Backed up existing installation to %s\n' "$BACKUP"
fi
if ! mv "$STAGE/shotloom" "$DEST"; then
  if [[ -n "$BACKUP" && ! -e "$DEST" && ! -L "$DEST" ]]; then
    if mv "$BACKUP" "$DEST"; then
      rmdir "$BACKUP_PARENT"
      printf '%s\n' 'Previous installation restored.' >&2
    else
      printf 'Restore failed; previous installation retained at %s\n' "$BACKUP" >&2
    fi
  fi
  printf 'Install failed; staging retained at %s\n' "$STAGE" >&2
  exit 1
fi
rmdir "$STAGE"
printf 'Installed Shotloom to %s\n' "$DEST"
