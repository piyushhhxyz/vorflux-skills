#!/usr/bin/env bash
# setup_docker.sh — Generate Docker config for a project
# Usage: setup_docker.sh [stack] [port]

set -euo pipefail

STACK="${1:-auto}"
PORT="${2:-3000}"
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

GREEN='\033[0;32m'; CYAN='\033[0;36m'; NC='\033[0m'

# ── Auto-detect stack ─────────────────────────────────────────────────────────
if [ "$STACK" = "auto" ]; then
  if [ -f "package.json" ];          then STACK="node"
  elif [ -f "requirements.txt" ] || [ -f "pyproject.toml" ]; then STACK="python"
  elif [ -f "go.mod" ];              then STACK="go"
  elif [ -f "Cargo.toml" ];          then STACK="rust"
  elif [ -f "Gemfile" ];             then STACK="ruby"
  else
    echo "Could not auto-detect stack. Pass it explicitly: setup_docker.sh node|python|go"
    exit 1
  fi
fi

echo -e "${CYAN}Detected stack: $STACK (port: $PORT)${NC}"

# ── .dockerignore ─────────────────────────────────────────────────────────────
cat > .dockerignore << 'EOF'
# Version control
.git
.gitignore

# Dependencies (reinstalled in container)
node_modules
__pycache__
*.pyc
.venv
venv
vendor

# Build artifacts
dist
build
.next
out
target

# Secrets & config
.env
.env.*
*.key
*.pem
secrets/

# Dev tools
.DS_Store
*.log
.idea
.vscode
coverage
.pytest_cache
.mypy_cache
EOF

echo -e "${GREEN}✅ .dockerignore${NC}"

# ── Stack-specific Dockerfile ──────────────────────────────────────────────────
generate_node_dockerfile() {
cat > Dockerfile << EOF
# syntax=docker/dockerfile:1
# ── Stage 1: deps ──────────────────────────────────────────────────────────────
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

# ── Stage 2: builder ───────────────────────────────────────────────────────────
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build 2>/dev/null || true

# ── Stage 3: runner ────────────────────────────────────────────────────────────
FROM node:20-alpine AS runner
WORKDIR /app

# Security: non-root user
RUN addgroup --system --gid 1001 nodejs && \\
    adduser  --system --uid 1001 appuser

COPY --from=deps    --chown=appuser:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=appuser:nodejs /app/dist         ./dist
COPY --from=builder --chown=appuser:nodejs /app/package.json ./

USER appuser
EXPOSE $PORT
ENV NODE_ENV=production PORT=$PORT

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \\
  CMD wget -qO- http://localhost:$PORT/health || exit 1

CMD ["node", "dist/index.js"]
EOF
}

generate_python_dockerfile() {
cat > Dockerfile << EOF
# syntax=docker/dockerfile:1
# ── Stage 1: builder ───────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder
WORKDIR /app

# Install build deps
RUN apt-get update && apt-get install -y --no-install-recommends \\
    build-essential gcc && rm -rf /var/lib/apt/lists/*

# Install Python deps into a virtual env
COPY requirements*.txt ./
RUN python -m venv /opt/venv && \\
    /opt/venv/bin/pip install --upgrade pip && \\
    /opt/venv/bin/pip install -r requirements.txt --no-cache-dir

# ── Stage 2: runner ────────────────────────────────────────────────────────────
FROM python:3.12-slim AS runner
WORKDIR /app

# Security: non-root user
RUN addgroup --system --gid 1001 appgroup && \\
    adduser  --system --uid 1001 appuser --ingroup appgroup

COPY --from=builder /opt/venv /opt/venv
COPY --chown=appuser:appgroup . .

ENV PATH="/opt/venv/bin:\$PATH" \\
    PYTHONDONTWRITEBYTECODE=1 \\
    PYTHONUNBUFFERED=1 \\
    PORT=$PORT

USER appuser
EXPOSE $PORT

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \\
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:$PORT/health')" || exit 1

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "$PORT"]
EOF
}

generate_go_dockerfile() {
  APP_NAME=$(basename "$(pwd)")
cat > Dockerfile << EOF
# syntax=docker/dockerfile:1
# ── Stage 1: builder ───────────────────────────────────────────────────────────
FROM golang:1.22-alpine AS builder
WORKDIR /app

RUN apk add --no-cache git ca-certificates

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 \\
    go build -ldflags="-w -s -extldflags '-static'" -o /app/server ./cmd/server

# ── Stage 2: runner (distroless for minimal attack surface) ───────────────────
FROM gcr.io/distroless/static-debian12 AS runner

COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=builder /app/server /server

EXPOSE $PORT
ENV PORT=$PORT

USER nonroot:nonroot

HEALTHCHECK --interval=30s --timeout=3s \\
  CMD ["/server", "-health"]

ENTRYPOINT ["/server"]
EOF
}

# ── Generate Dockerfile ────────────────────────────────────────────────────────
case "$STACK" in
  node)   generate_node_dockerfile   ;;
  python) generate_python_dockerfile ;;
  go)     generate_go_dockerfile     ;;
  *)      echo "Stack $STACK not yet supported. Using node as default."
          generate_node_dockerfile   ;;
esac

echo -e "${GREEN}✅ Dockerfile ($STACK)${NC}"

# ── docker-compose.yml ────────────────────────────────────────────────────────
cat > docker-compose.yml << EOF
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
      target: runner
    ports:
      - "\${PORT:-$PORT}:\${PORT:-$PORT}"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/appdb
      - REDIS_URL=redis://redis:6379
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - app-network

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: appdb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
    restart: unless-stopped
    networks:
      - app-network

volumes:
  postgres_data:
  redis_data:

networks:
  app-network:
    driver: bridge
EOF

echo -e "${GREEN}✅ docker-compose.yml${NC}"

# ── docker-compose.override.yml (dev) ─────────────────────────────────────────
cat > docker-compose.override.yml << EOF
# Development overrides — hot reload, debug ports, no health checks
services:
  app:
    build:
      target: builder
    volumes:
      - .:/app
      - /app/node_modules
    environment:
      - NODE_ENV=development
    command: npm run dev
    ports:
      - "9229:9229"   # Node.js debugger

  db:
    ports:
      - "5432:5432"   # expose for local DB clients

  redis:
    ports:
      - "6379:6379"
EOF

echo -e "${GREEN}✅ docker-compose.override.yml${NC}"
echo ""
echo -e "${CYAN}Quick start commands:${NC}"
echo "  docker compose up -d              # start all services"
echo "  docker compose logs -f app        # tail logs"
echo "  docker compose exec app sh        # shell into app container"
echo "  docker compose down -v            # stop and remove volumes"
