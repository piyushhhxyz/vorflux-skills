#!/usr/bin/env bash
# analyze_changes.sh — summarize repo state for commit message generation

set -euo pipefail

RED='\033[0;31m'; YELLOW='\033[1;33m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; NC='\033[0m'

echo -e "${CYAN}═══════════════════════════════════════════${NC}"
echo -e "${CYAN}  Git Change Analysis${NC}"
echo -e "${CYAN}═══════════════════════════════════════════${NC}"

# ── Branch info ───────────────────────────────────────────────────────────────
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
echo -e "\n${GREEN}Branch:${NC} $BRANCH"

# ── Recent commits (context) ──────────────────────────────────────────────────
echo -e "\n${GREEN}Recent commits (style reference):${NC}"
git log --oneline -5 2>/dev/null || echo "(no commits yet)"

# ── Staged changes ────────────────────────────────────────────────────────────
echo -e "\n${GREEN}Staged files:${NC}"
STAGED=$(git diff --cached --name-status 2>/dev/null)
if [ -z "$STAGED" ]; then
  echo -e "${YELLOW}  (nothing staged — will show unstaged)${NC}"
else
  echo "$STAGED"
fi

# ── Unstaged changes ──────────────────────────────────────────────────────────
echo -e "\n${GREEN}Unstaged modified files:${NC}"
UNSTAGED=$(git diff --name-status 2>/dev/null)
if [ -z "$UNSTAGED" ]; then
  echo "  (none)"
else
  echo "$UNSTAGED"
fi

# ── Untracked files ───────────────────────────────────────────────────────────
echo -e "\n${GREEN}Untracked files:${NC}"
UNTRACKED=$(git ls-files --others --exclude-standard 2>/dev/null | head -20)
if [ -z "$UNTRACKED" ]; then
  echo "  (none)"
else
  echo "$UNTRACKED"
fi

# ── Diff stats ────────────────────────────────────────────────────────────────
echo -e "\n${GREEN}Diff stats (staged):${NC}"
git diff --cached --stat 2>/dev/null || echo "  (nothing staged)"

echo -e "\n${GREEN}Full staged diff (first 200 lines):${NC}"
git diff --cached 2>/dev/null | head -200 || echo "  (nothing staged)"

# ── Security check ────────────────────────────────────────────────────────────
echo -e "\n${YELLOW}Security scan (looking for secrets in staged files):${NC}"
SECRETS_FOUND=0
PATTERNS=("password\s*=" "secret\s*=" "api_key\s*=" "private_key" "AWS_SECRET" "BEGIN RSA" "token\s*=")
for pat in "${PATTERNS[@]}"; do
  HITS=$(git diff --cached -I "$pat" 2>/dev/null | grep -i "$pat" | head -3 || true)
  if [ -n "$HITS" ]; then
    echo -e "${RED}  ⚠️  Possible secret pattern found: $pat${NC}"
    echo "$HITS"
    SECRETS_FOUND=1
  fi
done
if [ $SECRETS_FOUND -eq 0 ]; then
  echo -e "${GREEN}  ✅ No obvious secret patterns detected${NC}"
fi

echo -e "\n${CYAN}═══════════════════════════════════════════${NC}"
