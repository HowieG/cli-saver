"""Display formatting for deals."""

from rich.console import Console
from rich.panel import Panel


console = Console()


def display_deal(deal: dict) -> None:
    """Display a deal in a nice format - shows original freetext."""
    product_name = deal.get("product_name", "Unknown")
    raw_text = deal.get("raw_text", "")

    # Create a panel with the raw text
    panel = Panel(
        raw_text,
        title=f"[bold cyan]Found deal for {product_name}![/bold cyan]",
        border_style="green",
        padding=(1, 2),
    )

    console.print()
    console.print(panel)
    console.print()


def prompt_for_payment() -> bool:
    """Prompt user if they want to pay 1 cent as a thank you."""
    console.print("[dim]Pay cli-saver 1¢ as a thank you?[/dim] ", end="")
    try:
        response = input("[Y/n]: ").strip().lower()
        return response in ("", "y", "yes")
    except (EOFError, KeyboardInterrupt):
        console.print()
        return False
