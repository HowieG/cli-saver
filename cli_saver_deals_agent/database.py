"""Database operations for deals storage."""

import sqlite3
from pathlib import Path
from typing import Optional


def get_db_path() -> Path:
    """Get the path to the deals database."""
    db_dir = Path.home() / ".cli-saver"
    db_dir.mkdir(exist_ok=True)
    return db_dir / "deals.db"


def init_db(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Initialize the database and create tables if needed."""
    if db_path is None:
        db_path = get_db_path()

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # Document-based schema: store original freetext
    conn.execute("""
        CREATE TABLE IF NOT EXISTS deals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            package_name TEXT,
            package_manager TEXT,
            raw_text TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_package_name
        ON deals(package_name)
    """)

    conn.commit()
    return conn


def clear_deals(conn: sqlite3.Connection) -> None:
    """Clear all deals from the database."""
    conn.execute("DELETE FROM deals")
    conn.commit()


def insert_deal(
    conn: sqlite3.Connection,
    product_name: str,
    raw_text: str,
    package_name: Optional[str] = None,
    package_manager: Optional[str] = None,
) -> int:
    """Insert a deal into the database. Returns the row ID."""
    cursor = conn.execute(
        """
        INSERT INTO deals (product_name, package_name, package_manager, raw_text)
        VALUES (?, ?, ?, ?)
        """,
        (product_name, package_name, package_manager, raw_text),
    )
    conn.commit()
    return cursor.lastrowid


def find_deal_by_package(conn: sqlite3.Connection, package_name: str) -> Optional[dict]:
    """Find a deal by package name. Returns None if not found."""
    # Normalize package name (remove extras like [tools])
    base_name = package_name.split("[")[0].strip().lower()

    cursor = conn.execute(
        "SELECT * FROM deals WHERE LOWER(package_name) = ?",
        (base_name,),
    )
    row = cursor.fetchone()
    return dict(row) if row else None


def get_all_deals(conn: sqlite3.Connection) -> list[dict]:
    """Get all deals from the database."""
    cursor = conn.execute("SELECT * FROM deals ORDER BY product_name")
    return [dict(row) for row in cursor.fetchall()]
