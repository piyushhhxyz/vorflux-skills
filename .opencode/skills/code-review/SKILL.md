---
name: code-review
description: This skill should be used when the user asks to review code, audit a file, check for bugs, find security issues, review a pull request, analyze code quality, or get feedback on code. Trigger phrases include "review this code", "audit this file", "find bugs", "code review", "review my PR", "check for security issues", "what's wrong with this code", "review the diff".
version: 1.0.0
license: MIT
allowed-tools:
  - read
  - bash
metadata:
  version: "1.0"
  tags: [review, security, quality, bugs]
---

# code-review — Deep Code Review

Perform a senior-engineer-level code review covering correctness, security, performance, and maintainability. Format: structured report with severity levels.

## How to use

```
/code-review [file, directory, or PR number]
```

## Instructions

### Step 1 — Get code to review

**File/dir:** Read the file(s) directly.

**Staged/unstaged diff:**
```bash
git diff HEAD
```

**PR:**
```bash
gh pr diff <number>
```

### Step 2 — Run static analysis (if applicable)

```bash
bash ${SKILL_DIR}/scripts/static_analysis.sh [file]
```

### Step 3 — Perform manual review

Use the 5-dimension checklist in `templates/review_checklist.md`.

### Step 4 — Output structured report

Fill in `templates/review_report.md` with findings grouped by severity.

Use these severity levels:
- 🔴 **Critical** — must fix before merge (bug, security hole, data loss risk)
- 🟡 **Major** — should fix (logic flaw, perf issue, missing error handling)
- 🟢 **Minor** — nice to fix (naming, style, small refactor opportunity)
- ✅ **Positive** — acknowledge good patterns
