-- ═══════════════════════════════════════════════════════════════════════════
-- Database Migration Patterns Reference
-- Copy-paste safe patterns for common schema changes (PostgreSQL)
-- ═══════════════════════════════════════════════════════════════════════════

-- ── 1. Add a nullable column (zero downtime) ─────────────────────────────────
ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR(20);

-- ── 2. Add NOT NULL column with default (zero downtime) ──────────────────────
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified BOOLEAN NOT NULL DEFAULT FALSE;

-- ── 3. Add NOT NULL column WITHOUT default (multi-step for large tables) ──────
-- Step 1: add as nullable
ALTER TABLE users ADD COLUMN profile_complete BOOLEAN;
-- Step 2: backfill (batch if table is large)
UPDATE users SET profile_complete = FALSE WHERE profile_complete IS NULL;
-- Step 3: add constraint
ALTER TABLE users ALTER COLUMN profile_complete SET NOT NULL;
ALTER TABLE users ALTER COLUMN profile_complete SET DEFAULT FALSE;

-- ── 4. Create table with best practices ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS orders (
  id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  status      VARCHAR(20) NOT NULL DEFAULT 'pending'
                          CONSTRAINT orders_status_check
                          CHECK (status IN ('pending','processing','shipped','delivered','cancelled')),
  total_cents INTEGER     NOT NULL CONSTRAINT orders_total_positive CHECK (total_cents >= 0),
  metadata    JSONB       NOT NULL DEFAULT '{}',
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── 5. Add indexes (use CONCURRENTLY on production — outside transaction) ─────
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_user_id   ON orders(user_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_status    ON orders(status);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_created   ON orders(created_at DESC);
-- Partial index for active orders only:
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_active
  ON orders(user_id) WHERE status NOT IN ('delivered', 'cancelled');

-- ── 6. Add updated_at trigger ─────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_orders_updated_at ON orders;
CREATE TRIGGER trg_orders_updated_at
  BEFORE UPDATE ON orders
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ── 7. Rename column (safe approach) ─────────────────────────────────────────
-- Add new column
ALTER TABLE users ADD COLUMN full_name VARCHAR(200);
-- Backfill
UPDATE users SET full_name = CONCAT(first_name, ' ', last_name);
-- Add NOT NULL once backfilled
ALTER TABLE users ALTER COLUMN full_name SET NOT NULL;
-- (after deploying code that uses full_name:)
-- ALTER TABLE users DROP COLUMN first_name;
-- ALTER TABLE users DROP COLUMN last_name;

-- ── 8. Add foreign key without locking ───────────────────────────────────────
-- Step 1: add NOT VALID (skips validation scan)
ALTER TABLE orders ADD CONSTRAINT fk_orders_users
  FOREIGN KEY (user_id) REFERENCES users(id) NOT VALID;
-- Step 2: validate asynchronously (SHARE UPDATE EXCLUSIVE, non-blocking)
ALTER TABLE orders VALIDATE CONSTRAINT fk_orders_users;

-- ── 9. Soft-delete pattern ────────────────────────────────────────────────────
ALTER TABLE users ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_active
  ON users(id) WHERE deleted_at IS NULL;

-- ── 10. JSONB column with GIN index ──────────────────────────────────────────
ALTER TABLE users ADD COLUMN IF NOT EXISTS preferences JSONB NOT NULL DEFAULT '{}';
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_preferences_gin
  ON users USING GIN (preferences);
