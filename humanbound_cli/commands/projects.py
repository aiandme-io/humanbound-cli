"""Project commands."""

import click
from rich.console import Console
from rich.table import Table

from ..client import HumanboundClient
from ..exceptions import NotAuthenticatedError, APIError, ValidationError

console = Console()


@click.group("projects")
def projects_group():
    """Project management commands."""
    pass


@projects_group.command("list")
@click.option("--page", default=1, help="Page number")
@click.option("--size", default=20, help="Items per page")
def list_projects(page: int, size: int):
    """List projects in the current organisation."""
    client = HumanboundClient()

    try:
        response = client.list_projects(page=page, size=size)
        projects = response.get("data", [])

        if not projects:
            console.print("[yellow]No projects found.[/yellow]")
            return

        table = Table(title="Projects")
        table.add_column("ID", style="dim")
        table.add_column("Name", style="bold")
        table.add_column("Description")
        table.add_column("Active", justify="center")

        for proj in projects:
            is_active = "" if proj.get("id") != client.project_id else "[green]active[/green]"
            table.add_row(
                proj.get("id", ""),
                proj.get("name", "Unknown"),
                (proj.get("description", "") or "")[:40],
                is_active,
            )

        console.print(table)

        if response.get("has_next_page"):
            console.print(f"\n[dim]Page {page} of more. Use --page to navigate.[/dim]")

        if not client.project_id:
            console.print("\n[dim]Tip: Use 'hb projects use <id>' to select a project.[/dim]")

    except ValidationError as e:
        console.print(f"[yellow]{e}[/yellow]")
        console.print("Use 'hb switch <id>' to select an organisation first.")
        raise SystemExit(1)
    except NotAuthenticatedError:
        console.print("[red]Not authenticated.[/red] Run 'hb login' first.")
        raise SystemExit(1)
    except APIError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@projects_group.command("use")
@click.argument("project_id")
def use_project(project_id: str):
    """Set the active project.

    PROJECT_ID: Project UUID to use.
    """
    client = HumanboundClient()

    try:
        response = client.list_projects(size=100)
        projects = response.get("data", [])
        project = next((p for p in projects if p.get("id") == project_id), None)

        if not project:
            # Try partial match
            matches = [p for p in projects if p.get("id", "").startswith(project_id)]
            if len(matches) == 1:
                project = matches[0]
            elif len(matches) > 1:
                console.print(f"[yellow]Multiple projects match '{project_id}':[/yellow]")
                for p in matches:
                    console.print(f"  {p.get('id')} - {p.get('name')}")
                raise SystemExit(1)
            else:
                console.print(f"[red]Project not found:[/red] {project_id}")
                raise SystemExit(1)

        client.set_project(project.get("id"))
        console.print(f"[green]Switched to project:[/green] {project.get('name')}")

    except ValidationError as e:
        console.print(f"[yellow]{e}[/yellow]")
        raise SystemExit(1)
    except NotAuthenticatedError:
        console.print("[red]Not authenticated.[/red] Run 'hb login' first.")
        raise SystemExit(1)
    except APIError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)


@projects_group.command("current")
def current_project():
    """Show the currently selected project."""
    client = HumanboundClient()

    if not client.project_id:
        console.print("[yellow]No project selected.[/yellow]")
        console.print("Use 'hb projects use <id>' to select one.")
        return

    try:
        response = client.list_projects(size=100)
        projects = response.get("data", [])
        project = next((p for p in projects if p.get("id") == client.project_id), None)

        if project:
            console.print(f"[bold]{project.get('name')}[/bold]")
            console.print(f"[dim]ID: {client.project_id}[/dim]")
            if project.get("description"):
                console.print(f"Description: {project.get('description')}")
        else:
            console.print(f"[yellow]Project ID:[/yellow] {client.project_id}")

    except NotAuthenticatedError:
        console.print("[red]Not authenticated.[/red] Run 'hb login' first.")
        raise SystemExit(1)


@projects_group.command("show")
@click.argument("project_id", required=False)
def show_project(project_id: str):
    """Show project details.

    PROJECT_ID: Project UUID (uses current if not specified).
    """
    client = HumanboundClient()

    project_id = project_id or client.project_id

    if not project_id:
        console.print("[yellow]No project specified.[/yellow]")
        console.print("Use 'hb projects show <id>' or select a project first.")
        raise SystemExit(1)

    try:
        # Temporarily set project to fetch details
        original_project = client.project_id
        client.set_project(project_id)

        response = client.get(f"projects/{project_id}", include_project=True)

        console.print(f"\n[bold]{response.get('name')}[/bold]")
        console.print(f"[dim]ID: {response.get('id')}[/dim]\n")

        if response.get("description"):
            console.print(f"Description: {response.get('description')}\n")

        scope = response.get("scope", {})
        if scope:
            console.print("[bold]Scope:[/bold]")
            console.print(f"  Business: {scope.get('overall_business_scope', '')[:100]}...")

            intents = scope.get("intents", {})
            if intents.get("permitted"):
                console.print(f"  Permitted intents: {len(intents.get('permitted', []))} defined")
            if intents.get("restricted"):
                console.print(f"  Restricted intents: {len(intents.get('restricted', []))} defined")

        # Restore original project
        if original_project:
            client.set_project(original_project)

    except NotAuthenticatedError:
        console.print("[red]Not authenticated.[/red] Run 'hb login' first.")
        raise SystemExit(1)
    except APIError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)
