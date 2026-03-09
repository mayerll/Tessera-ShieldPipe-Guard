
import typer
import json
import os
import shutil
from rich.console import Console
from rich.table import Table
from engine.scanner import SecurityScanner
from engine.remediator import Remediator

app = typer.Typer(
    help="🛡️ ShieldPipe: Hybrid Security Automation",
    rich_markup_mode="rich"
)
console = Console()
BACKUP_DIR = ".shieldpipe_backups"

def create_backup(file_path: str):
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    if os.path.isfile(file_path):
        filename = os.path.basename(file_path)
        shutil.copy2(file_path, os.path.join(BACKUP_DIR, filename))

@app.command()
def scan(
    target: str = typer.Argument(..., help="Path to file/dir or a Docker image name"),
    fix: bool = typer.Option(False, "--fix", help="Apply fixes and create a backup"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show proposed fixes without applying them"),
    json_output: bool = typer.Option(False, "--json/--no-json", is_flag=True, help="Output results in JSON format")
):
    """
    Scan and optionally fix security issues in IaC, Docker, and Images.

    [bold cyan]Examples:[/bold cyan]
    - python3 main.py scan ./tests/Dockerfile
    - python3 main.py scan ./tests/main.tf
    - python3 main.py scan ./tests/requirements.txt
    - python3 main.py scan python:3.9-slim
    """
    scanner = SecurityScanner(target)

    with console.status("[bold green]Analyzing target..."):
        findings = scanner.run()

    # Calculate Severity Summary
    summary = {}
    for issue in findings:
        sev = issue.get('severity', 'UNKNOWN').upper()
        summary[sev] = summary.get(sev, 0) + 1

    if json_output:
        print(json.dumps({"target": target, "findings": findings, "summary": summary}, indent=2))
        return

    if not findings:
        console.print("[bold green]✔ No security issues detected![/bold green]")
        return

    # Findings Table
    table = Table(title=f"Findings: {target}")
    table.add_column("Rule ID", style="cyan")
    table.add_column("Severity", style="bold red")
    table.add_column("Message")
    for issue in findings:
        table.add_row(str(issue['rule']), str(issue['severity']), str(issue['message']))
    console.print(table)

    # Summary Table
    summary_table = Table(title="Summary")
    summary_table.add_column("Severity")
    summary_table.add_column("Count")
    for sev, count in summary.items():
        summary_table.add_row(sev, str(count))
    console.print(summary_table)

    # Fix / Dry Run Logic
    if (fix or dry_run) and os.path.exists(target):
        if fix and not dry_run:
            create_backup(target)

        remediator = Remediator(target)
        results = remediator.apply_fixes(dry_run=dry_run)
        for msg in results:
            console.print(f"[blue]ℹ[/blue] {msg}")

@app.command()
def rollback(file_path: str):
    """Restore file from the backup directory."""
    filename = os.path.basename(file_path)
    backup_path = os.path.join(BACKUP_DIR, filename)
    if os.path.exists(backup_path):
        shutil.copy2(backup_path, file_path)
        console.print(f"[bold green]Rollback successful:[/bold green] {file_path} restored.")
    else:
        console.print(f"[bold red]Error:[/bold red] No backup found for {filename}")

if __name__ == "__main__":
    app()


