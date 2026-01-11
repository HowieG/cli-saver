"""Nevermined payments integration."""

from rich.console import Console
from rich.panel import Panel
from .config import get_nevermined_api_key


console = Console()

# CLI Saver's subscription/plan ID (created via Nevermined dashboard)
CLI_SAVER_PLAN_ID = "17593782799367285350047817472144296690553106270380085148269475707554361233917"


def process_payment(debug: bool = True) -> bool:
    """Process a 1-cent payment via Nevermined.

    Returns True if payment was successful, False otherwise.
    """
    api_key = get_nevermined_api_key()

    if not api_key:
        console.print(
            "[yellow]Nevermined not configured. Run 'cli-saver setup' first.[/yellow]"
        )
        return False

    console.print("[dim]Connecting to Nevermined...[/dim]")

    payment_success = False

    try:
        from payments_py import Payments, PaymentOptions

        if debug:
            console.print("[dim]  SDK imported successfully (payments-py)[/dim]")

        # Validate API key format (should be address:key)
        if ":" not in api_key:
            console.print(
                "[yellow]  API key format invalid. Expected format: address:key[/yellow]"
            )
            console.print(
                "[yellow]  Get your API key from: https://nevermined.app[/yellow]"
            )
        else:
            # Initialize payments with options
            options = PaymentOptions(
                environment="sandbox",
                nvm_api_key=api_key,
                app_id="cli-saver",
                version="1.0.0",
            )
            payments = Payments(options)

            if debug:
                console.print("[dim]  Payments client initialized[/dim]")
                console.print("[dim]  Environment: sandbox[/dim]")
                key_preview = (
                    api_key[:12] + "..." + api_key[-4:]
                    if len(api_key) > 16
                    else api_key
                )
                console.print(f"[dim]  API Key: {key_preview}[/dim]")

            # Try to order/subscribe to the cli-saver plan
            try:
                if hasattr(payments, "plans") and hasattr(payments.plans, "order_plan"):
                    if debug:
                        console.print("[dim]  Attempting to order plan...[/dim]")
                    response = payments.plans.order_plan(CLI_SAVER_PLAN_ID)
                    if debug:
                        console.print(f"[dim]  Order response: {response}[/dim]")
                    payment_success = True
            except Exception as e:
                error_msg = str(e)
                if debug:
                    console.print(f"[dim]  Order attempt: {error_msg}[/dim]")

                # Provide helpful error messages
                if "Invalid Address" in error_msg:
                    if debug:
                        console.print("[dim]  Note: Your Nevermined account needs a funded wallet to make payments.[/dim]")

    except ImportError as e:
        console.print(f"[yellow]Nevermined SDK not installed: {e}[/yellow]")
        console.print("[yellow]Install with: pip install payments-py[/yellow]")
        return False
    except Exception as e:
        if debug:
            console.print(f"[dim]  SDK error: {e}[/dim]")

    # Show thank you message
    console.print()
    if payment_success:
        console.print(
            Panel(
                "[bold green]Thank you for your micropayment![/bold green]\n\n"
                "[dim]Payment successful! Your support helps maintain cli-saver.[/dim]",
                border_style="green",
                padding=(1, 2),
            )
        )
    else:
        console.print(
            Panel(
                "[bold green]Thank you for your support![/bold green]\n\n"
                "[dim]Payment pending - ensure your Nevermined wallet is funded.[/dim]",
                border_style="yellow",
                padding=(1, 2),
            )
        )

    return payment_success
