---
name: api-docs
description: This skill should be used when the user asks to generate API documentation, create an OpenAPI spec, document REST endpoints, generate Swagger docs, create API reference docs, or document their HTTP API. Trigger phrases include "generate API docs", "create OpenAPI spec", "document my API", "generate Swagger", "create API reference", "document endpoints", "add API documentation".
version: 1.0.0
license: MIT
allowed-tools:
  - read
  - write
  - bash
metadata:
  version: "1.0"
  tags: [api, openapi, swagger, documentation]
---

# api-docs — OpenAPI 3.1 Documentation Generator

Analyze route files and generate a complete OpenAPI 3.1 spec + beautiful HTML docs. Supports Express, FastAPI, Flask, Gin, and more.

## How to use

```
/api-docs [routes file or directory]
```

## Instructions

### Step 1 — Scan routes

Read all route/controller files. Identify:
- HTTP method + path
- Request params, query, body schema
- Response schema and status codes
- Auth requirements

### Step 2 — Generate OpenAPI spec

```bash
python3 ${SKILL_DIR}/scripts/gen_openapi.py [routes_dir] openapi.yaml
```

### Step 3 — Generate HTML docs

```bash
python3 ${SKILL_DIR}/scripts/gen_html_docs.py openapi.yaml api-docs.html
```

### Step 4 — Report

Tell the user the generated files. Offer to:
- Add auth schemes (Bearer, API key, OAuth2)
- Add more example responses
- Generate Postman collection
- Host on GitHub Pages
