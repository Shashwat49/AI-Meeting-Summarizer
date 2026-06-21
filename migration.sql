-- Run this once against your existing database before starting the app.
-- create_all() only creates missing tables, it does NOT alter existing
-- tables, so these 4 new columns must be added manually.

ALTER TABLE meetings ADD COLUMN IF NOT EXISTS participants JSONB;
ALTER TABLE meetings ADD COLUMN IF NOT EXISTS date_time VARCHAR;
ALTER TABLE meetings ADD COLUMN IF NOT EXISTS duration VARCHAR;
ALTER TABLE meetings ADD COLUMN IF NOT EXISTS sentiment VARCHAR;
