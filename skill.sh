#!/usr/bin/env bash
# Install CEO Operating System skill into .cursor/skills/ceo-operating-system/
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_NAME="ceo-operating-system"

usage() {
  cat <<EOF
Usage:
  ./skill.sh list
  ./skill.sh install /path/to/target/project

Copies: SKILL.md, VERSION, references/, tools/, templates/, frameworks/
  -> <target>/.cursor/skills/${SKILL_NAME}/
EOF
}

copy_skill() {
  local dest="$1"
  mkdir -p "${dest}"
  cp "${ROOT}/SKILL.md" "${ROOT}/VERSION" "${dest}/"
  for dir in references tools templates frameworks; do
    rm -rf "${dest}/${dir}"
    cp -R "${ROOT}/${dir}" "${dest}/${dir}"
  done
}

cmd="${1:-}"
case "$cmd" in
  list)
    echo "ceo-operating-system (v$(tr -d '\r\n' < "${ROOT}/VERSION"))"
    echo "  tools: saas_health, equity_calc, pitch scorer"
    echo "  references: $(find "${ROOT}/references" -name '*.md' | wc -l | tr -d ' ') files"
    ;;
  install)
    target="${2:-}"
    if [[ -z "$target" ]]; then
      usage
      exit 1
    fi
    abs_target="$(cd "$target" && pwd)"
    dest="${abs_target}/.cursor/skills/${SKILL_NAME}"
    copy_skill "${dest}"
    echo "Installed to ${dest}"
    echo "Reload Cursor → /ceo-operating-system"
    ;;
  *)
    usage
    exit 1
    ;;
esac
