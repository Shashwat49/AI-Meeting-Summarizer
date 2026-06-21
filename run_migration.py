"""
Runs migration.sql against your database using the DATABASE_URL from .env.
No need for psql to be installed — this uses the same SQLAlchemy engine
the app already depends on.

Usage:
    python run_migration.py
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in .env file")

MIGRATION_FILE = os.path.join(os.path.dirname(__file__), "migration.sql")

with open(MIGRATION_FILE, "r") as f:
    sql_script = f.read()

engine = create_engine(DATABASE_URL)

# Split on semicolons so each ALTER TABLE statement runs separately
statements = [s.strip() for s in sql_script.split(";") if s.strip() and not s.strip().startswith("--")]

with engine.connect() as conn:
    for statement in statements:
        print(f"Running: {statement}")
        conn.execute(text(statement))
    conn.commit()

print("\nMigration completed successfully.")