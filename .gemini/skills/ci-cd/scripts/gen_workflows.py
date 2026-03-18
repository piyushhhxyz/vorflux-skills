#!/usr/bin/env python3
"""
gen_workflows.py — Generate GitHub Actions workflow files
Usage: python3 gen_workflows.py [ci|cd|release|security|full]
"""

import sys
import os
import json
from pathlib import Path

WORKFLOWS_DIR = Path(".github/workflows")

CI_NODE = """\
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm run lint
      - run: npm run type-check 2>/dev/null || true

  test:
    name: Test (Node ${{ matrix.node-version }})
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [18, 20, 22]
      fail-fast: false
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: npm
      - run: npm ci
      - run: npm test -- --coverage --ci
      - uses: codecov/codecov-action@v4
        if: matrix.node-version == 20
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
          fail_ci_if_error: false

  build:
    name: Build
    runs-on: ubuntu-latest
    needs: [lint, test]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm run build
      - uses: actions/upload-artifact@v4
        with:
          name: build-${{ github.sha }}
          path: dist/
          retention-days: 7
"""

CI_PYTHON = """\
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint:
    name: Lint & Type Check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
      - run: pip install ruff mypy
      - run: ruff check .
      - run: mypy . --ignore-missing-imports 2>/dev/null || true

  test:
    name: Test (Python ${{ matrix.python-version }})
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
      fail-fast: false
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip
      - run: pip install -r requirements.txt
      - run: pip install pytest pytest-cov pytest-asyncio
      - run: pytest --cov=. --cov-report=xml -v
      - uses: codecov/codecov-action@v4
        if: matrix.python-version == '3.12'
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
"""

CI_GO = """\
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version-file: go.mod
          cache: true
      - uses: golangci/golangci-lint-action@v4
        with:
          version: latest

  test:
    name: Test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version-file: go.mod
          cache: true
      - run: go test ./... -race -coverprofile=coverage.txt -covermode=atomic
      - uses: codecov/codecov-action@v4
        with:
          token: ${{ secrets.CODECOV_TOKEN }}

  build:
    name: Build
    runs-on: ubuntu-latest
    needs: [lint, test]
    strategy:
      matrix:
        goos: [linux, darwin, windows]
        goarch: [amd64, arm64]
        exclude:
          - goos: windows
            goarch: arm64
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version-file: go.mod
          cache: true
      - run: |
          GOOS=${{ matrix.goos }} GOARCH=${{ matrix.goarch }} \\
          go build -ldflags="-w -s" -o dist/app-${{ matrix.goos }}-${{ matrix.goarch }} ./cmd/server
      - uses: actions/upload-artifact@v4
        with:
          name: dist-${{ matrix.goos }}-${{ matrix.goarch }}
          path: dist/
"""

CD_WORKFLOW = """\
name: Deploy

on:
  push:
    branches: [main]

concurrency:
  group: deploy-production
  cancel-in-progress: false   # never cancel an in-flight deploy

jobs:
  deploy:
    name: Deploy to Production
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://your-app.com
    steps:
      - uses: actions/checkout@v4

      - name: Build Docker image
        run: |
          docker build -t ${{ vars.IMAGE_NAME }}:${{ github.sha }} .
          docker tag ${{ vars.IMAGE_NAME }}:${{ github.sha }} ${{ vars.IMAGE_NAME }}:latest

      - name: Push to registry
        run: |
          echo "${{ secrets.REGISTRY_PASSWORD }}" | \\
            docker login ${{ vars.REGISTRY_URL }} -u ${{ vars.REGISTRY_USER }} --password-stdin
          docker push ${{ vars.IMAGE_NAME }}:${{ github.sha }}
          docker push ${{ vars.IMAGE_NAME }}:latest

      - name: Deploy via SSH
        uses: appleboy/ssh-action@v1
        with:
          host:     ${{ secrets.DEPLOY_HOST }}
          username: ${{ secrets.DEPLOY_USER }}
          key:      ${{ secrets.DEPLOY_SSH_KEY }}
          script: |
            docker pull ${{ vars.IMAGE_NAME }}:${{ github.sha }}
            docker compose -f /app/docker-compose.yml up -d --no-deps app
            docker image prune -f

      - name: Health check
        run: |
          sleep 15
          curl -f https://your-app.com/health || exit 1
          echo "✅ Deploy successful"

      - name: Notify on failure
        if: failure()
        uses: slackapi/slack-github-action@v1
        with:
          channel-id: ${{ secrets.SLACK_CHANNEL_ID }}
          slack-message: "🔴 Deploy FAILED: ${{ github.repository }} @ ${{ github.sha }}"
        env:
          SLACK_BOT_TOKEN: ${{ secrets.SLACK_BOT_TOKEN }}
"""

