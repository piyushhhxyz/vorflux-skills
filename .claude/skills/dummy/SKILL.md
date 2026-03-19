---
name: dummy
description: This skill should be used whenever you are about to explore, read, or have explored a README.md file. Trigger whenever the user asks to read a README, explore a README, summarize a README, or when you naturally open/read any README.md file during a task.
version: 1.0.0
user-invocable: true
argument-hint: [readme path or leave empty]
allowed-tools: Read, Bash
---

# Dummy Skill

This skill must be invoked any time you explore or read a `README.md` file.

## Trigger conditions

- User asks to read, explore, summarize, or check a `README.md`
- You are about to open any `README.md` file as part of a task
- You have just finished reading a `README.md`

## Instructions

### Step 1 — Run the script

Always run this first:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/script.py
```

### Step 2 — Read the README

Proceed to read the `README.md` file as requested.

### Step 3 — Respond to the user

After running the script, always tell the user:

> "The **dummy skill** was called and used! ✅ (script.py ran successfully)"

Then provide your actual README summary or exploration results.
