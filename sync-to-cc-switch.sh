#!/usr/bin/env bash
#
# sync-to-cc-switch.sh
# 把本仓库里的每个 skill（含 SKILL.md 的目录）同步进 cc-switch 管理。
#
# 行为：
#   - rsync 到 ~/.cc-switch/skills/<name>（只补不删，排除 .DS_Store/.git）
#   - 新 skill：在 cc-switch.db 写入 local:<name> 记录（默认对 claude/codex 启用），
#     并在 ~/.claude/skills、~/.codex/skills 建软链
#   - 已存在的 skill：仅刷新文件内容，不动 DB（content_hash 由 cc-switch 自查）
#   - 任何写库前先备份 DB
#
# 用法：
#   ./sync-to-cc-switch.sh            # 同步全部 skill
#   ./sync-to-cc-switch.sh <name> ... # 只同步指定 skill
#
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CC_SKILLS="$HOME/.cc-switch/skills"
DB="$HOME/.cc-switch/cc-switch.db"
LINK_DIRS=("$HOME/.claude/skills" "$HOME/.codex/skills")  # enabled_claude / enabled_codex

command -v sqlite3 >/dev/null || { echo "缺少 sqlite3，请先安装"; exit 1; }
[ -f "$DB" ] || { echo "找不到 cc-switch 数据库: $DB"; exit 1; }
mkdir -p "$CC_SKILLS"

# 待同步的 skill 列表：参数指定，或自动发现含 SKILL.md 的目录
if [ "$#" -gt 0 ]; then
  SKILLS=("$@")
else
  SKILLS=()
  for d in "$REPO_DIR"/*/; do
    [ -f "${d}SKILL.md" ] && SKILLS+=("$(basename "$d")")
  done
fi
[ "${#SKILLS[@]}" -gt 0 ] || { echo "没有发现可同步的 skill"; exit 0; }

# 是否需要写库（有新 skill 时才备份+写）
DB_BACKED_UP=0
backup_db_once() {
  [ "$DB_BACKED_UP" -eq 1 ] && return
  local ts; ts="$(date +%Y%m%d-%H%M%S)"
  cp "$DB" "$DB.bak.$ts"
  echo "  · DB 已备份 -> cc-switch.db.bak.$ts"
  DB_BACKED_UP=1
}

for name in "${SKILLS[@]}"; do
  src="$REPO_DIR/$name"
  if [ ! -f "$src/SKILL.md" ]; then
    echo "跳过 $name：$src/SKILL.md 不存在"
    continue
  fi
  echo "==> $name"

  # 1) 同步文件
  rsync -a --exclude='.DS_Store' --exclude='.git' "$src/" "$CC_SKILLS/$name/"

  # 2) 是否已在 DB
  exists="$(sqlite3 "$DB" "SELECT 1 FROM skills WHERE id='local:$name' LIMIT 1;")"
  if [ -z "$exists" ]; then
    echo "  · 新 skill，写入 DB 记录并建软链"
    backup_db_once
    desc="$(awk -F': ' '/^description:/{ sub(/^description: /,""); print; exit }' "$src/SKILL.md")"
    now="$(date +%s)"
    sqlite3 "$DB" <<SQL
INSERT OR REPLACE INTO skills
 (id,name,description,directory,repo_owner,repo_name,repo_branch,readme_url,
  enabled_claude,enabled_codex,enabled_gemini,enabled_opencode,enabled_hermes,
  installed_at,content_hash,updated_at)
VALUES
 ('local:$name','$name',$(sqlite3 "$DB" "SELECT quote('$desc')"),'$name','','','','',
  1,1,0,0,0,$now,NULL,0);
SQL
    for ld in "${LINK_DIRS[@]}"; do
      [ -d "$ld" ] || continue
      ln -sfn "$CC_SKILLS/$name" "$ld/$name"
      echo "    -> $ld/$name"
    done
  else
    echo "  · 已存在，仅刷新文件"
  fi
done

echo "完成。cc-switch 当前共 $(sqlite3 "$DB" "SELECT count(*) FROM skills;") 个 skill。"
echo "提示：打开 cc-switch app 后会自动重算 content_hash。"
