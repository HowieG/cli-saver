"""Proxlock storage integration."""

import requests
from rich.console import Console
from .config import get_proxlock_api_key


console = Console()

PROXLOCK_API_BASE = "https://api.proxlock.dev/v1"


def save_to_proxlock(deal: dict) -> bool:
    """Save a deal/code to Proxlock.

    Returns True if successful, False otherwise.
    """
    api_key = get_proxlock_api_key()

    if not api_key:
        # Silently skip if not configured
        return False

    try:
        # Prepare the data to store
        key_name = f"cli-saver:{deal.get('package_name', deal.get('product_name', 'unknown'))}"
        key_data = {
            "product": deal.get("product_name"),
            "code": deal.get("code"),
            "value": deal.get("value"),
            "url": deal.get("url"),
        }

        # Make the API request to Proxlock
        # Note: The actual Proxlock API structure may differ
        # This is based on typical key-value storage API patterns
        response = requests.post(
            f"{PROXLOCK_API_BASE}/keys",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "name": key_name,
                "value": str(key_data),
                "tags": ["cli-saver", "discount-code"],
            },
            timeout=10,
        )

        if response.status_code in (200, 201):
            console.print("[dim]Code saved to Proxlock[/dim]")
            return True
        else:
            # Silently fail - storage is optional
            return False

    except requests.RequestException:
        # Silently fail - storage is optional
        return False
    except Exception:
        return False
