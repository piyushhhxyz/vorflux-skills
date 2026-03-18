#!/usr/bin/env bash
# static_analysis.sh — run available linters/analyzers on a file or directory
# Usage: static_analysis.sh [path]

set -euo pipefail

TARGET="${1:-.}"
ISSUES=0

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; CYAN='\033[0;36m'; NC='\033[0m'

echo -e "${CYAN}═══════════════════════════════════════════${NC}"
echo -e "${CYAN}  Static Analysis: $TARGET${NC}"
echo -e "${CYAN}═══════════════════════════════════════════${NC}"

run_if_available() {
  local tool="$1"; shift
  if command -v "$tool" &>/dev/null; then
    echo -e "\n${GREEN}▶ $tool${NC}"
    "$tool" "$@" 2>&1 || true
    ISSUES=$((ISSUES + 1))
  else
    echo -e "${YELLOW}  (skipping $tool — not installed)${NC}"
  fi
}

# ── Python ────────────────────────────────────────────────────────────────────
if find "$TARGET" -name "*.py" -quit 2>/dev/null | grep -q .; then
  echo -e "\n${CYAN}── Python ──${NC}"
  run_if_available ruff check "$TARGET" --output-format=concise
  run_if_available mypy "$TARGET" --ignore-missing-imports --no-error-summary
  run_if_available bandit -r "$TARGET" -ll -q
fi

# ── JavaScript / TypeScript ────────────────────────────────────────────────────
if find "$TARGET" \( -name "*.js" -o -name "*.ts" -o -name "*.tsx" \) -quit 2>/dev/null | grep -q .; then
  echo -e "\n${CYAN}── JS/TS ──${NC}"
  if [ -f "package.json" ]; then
    run_if_available npx eslint "$TARGET" --max-warnings 0 2>/dev/null || true
  fi
fi

# ── Go ────────────────────────────────────────────────────────────────────────
if find "$TARGET" -name "*.go" -quit 2>/dev/null | grep -q .; then
  echo -e "\n${CYAN}── Go ──${NC}"
  run_if_available go vet ./...
  run_if_available staticcheck ./...
fi

# ── Shell scripts ─────────────────────────────────────────────────────────────
if find "$TARGET" -name "*.sh" -quit 2>/dev/null | grep -q .; then
  echo -e "\n${CYAN}── Shell ──${NC}"
  run_if_available shellcheck "$TARGET"
fi

# ── Security: secrets scan ────────────────────────────────────────────────────
echo -e "\n${CYAN}── Secret scan ──${NC}"
if command -v gitleaks &>/dev/null; then
  gitleaks detect --source "$TARGET" --no-git 2>&1 | tail -20 || true
elif command -v trufflehog &>/dev/null; then
  trufflehog filesystem "$TARGET" 2>&1 | tail -20 || true
else
  echo -e "${YELLOW}  (gitleaks/trufflehog not found — manual secret check recommended)${NC}"
  # Basic grep for common patterns
  echo "  Scanning for common secret patterns..."
  grep -rn --include="*.{py,js,ts,go,rb,env}" \
    -E "(password|secret|api_key|private_key|token)\s*=\s*['\"][^'\"]{8,}" \
    "$TARGET" 2>/dev/null | head -10 || echo "  No obvious patterns found."
fi

echo -e "\n${CYAN}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}Analysis complete.${NC}"
