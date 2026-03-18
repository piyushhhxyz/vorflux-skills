---
name: db-migrate
description: This skill should be used when the user asks to create a database migration, generate SQL migration files, add a new column or table, modify the database schema, create an Alembic migration, write a Prisma migration, or manage database changes. Trigger phrases include "create a migration", "add a column to the database", "generate SQL migration", "create database migration", "add a table", "migrate the database", "schema migration".
version: 1.0.0
license: MIT
allowed-tools:
  - read
  - write
  - bash
metadata:
  version: "1.0"
  tags: [database, migrations, sql, alembic, prisma]
---

# db-migrate — Database Migration Generator

Generate safe, reversible database migrations for PostgreSQL, MySQL, and SQLite. Supports raw SQL, Alembic (Python), Prisma (Node.js), and Flyway formats.

## How to use

```
/db-migrate [description of change]
```

Examples:
- `/db-migrate add email_verified column to users table`
- `/db-migrate create orders table with foreign key to users`
- `/db-migrate add index on products.category_id`

## Instructions

### Step 1 — Detect migration system

Check for:
- `alembic.ini` → Alembic
- `prisma/schema.prisma` → Prisma
- `migrations/` folder → raw SQL or Flyway
- `db/migrate/` → Rails ActiveRecord

### Step 2 — Analyze current schema

Read existing migration files or schema file to understand current state.

### Step 3 — Generate migration

```bash
python3 ${SKILL_DIR}/scripts/gen_migration.py "$ARGUMENTS" [--format sql|alembic|prisma]
```

### Step 4 — Safety check

Every migration must have:
- An `up` (apply) operation
- A `down` (rollback) operation
- A transaction wrapper
- No destructive operations without explicit confirmation

### Step 5 — Report

Show the generated migration file. Warn about:
- Locking issues on large tables (add column on 10M+ row table)
- Data loss risk (DROP, ALTER with type change)
- Index creation best practice (`CREATE INDEX CONCURRENTLY`)
