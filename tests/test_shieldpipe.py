
import sys
import os
import pytest
from typer.testing import CliRunner

# Add the project root to sys.path so 'engine' and 'main' are discoverable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.scanner import SecurityScanner
from engine.remediator import Remediator
from main import app

runner = CliRunner()

# ==========================================
# 1. SCANNER TESTS
# ==========================================

def test_dockerfile_scanner():
    """Verify that Trivy detects critical/high issues in the Dockerfile."""
    scanner = SecurityScanner("./tests/Dockerfile")
    findings = scanner.run()

    rule_ids = [f['rule'] for f in findings]
    # Check for specific Trivy Docker IDs
    assert "DS-0001" in rule_ids  # Latest tag
    assert "DS-0002" in rule_ids  # Root user
    assert any(f['severity'] in ["HIGH", "CRITICAL"] for f in findings)

def test_requirements_scanner():
    """Verify that Trivy detects CVEs in requirements.txt."""
    scanner = SecurityScanner("./tests/requirements.txt")
    findings = scanner.run()

    assert len(findings) > 0
    # Ensure it's picking up Flask/Requests related CVEs
    messages = [f['message'].lower() for f in findings]
    assert any("flask" in msg or "requests" in msg for msg in messages)

# ==========================================
# 2. REMEDIATOR TESTS (DRY-RUN)
# ==========================================

def test_remediator_dockerfile_dry_run():
    """Verify Semgrep proposes changes to Dockerfile without touching the file."""
    remediator = Remediator("./tests/Dockerfile")
    mtime_before = os.path.getmtime("./tests/Dockerfile")

    results = remediator.apply_fixes(dry_run=True)

    # Check that a diff was actually proposed in the output
    combined_output = "".join(results)
    assert "Proposed Diff" in combined_output
    assert "FROM node:20-slim" in combined_output

    # Integrity check: Ensure file was NOT modified on disk
    assert os.path.getmtime("./tests/Dockerfile") == mtime_before

def test_remediator_requirements_match():
    """Verify that 'generic' rules in fix_rules.yaml match the text file."""
    remediator = Remediator("./tests/requirements.txt")
    results = remediator.apply_fixes(dry_run=True)

    combined_output = "".join(results)
    assert "flask==2.3.3" in combined_output
    assert "requests==2.31.0" in combined_output

# ==========================================
# 3. CLI INTEGRATION TESTS
# ==========================================

def test_cli_scan_json():
    """Test the CLI 'scan' command with --json flag."""
    # Using a simple file to ensure quick execution
    result = runner.invoke(app, ["scan", "./tests/requirements.txt", "--json"])
    assert result.exit_code == 0
    import json
    data = json.loads(result.stdout)
    assert "target" in data
    assert "findings" in data
    assert "summary" in data

def test_cli_help():
    """Test that the custom help examples are present."""
    result = runner.invoke(app, ["scan", "--help"])
    assert result.exit_code == 0
    assert "python3 main.py scan ./tests/Dockerfile" in result.stdout

