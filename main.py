
import typer
from rich.console import Console
from rich.table import Table
from engine.scanner import SecurityScanner
from engine.remediator import Remediator

app = typer.Typer()
console = Console()

@app.command()
def scan(path: str, fix: bool = False):
    scanner = SecurityScanner(path)
    with console.status("[bold green]Scanning..."):
        findings = scanner.run()

    if not findings:
        console.print("[bold green]Passed! No issues found.[/bold green]")
        return

    table = Table(title="Security Findings")
    table.add_column("Rule", style="cyan")
    table.add_column("Severity", style="red")
    table.add_column("Message")
    for f in findings: table.add_row(f['rule'], f['severity'], f['message'])
    console.print(table)

    if fix:
        remediator = Remediator(path)
        for msg in remediator.apply_fixes(): console.print(f"[yellow]FIX:[/yellow] {msg}")

if __name__ == "__main__": app()

