"""Deal lookup functionality."""

from typing import Optional
from cli_saver_deals_agent.database import init_db, find_deal_by_package


def lookup_deal(package_name: str) -> Optional[dict]:
    """Look up a deal for a package name."""
    conn = init_db()
    deal = find_deal_by_package(conn, package_name)
    conn.close()
    return deal
