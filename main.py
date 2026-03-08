
import typer
import json
import os
import shutil
from rich.console import Console
from rich.table import Table
from engine.scanner import SecurityScanner
from engine.remediator import Remediator

app = typer.Typer(help="ShieldPipe: Hybrid Security Automation Tool")
console = Console()

BACKUP_DIR = ".shieldpipe_backups"

def create_backup(file_path: str):
    """Save a copy of the file before applying fixes."""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    if os.path.isfile(file_path):
        filename = os.path.basename(file_path)
        dest = os.path.join(BACKUP_DIR, filename)
        shutil.copy2(file_path, dest)

@app.command()
def scan(
    target: str = typer.Argument(..., help="Path to file/dir or Docker image name"),
    is_image: bool = typer.Option(False, "--image", help="Specify that the target is a Docker image"),
    fix: bool = typer.Option(False, "--fix", help="Apply fixes automatically (Files only)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview fixes without applying (Files only)"),
    json_output: bool = typer.Option(False, "--json", help="Output results in JSON format")
):
    """
    Scan IaC, Dockerfile, dependencies, or container image for security issues.
    """

    # Validation: If it's an image, we don't allow fix or dry-run
    if is_image and (fix or dry_run):
        console.print("[bold red]Error:[/bold red] Remediation (--fix/--dry-run) is not supported for binary images.")
        console.print("Please fix the source Dockerfile and rebuild the image.")
        raise typer.Exit(code=1)

    scanner = SecurityScanner(target)

    # 1️⃣ Run scan
    with console.status(f"[bold green]Scanning {target}..."):
        findings = scanner.run()

    # Calculate Summaries
    high = sum(1 for f in findings if str(f.get("severity", "")).upper() == "HIGH")
    medium = sum(1 for f in findings if str(f.get("severity", "")).upper() == "MEDIUM")
    low = sum(1 for f in findings if str(f.get("severity", "")).upper() == "LOW")

    # 2️⃣ JSON Output (for CI/CD)
    if json_output:
        output = {
            "target": target,
            "type": "container_image" if is_image else "source_file",
            "summary": {
                "high": high,
                "medium": medium,
                "low": low,
                "total": len(findings)
            },
            "findings": findings
        }
        print(json.dumps(output, indent=2))
        raise typer.Exit()

    # 3️⃣ Human readable output (table)
    if not findings:
        console.print(f"[bold green]✔ No security issues detected in {target}![/bold green]")
    else:
        table = Table(title=f"Security Findings: {target}")
        table.add_column("Rule ID", style="cyan", no_wrap=True)
        table.add_column("Severity", style="bold red")
        table.add_column("Message", style="white")

        for issue in findings:
            table.add_row(
                str(issue.get("rule", "N/A")),
                str(issue.get("severity", "MEDIUM")),
                str(issue.get("message", "No details"))
            )
        console.print(table)

        # 4️⃣ SUMMARY SECTION (Table View)
        console.print("\n[bold]Summary[/bold]")
        console.print(f"[red]HIGH[/red]: {high}")
        console.print(f"[yellow]MEDIUM[/yellow]: {medium}")
        console.print(f"[green]LOW[/green]: {low}")
        console.print(f"[bold]Total Findings:[/bold] {len(findings)}")

    # 5️⃣ Remediation section (Skipped if is_image or no file exists)
    if (fix or dry_run) and os.path.exists(target):
        if not dry_run:
            console.print(f"\n[yellow]Backing up {target} to {BACKUP_DIR}...[/yellow]")
            create_backup(target)

        remediator = Remediator(target)
        remediation_results = remediator.apply_fixes(dry_run=dry_run)

        console.print("\n[bold]Remediation[/bold]")
        for msg in remediation_results:
            color = "blue" if dry_run else "green"
            console.print(f"[{color}]ℹ[/{color}] {msg}")

@app.command()
def rollback(file_path: str):
    """Restore a file from backup."""
    filename = os.path.basename(file_path)
    backup_path = os.path.join(BACKUP_DIR, filename)

    if os.path.exists(backup_path):
        shutil.copy2(backup_path, file_path)
        console.print(f"[bold green]Rollback successful:[/bold green] {file_path} restored from backup.")
    else:
        console.print(f"[bold red]Error:[/bold red] No backup found for {filename} in {BACKUP_DIR}")

if __name__ == "__main__":
    app()

