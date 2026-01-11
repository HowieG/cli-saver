"""Parser for seed files containing deals."""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class Deal:
    """Represents a parsed deal - document-based with raw text."""
    product_name: str
    raw_text: str
    package_name: Optional[str] = None
    package_manager: Optional[str] = None


# Known product to package mappings
PRODUCT_TO_PACKAGE = {
    "crewai": {"package": "crewai", "manager": "pip"},
    "apify": {"package": "apify", "manager": "pip"},
    "openai": {"package": "openai", "manager": "pip"},
    "proxlock": {"package": "proxlock", "manager": "pip"},
    "nevermined": {"package": "nevermined-payments", "manager": "pip"},
    "minimax": {"package": "minimax", "manager": "pip"},
}

# Known product names to look for
KNOWN_PRODUCTS = [
    "Nevermined",
    "CrewAI",
    "AI-Native IDE",
    "Rilo",
    "OpenAI",
    "ProxLock",
    "Proxlock",
    "Kalibr Intelligence",
    "Apify",
    "Minimax",
    "FlipECommerce",
]


def clean_line(line: str) -> str:
    """Remove unicode control characters and invisible chars from a line."""
    # Remove common invisible/control characters
    cleaned = re.sub(r'[\u200b\u200c\u200d\ufeff\u00a0]', '', line)
    # Remove leading non-printable chars but keep alphanumeric start
    cleaned = re.sub(r'^[^\x20-\x7e]+', '', cleaned)
    return cleaned.strip()


def parse_seed_file(content: str) -> list[Deal]:
    """Parse a seed file and extract deals as documents with raw text."""
    deals = []
    lines = content.split('\n')

    current_product = None
    current_section_raw = []  # Original lines (just cleaned of control chars)

    for line in lines:
        cleaned = clean_line(line)

        # Check if this line is a known product name
        is_product_line = False
        for product in KNOWN_PRODUCTS:
            if cleaned.lower() == product.lower():
                is_product_line = True
                # Save previous section
                if current_product and current_section_raw:
                    raw_text = '\n'.join(current_section_raw).strip()
                    if raw_text:
                        deal = create_deal(current_product, raw_text)
                        deals.append(deal)
                current_product = product
                current_section_raw = []
                break

        if not is_product_line and current_product:
            current_section_raw.append(cleaned)

    # Don't forget the last section
    if current_product and current_section_raw:
        raw_text = '\n'.join(current_section_raw).strip()
        if raw_text:
            deal = create_deal(current_product, raw_text)
            deals.append(deal)

    return deals


def create_deal(product_name: str, raw_text: str) -> Deal:
    """Create a deal with package mapping lookup."""
    product_key = product_name.lower().replace(' ', '').replace('-', '')
    package_info = PRODUCT_TO_PACKAGE.get(product_key, {})

    return Deal(
        product_name=product_name,
        raw_text=raw_text,
        package_name=package_info.get("package"),
        package_manager=package_info.get("manager"),
    )