RELEASE_WORKFLOW = """\
name: Release

on:
  push:
    tags:
      - 'v[0-9]+.[0-9]+.[0-9]+'

permissions:
  contents: write
  packages: write

jobs:
  release:
    name: Create Release
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0   # full history for changelog

      - name: Generate changelog
        id: changelog
        uses: orhun/git-cliff-action@v3
        with:
          config: cliff.toml
          args: --verbose --latest
        env:
          OUTPUT: RELEASE_NOTES.md

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          body_path: RELEASE_NOTES.md
          draft: false
          prerelease: ${{ contains(github.ref, '-rc') || contains(github.ref, '-beta') }}
          generate_release_notes: false
          files: |
            dist/**

      - name: Publish to npm
        if: startsWith(github.ref, 'refs/tags/v')
        run: |
          npm ci
          npm publish --access public
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}

      - name: Update CHANGELOG.md
        run: |
          git cliff --output CHANGELOG.md
          git config user.name  "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add CHANGELOG.md
          git commit -m "chore(release): update CHANGELOG for ${{ github.ref_name }}" || true
          git push origin HEAD:main || true
"""

SECURITY_WORKFLOW = """\
name: Security

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 6 * * 1'   # Weekly on Monday at 06:00 UTC

permissions:
  security-events: write
  contents: read

jobs:
  dependency-audit:
    name: Dependency Audit
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: npm audit
        run: npm audit --audit-level=high
        continue-on-error: false

  codeql:
    name: CodeQL SAST
    runs-on: ubuntu-latest
    strategy:
      matrix:
        language: [javascript, typescript]   # adjust for your stack
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with:
          languages: ${{ matrix.language }}
          queries: security-extended
      - uses: github/codeql-action/autobuild@v3
      - uses: github/codeql-action/analyze@v3
        with:
          category: "/language:${{ matrix.language }}"

  secret-scan:
    name: Secret Scanning
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  container-scan:
    name: Container Scan
    runs-on: ubuntu-latest
    if: hashFiles('Dockerfile') != ''
    steps:
      - uses: actions/checkout@v4
      - name: Build image for scanning
        run: docker build -t scan-target:latest .
      - uses: aquasecurity/trivy-action@master
        with:
          image-ref: scan-target:latest
          format: sarif
          output: trivy-results.sarif
          severity: CRITICAL,HIGH
          exit-code: '1'
      - uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: trivy-results.sarif
"""


def detect_stack() -> str:
    if Path("package.json").exists():  return "node"
    if Path("requirements.txt").exists() or Path("pyproject.toml").exists(): return "python"
    if Path("go.mod").exists():        return "go"
    if Path("Cargo.toml").exists():    return "rust"
    return "node"


def write_workflow(filename: str, content: str):
    WORKFLOWS_DIR.mkdir(parents=True, exist_ok=True)
    path = WORKFLOWS_DIR / filename
    path.write_text(content)
    print(f"✅  {path}")


def main():
    wf_type = (sys.argv[1] if len(sys.argv) > 1 else "ci").lower()
    stack   = detect_stack()

    print(f"Detected stack: {stack} | Generating: {wf_type}")
    print()

    ci_content = {"node": CI_NODE, "python": CI_PYTHON, "go": CI_GO}.get(stack, CI_NODE)

    if wf_type in ("ci", "full"):
        write_workflow("ci.yml", ci_content)

    if wf_type in ("cd", "full"):
        write_workflow("cd.yml", CD_WORKFLOW)

    if wf_type in ("release", "full"):
        write_workflow("release.yml", RELEASE_WORKFLOW)

    if wf_type in ("security", "full"):
        write_workflow("security.yml", SECURITY_WORKFLOW)

    print()
    print("Required GitHub Secrets (Settings → Secrets and variables → Actions):")
    if wf_type in ("cd", "full"):
        print("  DEPLOY_HOST, DEPLOY_USER, DEPLOY_SSH_KEY")
        print("  REGISTRY_PASSWORD")
        print("  SLACK_BOT_TOKEN, SLACK_CHANNEL_ID (optional)")
    if wf_type in ("release", "full"):
        print("  NPM_TOKEN (if publishing to npm)")
    if wf_type in ("security", "full"):
        print("  (none required — uses GITHUB_TOKEN)")
    print("  CODECOV_TOKEN (optional — for coverage reporting)")


if __name__ == "__main__":
    main()
