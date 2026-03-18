#!/usr/bin/env python3
"""
analyze_project.py — Extract project metadata for README generation
Usage: python3 analyze_project.py [directory]
Outputs JSON to stdout that the AI uses to fill the README template.
"""

import sys
import os
import json
import re
from pathlib import Path


def read_safe(path) -> str:
    try:
        return Path(path).read_text(errors="ignore")
    except Exception:
        return ""


def detect_stack(root: Path) -> dict:
    result = {"language": "unknown", "framework": "unknown",
              "runtime": "unknown", "test_runner": "unknown", "package_manager": "npm"}

    if (root / "package.json").exists():
        pkg = json.loads(read_safe(root / "package.json") or "{}")
        deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
        result["language"] = "TypeScript" if (root / "tsconfig.json").exists() else "JavaScript"
        result["runtime"]  = f"Node.js {pkg.get('engines', {}).get('node', '18+')}"
        result["name"]     = pkg.get("name", root.name)
        result["version"]  = pkg.get("version", "0.1.0")
        result["description"] = pkg.get("description", "")
        result["scripts"]  = list(pkg.get("scripts", {}).keys())
        result["package_manager"] = "pnpm" if (root / "pnpm-lock.yaml").exists() else \
                                    "yarn"  if (root / "yarn.lock").exists() else "npm"
        # Framework detection
        if "next" in deps:          result["framework"] = "Next.js"
        elif "react" in deps:       result["framework"] = "React"
        elif "vue" in deps:         result["framework"] = "Vue.js"
        elif "fastify" in deps:     result["framework"] = "Fastify"
        elif "express" in deps:     result["framework"] = "Express"
        elif "@nestjs/core" in deps: result["framework"] = "NestJS"
        # Test runner
        if "jest" in deps:     result["test_runner"] = "jest"
        elif "vitest" in deps: result["test_runner"] = "vitest"

    elif (root / "pyproject.toml").exists() or (root / "requirements.txt").exists():
        result["language"] = "Python"
        result["package_manager"] = "pip"
        if (root / "pyproject.toml").exists():
            content = read_safe(root / "pyproject.toml")
            m = re.search(r'name\s*=\s*"([^"]+)"', content)
            result["name"] = m.group(1) if m else root.name
            m = re.search(r'version\s*=\s*"([^"]+)"', content)
            result["version"] = m.group(1) if m else "0.1.0"
            if "fastapi" in content.lower():  result["framework"] = "FastAPI"
            elif "django" in content.lower(): result["framework"] = "Django"
            elif "flask" in content.lower():  result["framework"] = "Flask"
        result["test_runner"] = "pytest"

    elif (root / "go.mod").exists():
        result["language"] = "Go"
        result["package_manager"] = "go modules"
        content = read_safe(root / "go.mod")
        m = re.search(r"^module (.+)$", content, re.MULTILINE)
        result["name"] = Path(m.group(1)).name if m else root.name
        m = re.search(r"^go (.+)$", content, re.MULTILINE)
        result["runtime"] = f"Go {m.group(1).strip()}" if m else "Go 1.21+"
        result["test_runner"] = "go test"

    elif (root / "Cargo.toml").exists():
        result["language"] = "Rust"
        result["package_manager"] = "cargo"
        content = read_safe(root / "Cargo.toml")
        m = re.search(r'^name\s*=\s*"([^"]+)"', content, re.MULTILINE)
        result["name"] = m.group(1) if m else root.name
        result["test_runner"] = "cargo test"

    else:
        result["name"] = root.name

    return result


def extract_env_vars(root: Path) -> list:
    """Find environment variables from .env.example or source files."""
    vars_found = {}

    # Check .env.example / .env.sample
    for env_file in [".env.example", ".env.sample", ".env.template"]:
        content = read_safe(root / env_file)
        if content:
            for line in content.splitlines():
                m = re.match(r"^([A-Z_][A-Z0-9_]*)\s*=\s*(.*)", line)
                if m:
                    key, default = m.group(1), m.group(2).strip()
                    vars_found[key] = {
                        "key": key,
                        "required": not bool(default),
                        "default": default or None,
                        "description": f"TODO: describe {key}"
                    }

    # Scan source files for common patterns
    for ext in ("*.py", "*.js", "*.ts", "*.go"):
        for f in list(root.rglob(ext))[:30]:
            if "node_modules" in str(f) or ".git" in str(f):
                continue
            content = read_safe(f)
            for m in re.finditer(r'(?:os\.environ\.get|process\.env|os\.Getenv)\(["\']([A-Z_][A-Z0-9_]*)', content):
                key = m.group(1)
                if key not in vars_found:
                    vars_found[key] = {"key": key, "required": True, "default": None,
                                       "description": f"TODO: describe {key}"}

    return list(vars_found.values())[:20]


def detect_ports(root: Path) -> list:
    ports = set()
    for f in list(root.rglob("*.py"))[:20] + list(root.rglob("*.js"))[:20] + \
             list(root.rglob("*.ts"))[:20]:
        if "node_modules" in str(f):
            continue
        content = read_safe(f)
        for m in re.finditer(r'(?:PORT|port)[^\d]*(\d{4,5})', content):
            p = int(m.group(1))
            if 1000 < p < 65535:
                ports.add(p)
    return sorted(ports)[:5]


def get_ci_badges(root: Path, repo_url: str = "") -> list:
    badges = []
    if (root / ".github" / "workflows").exists():
        badges.append({"label": "CI", "type": "github-actions"})
    return badges


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    stack = detect_stack(root)
    env_vars = extract_env_vars(root)
    ports    = detect_ports(root)

    # Find existing docs
    has_license      = (root / "LICENSE").exists() or (root / "LICENSE.md").exists()
    has_contributing = (root / "CONTRIBUTING.md").exists()
    has_changelog    = (root / "CHANGELOG.md").exists()
    has_docker       = (root / "Dockerfile").exists() or (root / "docker-compose.yml").exists()

    # List source directories
    src_dirs = [d.name for d in root.iterdir()
                if d.is_dir() and d.name not in
                (".git", "node_modules", "__pycache__", ".venv", "dist", "build", ".next")][:8]

    output = {
        "name":            stack.get("name", root.name),
        "version":         stack.get("version", "0.1.0"),
        "description":     stack.get("description", ""),
        "language":        stack["language"],
        "framework":       stack["framework"],
        "runtime":         stack["runtime"],
        "package_manager": stack["package_manager"],
        "test_runner":     stack["test_runner"],
        "scripts":         stack.get("scripts", []),
        "env_vars":        env_vars,
        "ports":           ports,
        "src_dirs":        src_dirs,
        "has_license":     has_license,
        "has_contributing": has_contributing,
        "has_changelog":   has_changelog,
        "has_docker":      has_docker,
        "ci_badges":       get_ci_badges(root),
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
