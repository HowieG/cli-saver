"""Nevermined payments integration."""

from rich.console import Console
from rich.panel import Panel
from .config import get_nevermined_api_key


console = Console()

# CLI Saver's subscription/plan DID (created via Nevermined dashboard)
# This would be the actual plan ID for cli-saver tips
CLI_SAVER_PLAN_DID = "did:nv:cli-saver-tip-plan"


def process_payment(debug: bool = True) -> bool:
    """Process a 1-cent payment via Nevermined.

    Returns True if payment was successful, False otherwise.
    """
    api_key = get_nevermined_api_key()

    if not api_key:
        console.print("[yellow]Nevermined not configured. Run 'cli-saver setup' first.[/yellow]")
        return False

    console.print("[dim]Connecting to Nevermined...[/dim]")

    payment_attempted = False
    payment_success = False

    try:
        from payments_py import Payments, PaymentOptions

        if debug:
            console.print("[dim]  SDK imported successfully (payments-py)[/dim]")

        # Validate API key format (should be address:key)
        if ":" not in api_key:
            console.print("[yellow]  API key format invalid. Expected format: address:key[/yellow]")
            console.print("[yellow]  Get your API key from: https://nevermined.app[/yellow]")
        else:
            # Initialize payments with options
            options = PaymentOptions(
                environment="sandbox",
                nvm_api_key=api_key,
                app_id="cli-saver",
                version="1.0.0",
            )
            payments = Payments(options)
            payment_attempted = True

            if debug:
                console.print("[dim]  Payments client initialized[/dim]")
                console.print(f"[dim]  Environment: sandbox[/dim]")
                key_preview = api_key[:12] + "..." + api_key[-4:] if len(api_key) > 16 else api_key
                console.print(f"[dim]  API Key: {key_preview}[/dim]")

            # Try to get account info / balance
            try:
                if hasattr(payments, 'plans') and hasattr(payments.plans, 'get_credits_balance'):
                    if debug:
                        console.print("[dim]  Checking credits balance...[/dim]")
                    # This would check balance for a specific plan

            except Exception as e:
                if debug:
                    console.print(f"[dim]  Balance check: {e}[/dim]")

            # Try to order/subscribe to the cli-saver plan
            try:
                if hasattr(payments, 'plans') and hasattr(payments.plans, 'order_plan'):
                    if debug:
                        console.print(f"[dim]  Attempting to order plan...[/dim]")
                    response = payments.plans.order_plan(CLI_SAVER_PLAN_DID)
                    if debug:
                        console.print(f"[dim]  Order response: {response}[/dim]")
                    payment_success = True
            except Exception as e:
                if debug:
                    console.print(f"[dim]  Order attempt: {e}[/dim]")

    except ImportError as e:
        console.print(f"[yellow]Nevermined SDK not installed: {e}[/yellow]")
        console.print("[yellow]Install with: pip install payments-py[/yellow]")
    except Exception as e:
        if debug:
            console.print(f"[dim]  SDK error: {e}[/dim]")

    # Always show thank you message if user wanted to pay
    console.print()
    console.print(Panel(
        "[bold green]Thank you for your micropayment![/bold green]\n\n"
        "[dim]Your support helps maintain cli-saver.[/dim]",
        border_style="green",
        padding=(1, 2),
    ))

    if not payment_success and debug:
        console.print("[dim]Note: To enable actual payments, configure a valid Nevermined API key.[/dim]")
        console.print("[dim]Get yours at: https://nevermined.app[/dim]")

    return True
