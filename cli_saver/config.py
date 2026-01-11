"""Configuration management for cli-saver."""

import json
from pathlib import Path
from typing import Optional


def get_config_dir() -> Path:
    """Get the configuration directory."""
    config_dir = Path.home() / ".cli-saver"
    config_dir.mkdir(exist_ok=True)
    return config_dir


def get_config_path() -> Path:
    """Get the path to the config file."""
    return get_config_dir() / "config.json"


def get_installed_path() -> Path:
    """Get the path to the installed packages tracking file."""
    return get_config_dir() / "installed.json"


def load_config() -> dict:
    """Load configuration from disk."""
    config_path = get_config_path()
    if config_path.exists():
        return json.loads(config_path.read_text())
    return {}


def save_config(config: dict) -> None:
    """Save configuration to disk."""
    config_path = get_config_path()
    config_path.write_text(json.dumps(config, indent=2))


def get_nevermined_api_key() -> Optional[str]:
    """Get the Nevermined API key from config."""
    return load_config().get("nevermined_api_key")


def get_proxlock_api_key() -> Optional[str]:
    """Get the Proxlock API key from config."""
    return load_config().get("proxlock_api_key")


def set_nevermined_api_key(api_key: str) -> None:
    """Set the Nevermined API key."""
    config = load_config()
    config["nevermined_api_key"] = api_key
    save_config(config)


def set_proxlock_api_key(api_key: str) -> None:
    """Set the Proxlock API key."""
    config = load_config()
    config["proxlock_api_key"] = api_key
    save_config(config)


def load_installed() -> dict:
    """Load the set of installed packages we've already shown deals for."""
    installed_path = get_installed_path()
    if installed_path.exists():
        return json.loads(installed_path.read_text())
    return {"pip": [], "brew": [], "npm": []}


def save_installed(installed: dict) -> None:
    """Save the installed packages tracking."""
    installed_path = get_installed_path()
    installed_path.write_text(json.dumps(installed, indent=2))


def mark_package_seen(package_manager: str, package_name: str) -> None:
    """Mark a package as seen (we've shown the deal for it)."""
    installed = load_installed()
    if package_manager not in installed:
        installed[package_manager] = []
    if package_name not in installed[package_manager]:
        installed[package_manager].append(package_name)
        save_installed(installed)


def is_package_seen(package_manager: str, package_name: str) -> bool:
    """Check if we've already shown a deal for this package."""
    installed = load_installed()
    return package_name in installed.get(package_manager, [])
