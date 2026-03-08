
import typer
import json
import os
import shutil
from rich.console import Console
from rich.table import Table
from engine.scanner import SecurityScanner
from engine.remediator import Remediator

app = typer.Typer(help="ShieldPipe: Hybrid Security Automation")
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
    json_output: bool = typer.Option(False, "--json", help="Output results in JSON format")
):
    """Scan and optionally fix security issues in IaC, Docker, and Images."""
    scanner = SecurityScanner(target)

    with console.status("[bold green]Analyzing target..."):
        findings = scanner.run()

    # Count the number of issues by severity
    severity_count = {}
    for issue in findings:
        sev = issue['severity'].upper()
        severity_count[sev] = severity_count.get(sev, 0) + 1

    # JSON output includes summary
    if json_output is False:
        output = {
            "target": target,
            "findings": findings,
            "summary": severity_count
        }
        print(json.dumps(output, indent=2))
        return

    if not findings:
        console.print("[bold green]✔ No security issues detected![/bold green]")
        return

    # Severity color map
    severity_colors = {
        "CRITICAL": "red",
        "HIGH": "bright_red",
        "MEDIUM": "yellow",
        "LOW": "green"
    }

    # Detailed findings table with colored Severity
    table = Table(title=f"Findings: {target}")
    table.add_column("Rule ID", style="cyan")
    table.add_column("Severity", style="bold")
    table.add_column("Message")
    for issue in findings:
        sev = issue['severity'].upper()
        color = severity_colors.get(sev, "white")
        table.add_row(
            str(issue['rule']),
            f"[{color}]{sev}[/{color}]",
            str(issue['message'])
        )
    console.print(table)

    # Colorful summary table
    summary_table = Table(title="Summary")
    summary_table.add_column("Severity", style="bold")
    summary_table.add_column("Count", justify="right")
    for sev, count in severity_count.items():
        color = severity_colors.get(sev, "white")
        summary_table.add_row(f"[{color}]{sev}[/{color}]", str(count))
    console.print(summary_table)

    # Apply fixes if requested
    if (fix or dry_run) and os.path.exists(target):
        if not dry_run:
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



