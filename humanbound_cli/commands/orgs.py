"""Organisation commands."""

import click
from rich.console import Console
from rich.table import Table

from ..client import HumanboundClient
from ..exceptions import NotAuthenticatedError, APIError

console = Console()


@click.group("orgs")
def orgs_group():
    """Organisation management commands."""
    pass


@orgs_group.command("list")
def list_orgs():
    """List organisations you have access to."""
    client = HumanboundClient()

    try:
        orgs = client.list_organisations()

        if not orgs:
            console.print("[yellow]No organisations found.[/yellow]")
            return

        table = Table(title="Organisations")
        table.add_column("ID", style="dim")
        table.add_column("Name", style="bold")
        table.add_column("Active", justify="center")

        for org in orgs:
            is_active = "  " if org.get("id") != client.organisation_id else "[green]active[/green]"
            table.add_row(
                org.get("id", ""),
                org.get("name", "Unknown"),
                is_active,
            )

        console.print(table)

        if not client.organisation_id:
            console.print("\n[dim]Tip: Use 'hb switch <id>' to select an organisation.[/dim]")

    except NotAuthenticatedError:
        console.print("[red]Not authenticated.[/red] Run 'hb login' first.")
        raise SystemExit(1)
    except APIError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@orgs_group.command("current")
def current_org():
    """Show the currently selected organisation."""
    client = HumanboundClient()

    if not client.organisation_id:
        console.print("[yellow]No organisation selected.[/yellow]")
        console.print("Use 'hb switch <id>' to select one.")
        return

    try:
        orgs = client.list_organisations()
        org = next((o for o in orgs if o.get("id") == client.organisation_id), None)

        if org:
            console.print(f"[bold]{org.get('name')}[/bold]")
            console.print(f"[dim]ID: {client.organisation_id}[/dim]")
        else:
            console.print(f"[yellow]Organisation ID:[/yellow] {client.organisation_id}")
            console.print("[dim]Unable to fetch organisation details.[/dim]")

    except NotAuthenticatedError:
        console.print("[red]Not authenticated.[/red] Run 'hb login' first.")
        raise SystemExit(1)
