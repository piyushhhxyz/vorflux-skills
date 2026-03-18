#!/usr/bin/env python3
"""
gen_openapi.py — Generate OpenAPI 3.1 spec from route analysis
Usage: python3 gen_openapi.py <routes_dir_or_file> <output.yaml>

This script provides the skeleton + helpers. The AI agent fills in
the actual endpoint details after reading the route files.
"""

import sys
import os
import re
import json
from pathlib import Path
from datetime import date

try:
    import yaml
except ImportError:
    os.system("pip install pyyaml -q")
    import yaml


# ── Route pattern detectors ────────────────────────────────────────────────────

PATTERNS = {
    "express": [
        (r'(?:router|app)\.(get|post|put|patch|delete)\s*\(\s*[\'"]([^\'"]+)[\'"]', "js"),
    ],
    "fastapi": [
        (r'@(?:app|router)\.(get|post|put|patch|delete)\s*\(\s*[\'"]([^\'"]+)[\'"]', "py"),
    ],
    "flask": [
        (r"@(?:app|bp)\.route\s*\(\s*['\"]([^'\"]+)['\"].*methods=\[([^\]]+)\]", "py"),
    ],
    "gin": [
        (r'(?:r|router|v1|api)\.(GET|POST|PUT|PATCH|DELETE)\s*\(\s*"([^"]+)"', "go"),
    ],
}


def detect_framework(source: str, ext: str) -> str:
    if ext in (".js", ".ts"):
        if "fastify" in source: return "fastify"
        if "express" in source or "router" in source: return "express"
    if ext == ".py":
        if "fastapi" in source.lower(): return "fastapi"
        if "flask" in source.lower(): return "flask"
    if ext == ".go":
        if "gin" in source.lower(): return "gin"
    return "unknown"


def extract_routes(filepath: str):
    source = Path(filepath).read_text(errors="ignore")
    ext    = Path(filepath).suffix.lower()
    routes = []

    for framework, pats in PATTERNS.items():
        for pattern, lang_ext in pats:
            if ext.lstrip(".") != lang_ext:
                continue
            for m in re.finditer(pattern, source, re.IGNORECASE):
                method = m.group(1).upper()
                path   = m.group(2)
                # Convert Express :param → OpenAPI {param}
                path = re.sub(r":(\w+)", r"{\1}", path)
                routes.append({"method": method, "path": path,
                                "framework": framework, "file": filepath})

    return routes


def route_to_operation(route: dict, index: int) -> dict:
    """Generate a basic OpenAPI operation object for a route."""
    path    = route["path"]
    method  = route["method"]
    params  = re.findall(r"\{(\w+)\}", path)
    op_id   = f"{method.lower()}_{path.replace('/', '_').strip('_')}_{index}"

    operation = {
        "operationId": op_id,
        "summary":     f"{method} {path}",
        "tags":        [path.split("/")[1] if "/" in path else "default"],
        "parameters":  [
            {
                "name": p, "in": "path", "required": True,
                "schema": {"type": "string"},
                "description": f"The {p} identifier"
            }
            for p in params
        ],
        "responses": {
            "200": {
                "description": "Successful response",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/SuccessResponse"}
                    }
                }
            },
            "400": {"description": "Bad request"},
            "401": {"description": "Unauthorized"},
            "404": {"description": "Not found"},
            "500": {"description": "Internal server error"},
        }
    }

    if method in ("POST", "PUT", "PATCH"):
        operation["requestBody"] = {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/RequestBody"}
                }
            }
        }

    return operation


def build_openapi_spec(routes: list, title: str, version: str) -> dict:
    paths = {}
    for i, route in enumerate(routes):
        path   = route["path"]
        method = route["method"].lower()
        if path not in paths:
            paths[path] = {}
        paths[path][method] = route_to_operation(route, i)

    return {
        "openapi": "3.1.0",
        "info": {
            "title":       title,
            "version":     version,
            "description": f"API documentation generated on {date.today().isoformat()}",
            "contact":     {"name": "API Support", "email": "api@example.com"},
            "license":     {"name": "MIT"},
        },
        "servers": [
            {"url": "https://api.example.com/v1", "description": "Production"},
            {"url": "http://localhost:3000",       "description": "Local dev"},
        ],
        "security": [{"BearerAuth": []}],
        "paths": paths,
        "components": {
            "securitySchemes": {
                "BearerAuth": {
                    "type":   "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                }
            },
            "schemas": {
                "SuccessResponse": {
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean", "example": True},
                        "data":    {"type": "object"},
                        "message": {"type": "string"},
                    }
                },
                "RequestBody": {
                    "type":       "object",
                    "description": "Request payload — fill in specific properties",
                    "additionalProperties": True,
                },
                "ErrorResponse": {
                    "type": "object",
                    "properties": {
                        "error":   {"type": "string"},
                        "message": {"type": "string"},
                        "code":    {"type": "integer"},
                    }
                }
            }
        },
        "tags": list({
            {"name": r["path"].split("/")[1] if "/" in r["path"] else "default"}
            for r in routes
        })
    }


def main():
    if len(sys.argv) < 3:
        print("Usage: gen_openapi.py <routes_dir_or_file> <output.yaml>")
        sys.exit(1)

    target  = sys.argv[1]
    output  = sys.argv[2]
    title   = Path(os.getcwd()).name.title() + " API"
    version = "1.0.0"

    all_routes = []

    if os.path.isfile(target):
        all_routes = extract_routes(target)
    else:
        for ext in ("*.js", "*.ts", "*.py", "*.go"):
            for f in Path(target).rglob(ext):
                if "test" not in str(f) and "node_modules" not in str(f):
                    all_routes.extend(extract_routes(str(f)))

    if not all_routes:
        print("No routes detected — generating skeleton spec.")
        all_routes = [
            {"method": "GET",    "path": "/items",      "framework": "express", "file": ""},
            {"method": "POST",   "path": "/items",      "framework": "express", "file": ""},
            {"method": "GET",    "path": "/items/{id}", "framework": "express", "file": ""},
            {"method": "PUT",    "path": "/items/{id}", "framework": "express", "file": ""},
            {"method": "DELETE", "path": "/items/{id}", "framework": "express", "file": ""},
        ]

    spec = build_openapi_spec(all_routes, title, version)

    with open(output, "w") as f:
        yaml.dump(spec, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print(f"✅  OpenAPI spec → {output}  ({len(all_routes)} endpoints)")
    print(f"   Validate at: https://editor.swagger.io  (paste the YAML)")


if __name__ == "__main__":
    main()
