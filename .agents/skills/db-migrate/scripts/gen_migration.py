#!/usr/bin/env python3
"""
gen_migration.py — Generate database migration files
Usage: python3 gen_migration.py "<description>" [--format sql|alembic|prisma]
"""

import sys
import os
import re
import argparse
from pathlib import Path
from datetime import datetime


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s-]+", "_", text)
    return text[:60]


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d%H%M%S")


def detect_format() -> str:
    if Path("alembic.ini").exists():       return "alembic"
    if Path("prisma/schema.prisma").exists(): return "prisma"
    if Path("db/migrate").exists():        return "activerecord"
    return "sql"


# ── SQL (Flyway / plain) ───────────────────────────────────────────────────────

SQL_TEMPLATE = """\
-- Migration: {description}
-- Generated: {timestamp}
-- Format: SQL (up/down split by marker)

-- ============================================================
-- UP: Apply migration
-- ============================================================

BEGIN;

-- TODO: Replace with your actual migration SQL
-- Examples:

-- Add column (safe for existing rows — nullable or with default):
-- ALTER TABLE users ADD COLUMN email_verified BOOLEAN NOT NULL DEFAULT FALSE;

-- Create table:
-- CREATE TABLE IF NOT EXISTS orders (
--   id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
--   user_id     UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
--   status      VARCHAR(20) NOT NULL DEFAULT 'pending'
--                           CHECK (status IN ('pending','processing','shipped','delivered','cancelled')),
--   total_cents INTEGER     NOT NULL CHECK (total_cents >= 0),
--   created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
--   updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
-- );

-- Add index (CONCURRENTLY avoids locking — cannot be inside a transaction):
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_user_id ON orders(user_id);
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_status  ON orders(status);

COMMIT;

-- ============================================================
-- DOWN: Rollback migration
-- ============================================================

BEGIN;

-- TODO: Reverse the UP migration exactly
-- Example:
-- DROP TABLE IF EXISTS orders;
-- ALTER TABLE users DROP COLUMN IF EXISTS email_verified;

COMMIT;
"""

# ── Alembic (Python) ────────────────────────────────────────────────────────

ALEMBIC_TEMPLATE = '''\
"""
{description}

Revision ID: {revision_id}
Revises: <prev_revision>
Create Date: {timestamp}
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision    = '{revision_id}'
down_revision = None  # TODO: set previous revision ID
branch_labels = None
depends_on    = None


def upgrade() -> None:
    """Apply the migration."""
    # TODO: Replace with your actual migration

    # ── Add column example ──────────────────────────────────────────────────
    # op.add_column('users', sa.Column(
    #     'email_verified', sa.Boolean(), nullable=False, server_default='false'
    # ))

    # ── Create table example ────────────────────────────────────────────────
    # op.create_table('orders',
    #     sa.Column('id',          postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
    #     sa.Column('user_id',     postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    #     sa.Column('status',      sa.String(20),  nullable=False, server_default='pending'),
    #     sa.Column('total_cents', sa.Integer(),   nullable=False),
    #     sa.Column('created_at',  sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()'), nullable=False),
    #     sa.Column('updated_at',  sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()'), nullable=False),
    # )
    # op.create_index('idx_orders_user_id', 'orders', ['user_id'])
    # op.create_index('idx_orders_status',  'orders', ['status'])

    pass


def downgrade() -> None:
    """Reverse the migration."""
    # TODO: Exact reverse of upgrade()

    # op.drop_table('orders')
    # op.drop_column('users', 'email_verified')

    pass
'''

# ── Prisma (Node.js) — generates a schema addition note ─────────────────────

PRISMA_NOTE = """\
-- Prisma Migration: {description}
-- Generated: {timestamp}

-- NOTE: Prisma manages migrations via `prisma migrate dev`.
-- Update prisma/schema.prisma first, then run:
--   npx prisma migrate dev --name "{slug}"
--
-- Example schema changes to make in schema.prisma:

-- ADD FIELD TO EXISTING MODEL:
-- model User {{
--   // ... existing fields ...
--   emailVerified Boolean  @default(false)
--   verifiedAt    DateTime?
-- }}

-- NEW MODEL:
-- model Order {{
--   id         String   @id @default(uuid())
--   userId     String
--   user       User     @relation(fields: [userId], references: [id], onDelete: Cascade)
--   status     String   @default("pending")
--   totalCents Int
--   createdAt  DateTime @default(now())
--   updatedAt  DateTime @updatedAt
--
--   @@index([userId])
--   @@index([status])
-- }}

-- After updating schema.prisma, run:
--   npx prisma migrate dev --name "{slug}"
--   npx prisma generate
"""


def generate(description: str, fmt: str, output_dir: str):
    slug = slugify(description)
    ts   = timestamp()

    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)

    if fmt == "alembic":
        rev_id   = ts[:12]
        filename = f"{ts}__{slug}.py"
        content  = ALEMBIC_TEMPLATE.format(
            description=description, revision_id=rev_id, timestamp=ts, slug=slug
        )
    elif fmt == "prisma":
        filename = f"{ts}_{slug}.sql"
        content  = PRISMA_NOTE.format(description=description, timestamp=ts, slug=slug)
    else:  # sql / flyway
        filename = f"V{ts}__{slug}.sql"
        content  = SQL_TEMPLATE.format(description=description, timestamp=ts)

    output_path = output_dir_path / filename
    output_path.write_text(content)
    print(f"✅  Migration file → {output_path}")

    # Safety warnings
    desc_lower = description.lower()
    if any(w in desc_lower for w in ["drop", "delete", "truncate", "remove"]):
        print("⚠️  WARNING: Destructive operation detected — ensure DOWN migration is correct")
    if any(w in desc_lower for w in ["rename", "alter type", "change type"]):
        print("⚠️  WARNING: Renaming/type-change can break existing queries — test in staging first")
    if any(w in desc_lower for w in ["index", "idx"]):
        print("ℹ️  TIP: For large tables, use CREATE INDEX CONCURRENTLY (outside of transaction)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("description", nargs="+")
    parser.add_argument("--format", choices=["sql", "alembic", "prisma"], default=None)
    parser.add_argument("--output-dir", default="migrations")
    args = parser.parse_args()

    desc   = " ".join(args.description)
    fmt    = args.format or detect_format()
    outdir = args.output_dir

    if fmt == "alembic" and Path("versions").exists():
        outdir = "versions"
    elif fmt == "prisma" and Path("prisma/migrations").exists():
        outdir = "prisma/migrations"

    generate(desc, fmt, outdir)


if __name__ == "__main__":
    main()
