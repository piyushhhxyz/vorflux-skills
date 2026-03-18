---
name: readme-gen
description: This skill should be used when the user asks to generate a README, create project documentation, write a README.md, document their project, create an open-source README, or add a getting-started guide. Trigger phrases include "generate a README", "create README.md", "write project docs", "document my project", "create a getting started guide", "write a README for this project".
version: 1.0.0
license: MIT
allowed-tools:
  - read
  - write
  - bash
metadata:
  version: "1.0"
  tags: [documentation, readme, markdown, open-source]
---

# readme-gen — Professional README Generator

Analyze a project and generate a comprehensive, well-structured README.md following best practices from top OSS projects (React, FastAPI, Tailwind, etc.).

## How to use

```
/readme-gen [directory or repo name]
```

## Instructions

### Step 1 — Analyze the project

Scan the project to detect:
- Language/framework (`package.json`, `requirements.txt`, `go.mod`, etc.)
- Entry points and main scripts
- Existing docs, `CHANGELOG`, `LICENSE`, `CONTRIBUTING.md`
- CI/CD config (GitHub Actions, etc.)
- Port numbers, environment variables

```bash
python3 ${SKILL_DIR}/scripts/analyze_project.py .
```

### Step 2 — Fill the template

Use `templates/README.md.j2` as the base. Fill all sections with real project-specific information — no generic placeholders.

Must include:
- Project name + one-line description
- Badges (CI status, version, license)
- Features list (3–7 bullets, specific to this project)
- Prerequisites & installation (exact commands)
- Usage examples with real code snippets
- Environment variables table
- API overview (if applicable)
- Contributing guide
- License

### Step 3 — Write output

Write to `README.md` (or `README_generated.md` if one already exists).

### Step 4 — Quality check

Verify:
- All code blocks have language hints (` ```bash `, ` ```python `)
- All links are relative or confirmed-valid
- No generic placeholder text remains (`your-project`, `TODO`, `example.com`)
