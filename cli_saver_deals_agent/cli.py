"""CLI for the deals agent."""

import click
from pathlib import Path
from rich.console import Console
from rich.table import Table

from .parser import parse_seed_file
from .database import init_db, clear_deals, insert_deal, get_all_deals


console = Console()


@click.group()
def main():
    """CLI Saver Deals Agent - Parse and manage discount code deals."""
    pass


@main.command()
@click.argument("seed_file", type=click.Path(exists=True))
@click.option("--clear", is_flag=True, help="Clear existing deals before parsing")
def parse(seed_file: str, clear: bool):
    """Parse a seed file and add deals to the database."""
    seed_path = Path(seed_file)
    content = seed_path.read_text()

    deals = parse_seed_file(content)

    conn = init_db()

    if clear:
        clear_deals(conn)
        console.print("[yellow]Cleared existing deals[/yellow]")

    added = 0
    for deal in deals:
        insert_deal(
            conn,
            product_name=deal.product_name,
            raw_text=deal.raw_text,
            package_name=deal.package_name,
            package_manager=deal.package_manager,
        )
        added += 1
        console.print(f"[green]Added:[/green] {deal.product_name}", end="")
        if deal.package_name:
            console.print(f" [dim]({deal.package_name})[/dim]", end="")
        console.print()

    conn.close()
    console.print(f"\n[bold green]Added {added} deals to database[/bold green]")


@main.command()
def list():
    """List all deals in the database."""
    from rich.panel import Panel

    conn = init_db()
    deals = get_all_deals(conn)
    conn.close()

    if not deals:
        console.print("[yellow]No deals in database. Run 'cli-saver-deals parse <seed_file>' first.[/yellow]")
        return

    console.print(f"\n[bold green]{len(deals)} deals in database[/bold green]\n")

    for deal in deals:
        title = f"[bold cyan]{deal['product_name']}[/bold cyan]"
        if deal["package_name"]:
            title += f" [dim]({deal['package_name']})[/dim]"

        panel = Panel(
            deal["raw_text"],
            title=title,
            border_style="green",
            padding=(1, 2),
        )
        console.print(panel)
        console.print()


@main.command()
def clear():
    """Clear all deals from the database."""
    conn = init_db()
    clear_deals(conn)
    conn.close()
    console.print("[green]Cleared all deals from database[/green]")


if __name__ == "__main__":
    main()
