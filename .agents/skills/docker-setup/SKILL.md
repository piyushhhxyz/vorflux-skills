---
name: docker-setup
description: This skill should be used when the user asks to dockerize an application, create a Dockerfile, add Docker Compose, containerize their project, set up Docker for development or production, or create container configuration. Trigger phrases include "dockerize this", "create a Dockerfile", "add Docker Compose", "containerize my app", "set up Docker", "create docker config", "add containers".
version: 1.0.0
license: MIT
allowed-tools:
  - read
  - write
  - bash
metadata:
  version: "1.0"
  tags: [docker, containers, devops, deployment]
---

# docker-setup — Production-Ready Docker Configuration

Generate optimized, security-hardened Dockerfiles and Docker Compose configs for Node.js, Python, Go, and other stacks. Used by best practices from Docker official docs, Google Cloud, and major OSS projects.

## How to use

```
/docker-setup [stack or directory]
```

Supported stacks: `node`, `python`, `go`, `rust`, `ruby`, `java`

## Instructions

### Step 1 — Detect the stack

Read the project root to detect:
- `package.json` → Node.js
- `requirements.txt` / `pyproject.toml` → Python
- `go.mod` → Go
- `Cargo.toml` → Rust
- `Gemfile` → Ruby

### Step 2 — Generate config files

Run the setup script:

```bash
bash ${SKILL_DIR}/scripts/setup_docker.sh [stack] [app_port]
```

This creates:
- `Dockerfile` — multi-stage, non-root user, minimal base image
- `docker-compose.yml` — app + common services (DB, Redis, etc.)
- `.dockerignore` — exclude build artifacts and secrets
- `docker-compose.override.yml` — development overrides with hot reload

### Step 3 — Verify

```bash
docker build -t app-test . && echo "✅ Build succeeded"
```

### Step 4 — Report

Show the user the generated files and key commands:
- `docker compose up -d` — start all services
- `docker compose logs -f app` — tail logs
- `docker compose exec app sh` — shell into container
