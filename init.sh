#!/usr/bin/env bash
# ============================================================
# init.sh — my-skills project bootstrap
# Run from repo root: bash init.sh
#
# What it does (all steps are IDEMPOTENT — safe to re-run):
#   1. Create .opencode/skills/ symlinks
#   2. Merge MCP server config into project .opencode/opencode.json
#   3. Check nowah-travel OAuth status
#   4. Check optional CLI tools (redbook)
# ============================================================

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
OPENCODE_DIR="$REPO_ROOT/.opencode"
SKILLS_DIR="$OPENCODE_DIR/skills"
CONFIG_FILE="$OPENCODE_DIR/opencode.jsonc"

# ---- helpers ------------------------------------------------

OK="\033[32m✓\033[0m"
WARN="\033[33m⚠\033[0m"
INFO="\033[36mℹ\033[0m"
SKIP="\033[90m· skip\033[0m"

step()  { echo -e "\n\033[1m▸ $1\033[0m"; }
ok()    { echo -e "  $OK $1"; }
warn()  { echo -e "  $WARN $1"; }
info()  { echo -e "  $INFO $1"; }
skip()  { echo -e "  $SKIP $1"; }

# ---- 1. Skills symlinks -------------------------------------

step "Setting up skill symlinks"
mkdir -p "$SKILLS_DIR"

declare -A SKILL_MAP=(
  ["skills-creator"]="../../skills-creator"
  ["travel-planner"]="../../travel-planner"
)

for skill_name in "${!SKILL_MAP[@]}"; do
  target="${SKILL_MAP[$skill_name]}"
  link="$SKILLS_DIR/$skill_name"

  if [ -L "$link" ]; then
    # True symlink — verify target
    current_target="$(readlink "$link" 2>/dev/null || true)"
    if [ "$current_target" = "$target" ]; then
      skip "$skill_name (symlink OK)"
    else
      warn "$skill_name symlink points to '$current_target', fixing → '$target'"
      rm "$link"
      ln -s "$target" "$link"
      ok "$skill_name → $target"
    fi
  elif [ -d "$link" ] && [ -f "$link/SKILL.md" ]; then
    # Windows junction or already-extracted directory with valid content — good enough
    skip "$skill_name (directory/junction OK)"
  elif [ -e "$link" ]; then
    warn "$skill_name exists but may not be a symlink — skipping"
  else
    ln -s "$target" "$link"
    ok "$skill_name → $target"
  fi
done

# ---- 2. MCP server config -----------------------------------

step "Checking MCP server config"
mkdir -p "$OPENCODE_DIR"

# Write JSONC with comments. Python handles stripping existing comments when reading.
python3 - "$CONFIG_FILE" <<'PYEOF'
import json, sys, os, re

config_path = sys.argv[1]

# Desired MCP config (oauth: {} triggers auto-discovery, not `true`)
desired_mcp = {
    "nowah-travel": {
        "type": "remote",
        "url": "https://claw.nowah.xyz/mcp",
        "oauth": {},
        "timeout": 30000
    },
    "12306": {
        "type": "local",
        "command": ["npx", "-y", "12306-mcp"],
        "timeout": 30000
    }
}

# Canonical JSONC to write (with helpful // comments)
CANONICAL_JSONC = '''\
// OpenCode project config — my-skills repo
// Run `bash init.sh` to regenerate. Edit as needed; format is JSONC (JSON with comments).
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {},
  "compaction": {
    "auto": true,
    "reserved": 20000
  },
  "mcp": {
    // 国内火车票（开箱即用，零 key）
    "12306": {
      "type": "local",
      "command": ["npx", "-y", "12306-mcp"],
      "timeout": 30000
    },
    // 国际航班/酒店/POI（需一次性 OAuth：opencode mcp auth nowah-travel）
    "nowah-travel": {
      "type": "remote",
      "url": "https://claw.nowah.xyz/mcp",
      "oauth": {},
      "timeout": 30000
    }
  }
}
'''

def parse_jsonc(text):
    """Strip // comments and trailing commas, then parse."""
    lines = [l for l in text.splitlines() if not l.lstrip().startswith('//')]
    clean = '\n'.join(lines)
    clean = re.sub(r',(\s*[}\]])', r'\1', clean)
    return json.loads(clean)

# Read existing file
if os.path.exists(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        current_text = f.read()
    try:
        current_config = parse_jsonc(current_text)
    except Exception:
        current_config = {}
else:
    current_text = ""
    current_config = {}

# Check mcp values match desired
def cmp(a, b):
    return json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)

mcp_ok = cmp(current_config.get("mcp", {}), desired_mcp)

if mcp_ok:
    # MCP is correct — check format: if it's not valid JSONC with our canonical structure,
    # still rewrite to ensure comments/formatting are canonical
    if "//" in current_text and "12306" in current_text and "nowah-travel" in current_text:
        # Already has comments + both servers — truly no-op
        print("SKIP MCP config already up-to-date")
    else:
        # Values right but missing JSONC comments — rewrite
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(CANONICAL_JSONC)
        print("OK mcp → canonical JSONC (with comments) written")
else:
    # Values differ — rewrite
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(CANONICAL_JSONC)
    print("OK mcp → written to JSONC config")
PYEOF

ok "Project config: $CONFIG_FILE"

# ---- 3. nowah-travel OAuth check -----------------------------

step "Checking nowah-travel OAuth"

# opencode mcp list shows auth status; check if "authenticated" line appears
if command -v opencode &>/dev/null; then
  mcp_output="$(opencode mcp list 2>&1 | tr -d '\0' || true)"

  # Heuristic: look for nowah-travel in the output and check auth state
  if echo "$mcp_output" | grep -qi "nowah.*\(auth\|token\|connected\|ok\|ready\)"; then
    ok "nowah-travel appears to be authenticated"
  else
    warn "nowah-travel OAuth may not be completed"
    echo ""
    echo "    To authenticate, run:"
    echo ""
    printf "    \033[1;37mopencode mcp auth nowah-travel\033[0m\n"
    echo ""
    echo "    This opens a browser for login. Required once for real-time"
    echo "    flight/hotel/POI queries via the nowah MCP server."
  fi
else
  warn "opencode CLI not found in PATH — skipping OAuth check"
  echo "    After installing opencode, run:"
  echo "    opencode mcp auth nowah-travel"
fi

# ---- 4. Optional CLI tools ----------------------------------

step "Checking optional CLI tools"

if command -v redbook &>/dev/null; then
  rb_version="$(redbook --version 2>/dev/null || echo 'installed')"
  ok "redbook CLI: $rb_version"
else
  warn "redbook CLI not installed (optional — for Xiaohongshu travel tips)"
  echo "    Install: npm install -g @lucasygu/redbook"
  echo "    After install, login to xiaohongshu.com in Chrome first"
fi

if command -v npx &>/dev/null; then
  ok "npx available (required for 12306-mcp)"
else
  warn "npx not found — 12306-mcp won't work without Node.js"
fi

# ---- Summary ------------------------------------------------

echo ""
echo -e "\033[1m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m"
echo -e "\033[1m  Setup complete!\033[0m"
echo ""
echo "  What was done:"
echo "    · Skill symlinks in .opencode/skills/"
echo "    · MCP servers in .opencode/opencode.jsonc"
echo ""
echo "  To verify everything works:"
echo "    opencode mcp list          # see connected servers"
echo ""
echo "  First time? Authenticate nowah:"
echo "    opencode mcp auth nowah-travel"
echo -e "\033[1m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m"
