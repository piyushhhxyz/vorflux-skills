---
name: ci-cd
description: This skill should be used when the user asks to set up CI/CD, create GitHub Actions workflows, configure a pipeline, add automated testing in CI, set up deployment automation, create a release workflow, or add continuous integration. Trigger phrases include "set up CI/CD", "create GitHub Actions", "add a CI pipeline", "automate deployments", "create release workflow", "add GitHub Actions", "set up continuous integration".
version: 1.0.0
license: MIT
allowed-tools:
  - read
  - write
  - bash
metadata:
  version: "1.0"
  tags: [ci-cd, github-actions, devops, automation, deployment]
---

# ci-cd — CI/CD Pipeline Generator

Generate production-ready GitHub Actions workflows for CI, CD, release automation, and security scanning. Based on patterns from major OSS projects.

## How to use

```
/ci-cd [workflow type]
```

Workflow types:
- `ci` — test + lint on every PR (default)
- `cd` — deploy on merge to main
- `release` — semantic versioning + changelog + GitHub release
- `security` — dependency audit + secret scanning + SAST
- `full` — all of the above

## Instructions

### Step 1 — Detect stack

Read `package.json`, `requirements.txt`, `go.mod`, `Cargo.toml` to detect language and test commands.

### Step 2 — Generate workflows

```bash
python3 ${SKILL_DIR}/scripts/gen_workflows.py [type]
```

This creates files in `.github/workflows/`.

### Step 3 — Report

List generated workflow files and their trigger conditions. Note any secrets that need to be added to GitHub repo settings.
