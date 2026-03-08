
import typer
import json
import os
import shutil
from rich.console import Console
from rich.table import Table
from engine.scanner import SecurityScanner
from engine.remediator import Remediator

# 1. Initialize the app FIRST
app = typer.Typer(help="ShieldPipe: Security Automation")
console = Console()
BACKUP_DIR = ".shieldpipe_backups"

# 2. Define helper functions
def create_backup(file_path: str):
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    if os.path.isfile(file_path):
        filename = os.path.basename(file_path)
        shutil.copy2(file_path, os.path.join(BACKUP_DIR, filename))

# 3. Define commands using @app.command()
@app.command()
def scan(
    target: str = typer.Argument(..., help="Path to file/dir or a Docker image name"),
    fix: bool = typer.Option(False, "--fix", help="Apply fixes and create a backup"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show proposed fixes without applying them"),
    json_output: bool = typer.Option(False, "--json", help="Output results in JSON format")
):
    scanner = SecurityScanner(target)
    findings = scanner.run()

    if json_output:
        print(json.dumps({"target": target, "findings": findings}, indent=2))
        return

    if not findings:
        console.print("[bold green]✔ No security issues detected![/bold green]")
        return

    table = Table(title=f"Findings: {target}")
    table.add_column("Rule ID", style="cyan")
    table.add_column("Severity", style="bold red")
    table.add_column("Message")
    for issue in findings:
        table.add_row(issue['rule'], issue['severity'], issue['message'])
    console.print(table)

    if (fix or dry_run) and os.path.exists(target):
        if not dry_run:
            create_backup(target)
        remediator = Remediator(target)
        results = remediator.apply_fixes(dry_run=dry_run)
        for msg in results:
            console.print(f"[blue]ℹ[/blue] {msg}")

@app.command()
def rollback(file_path: str):
    filename = os.path.basename(file_path)
    backup_path = os.path.join(BACKUP_DIR, filename)
    if os.path.exists(backup_path):
        shutil.copy2(backup_path, file_path)
        console.print(f"[bold green]Rollback successful:[/bold green] {file_path} restored.")
    else:
        console.print(f"[bold red]Error:[/bold red] No backup found for {filename}")

# 4. Entry point
if __name__ == "__main__":
    app()

