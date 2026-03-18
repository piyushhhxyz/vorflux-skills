---
name: git-commit
description: This skill should be used when the user asks to commit changes, write a commit message, stage and commit files, create a git commit, or push changes. Trigger phrases include "commit my changes", "write a commit message", "stage and commit", "git commit", "commit and push", "make a commit", "commit everything".
version: 1.0.0
license: MIT
allowed-tools:
  - read
  - write
  - bash
metadata:
  version: "1.0"
  tags: [git, workflow, conventional-commits]
---

# git-commit — Smart Conventional Commit Automation

Analyze staged/unstaged changes and generate a high-quality [Conventional Commits](https://www.conventionalcommits.org/) message, then commit. Used by Angular, React, Vue, Nx, and most major OSS monorepos.

## How to use

```
/git-commit [optional hint]
```

## Instructions

### Step 1 — Inspect repo state

Run the analysis script to get a full diff summary:

```bash
bash ${SKILL_DIR}/scripts/analyze_changes.sh
```

### Step 2 — Write commit message

Using the diff analysis, write a message following `templates/commit_types.md` conventions. Build message from the template in `templates/commit_message.txt`.

Key rules:
- Type must match the primary change (feat > fix > refactor > chore)
- Scope = the module/directory most affected (omit if project-wide)
- Summary: max 72 chars, imperative mood, no period
- Breaking changes: add `BREAKING CHANGE:` footer

### Step 3 — Commit

```bash
bash ${SKILL_DIR}/scripts/do_commit.sh "<type>(<scope>): <summary>" "<optional body>"
```

### Step 4 — Offer push

Ask if the user wants to `git push` or open a PR.
