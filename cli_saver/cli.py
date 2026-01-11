"""Main CLI for cli-saver."""

import sys
import click
from rich.console import Console

from .wrapper import wrap_command
from .config import (
    set_nevermined_api_key,
    set_proxlock_api_key,
    get_nevermined_api_key,
    get_proxlock_api_key,
)


console = Console()


@click.group()
def main():
    """CLI Saver - Find discount codes when installing packages."""
    pass


@main.command()
@click.argument("package_manager", type=click.Choice(["pip", "brew", "npm"]))
@click.argument("args", nargs=-1)
@click.option("--dry-run", is_flag=True, help="Don't execute the command, just show what would happen")
def wrap(package_manager: str, args: tuple, dry_run: bool):
    """Wrap a package manager command and check for deals."""
    exit_code = wrap_command(package_manager, list(args), dry_run=dry_run)
    sys.exit(exit_code)


@main.command()
def setup():
    """Set up cli-saver with API keys."""
    console.print("[bold]CLI Saver Setup[/bold]\n")

    # Nevermined
    console.print("[cyan]Nevermined Integration (optional)[/cyan]")
    console.print("This allows you to tip cli-saver when we find a discount code.")
    console.print("Get your API key from: https://app.nevermined.io\n")

    current_nvm = get_nevermined_api_key()
    if current_nvm:
        console.print(f"[dim]Current key: {current_nvm[:8]}...{current_nvm[-4:]}[/dim]")

    nvm_key = click.prompt("Nevermined API Key (press Enter to skip)", default="", show_default=False)
    if nvm_key:
        set_nevermined_api_key(nvm_key)
        console.print("[green]Nevermined API key saved![/green]\n")

    # Proxlock
    console.print("[cyan]Proxlock Integration (optional)[/cyan]")
    console.print("This saves found discount codes securely to Proxlock.")
    console.print("Get your API key from: https://app.proxlock.dev\n")

    current_pl = get_proxlock_api_key()
    if current_pl:
        console.print(f"[dim]Current key: {current_pl[:8]}...{current_pl[-4:]}[/dim]")

    pl_key = click.prompt("Proxlock API Key (press Enter to skip)", default="", show_default=False)
    if pl_key:
        set_proxlock_api_key(pl_key)
        console.print("[green]Proxlock API key saved![/green]\n")

    console.print("[bold green]Setup complete![/bold green]")


@main.command("shell-init")
@click.option("--shell", type=click.Choice(["bash", "zsh", "fish"]), default=None, help="Shell type")
def shell_init(shell: str):
    """Output shell configuration to set up aliases."""
    import os

    if shell is None:
        # Try to detect shell
        shell_path = os.environ.get("SHELL", "/bin/bash")
        if "zsh" in shell_path:
            shell = "zsh"
        elif "fish" in shell_path:
            shell = "fish"
        else:
            shell = "bash"

    if shell == "fish":
        config = """
# CLI Saver aliases
function pip
    cli-saver wrap pip $argv
end

function brew
    cli-saver wrap brew $argv
end

function npm
    cli-saver wrap npm $argv
end
"""
    else:
        config = """
# CLI Saver aliases
pip() { cli-saver wrap pip "$@"; }
brew() { cli-saver wrap brew "$@"; }
npm() { cli-saver wrap npm "$@"; }
"""

    click.echo(config)


@main.command()
def status():
    """Show current configuration status."""
    nvm_key = get_nevermined_api_key()
    pl_key = get_proxlock_api_key()

    console.print("[bold]CLI Saver Status[/bold]\n")

    if nvm_key:
        console.print(f"[green]✓[/green] Nevermined: Configured ({nvm_key[:8]}...)")
    else:
        console.print("[yellow]○[/yellow] Nevermined: Not configured")

    if pl_key:
        console.print(f"[green]✓[/green] Proxlock: Configured ({pl_key[:8]}...)")
    else:
        console.print("[yellow]○[/yellow] Proxlock: Not configured")

    console.print("\nRun [cyan]cli-saver setup[/cyan] to configure integrations.")
    console.print("Run [cyan]source <(cli-saver shell-init)[/cyan] to enable package manager wrapping.")


if __name__ == "__main__":
    main()
