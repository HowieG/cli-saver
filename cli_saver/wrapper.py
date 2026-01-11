"""Package manager wrapper logic."""

import re
import subprocess
import sys
import shutil
from typing import Optional

from .lookup import lookup_deal
from .display import display_deal, prompt_for_payment, console
from .config import is_package_seen, mark_package_seen


def get_real_command(package_manager: str) -> Optional[str]:
    """Get the path to the real package manager command."""
    # We need to find the real command, not our alias
    # Use 'which -a' to find all instances and skip the first (our wrapper)
    result = subprocess.run(
        ["which", package_manager],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        path = result.stdout.strip()
        # Return the real binary path
        return path
    return shutil.which(package_manager)


def extract_packages_from_pip(args: list[str]) -> list[str]:
    """Extract package names from pip install command."""
    packages = []
    skip_next = False

    # Look for 'install' command
    if "install" not in args:
        return []

    install_idx = args.index("install")

    for i, arg in enumerate(args[install_idx + 1:], start=install_idx + 1):
        if skip_next:
            skip_next = False
            continue

        # Skip flags and their values
        if arg.startswith("-"):
            if arg in ("-r", "--requirement", "-e", "--editable", "-t", "--target", "-c", "--constraint"):
                skip_next = True
            continue

        # Skip if it looks like a path
        if "/" in arg or arg.endswith(".txt") or arg.endswith(".whl"):
            continue

        # Extract package name (remove version specifiers and extras)
        pkg_name = re.split(r'[\[<>=!~]', arg)[0]
        if pkg_name:
            packages.append(pkg_name.lower())

    return packages


def extract_packages_from_brew(args: list[str]) -> list[str]:
    """Extract package names from brew install command."""
    packages = []

    if "install" not in args:
        return []

    install_idx = args.index("install")

    for arg in args[install_idx + 1:]:
        # Skip flags
        if arg.startswith("-"):
            continue
        packages.append(arg.lower())

    return packages


def extract_packages_from_npm(args: list[str]) -> list[str]:
    """Extract package names from npm install command."""
    packages = []

    # npm uses 'install' or 'i'
    install_idx = None
    for i, arg in enumerate(args):
        if arg in ("install", "i", "add"):
            install_idx = i
            break

    if install_idx is None:
        return []

    for arg in args[install_idx + 1:]:
        # Skip flags
        if arg.startswith("-"):
            continue
        # Remove version specifier
        pkg_name = arg.split("@")[0]
        if pkg_name:
            packages.append(pkg_name.lower())

    return packages


def wrap_command(package_manager: str, args: list[str], dry_run: bool = False) -> int:
    """Wrap a package manager command and check for deals."""
    # Get the real command path
    real_cmd = get_real_command(package_manager)
    if not real_cmd:
        console.print(f"[red]Error: Could not find {package_manager}[/red]")
        return 1

    # Extract packages being installed
    if package_manager == "pip":
        packages = extract_packages_from_pip(args)
    elif package_manager == "brew":
        packages = extract_packages_from_brew(args)
    elif package_manager == "npm":
        packages = extract_packages_from_npm(args)
    else:
        packages = []

    if dry_run:
        console.print(f"[dim]Would run: {real_cmd} {' '.join(args)}[/dim]")
        console.print(f"[dim]Packages detected: {packages}[/dim]")

    # Run the actual command
    if not dry_run:
        result = subprocess.run([real_cmd] + args)
        exit_code = result.returncode

        # Only show deals if the command succeeded
        if exit_code != 0:
            return exit_code
    else:
        exit_code = 0

    # Check for deals for each package
    for package in packages:
        # Skip if we've already shown this deal
        if is_package_seen(package_manager, package):
            continue

        deal = lookup_deal(package)
        if deal:
            display_deal(deal)

            # Mark as seen
            mark_package_seen(package_manager, package)

            # Ask about payment
            if prompt_for_payment():
                try:
                    from .payments import process_payment
                    process_payment()
                except ImportError:
                    console.print("[yellow]Payment module not available. Install with: pip install cli-saver[payments][/yellow]")
                except Exception as e:
                    console.print(f"[yellow]Payment failed: {e}[/yellow]")

            # Try to save to Proxlock
            try:
                from .storage import save_to_proxlock
                save_to_proxlock(deal)
            except Exception:
                pass  # Silently ignore storage errors

    return exit_code
