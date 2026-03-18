---
name: changelog
description: This skill should be used when the user asks to generate a changelog, update CHANGELOG.md, create release notes, document what changed in a version, summarize git history into a changelog, or prepare release documentation. Trigger phrases include "generate changelog", "update CHANGELOG.md", "create release notes", "what changed in this version", "generate release notes", "document changes", "prepare changelog for release".
version: 1.0.0
license: MIT
allowed-tools:
  - read
  - write
  - bash
metadata:
  version: "1.0"
  tags: [changelog, release-notes, git, versioning]
---

# changelog — Changelog & Release Notes Generator

Parse git history following [Conventional Commits](https://www.conventionalcommits.org/) and generate a formatted `CHANGELOG.md` and GitHub release notes. Used by Angular, Vue, semantic-release, and most major OSS release pipelines.

## How to use

```
/changelog [version] [--since <tag>]
```

Examples:
- `/changelog` — generate unreleased changes
- `/changelog v2.4.0` — generate changelog for v2.4.0
- `/changelog --since v2.3.0` — changes since a specific tag

## Instructions

### Step 1 — Get git log

```bash
python3 ${SKILL_DIR}/scripts/gen_changelog.py [version] [--since <tag>]
```

### Step 2 — Format output

The script outputs:
- `CHANGELOG_ENTRY.md` — new entry to prepend to CHANGELOG.md
- `RELEASE_NOTES.md` — GitHub release body (shorter, user-facing)

### Step 3 — Update CHANGELOG.md

Prepend the new entry to the top of `CHANGELOG.md` (after the header), keeping old entries.

### Step 4 — Confirm

Show the user the new changelog entry and ask if they want to commit it.

## Changelog format (Keep a Changelog 1.0)

Sections order: `Breaking Changes`, `Features`, `Bug Fixes`, `Performance`, `Deprecations`, `Removed`.
