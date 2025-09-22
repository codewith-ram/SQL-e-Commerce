import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = BASE_DIR / "app" / "database" / "app.db"
DB_PATH = Path(os.getenv("DATABASE_PATH", str(DEFAULT_DB_PATH)))
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(seed: bool = True):
    """Initialize database schema and conditionally seed data.

    - On first run (no products table), execute the full schema script (DDL + seed).
    - On subsequent runs, do nothing (schema already exists). Optionally seed if table is empty.
    """
    conn = get_connection()
    try:
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
        has_products_table = cur.fetchone() is not None

        if not has_products_table:
            # First-time initialization: run the entire schema (DDL + seed inserts)
            with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
                schema_sql = f.read()
            conn.executescript(schema_sql)
            conn.commit()
        else:
            # Optional: if table exists but empty and seed requested, seed products from file
            if seed:
                cur = conn.execute("SELECT COUNT(1) AS c FROM products")
                count = cur.fetchone()["c"]
                if count == 0:
                    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
                        schema_sql = f.read()
                    # Extract only INSERT statements for products and run them
                    inserts = [line for line in schema_sql.splitlines() if line.strip().upper().startswith("INSERT INTO PRODUCTS")]
                    if inserts:
                        conn.executescript("\n".join(inserts))
                        conn.commit()
    finally:
        conn.close()
