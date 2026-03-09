
import pytest
import os
from engine.scanner import SecurityScanner
from engine.remediator import Remediator

# 1. Test the Scanner
def test_dockerfile_scanner():
    """Verify that Trivy detects issues in the Dockerfile."""
    scanner = SecurityScanner("./tests/Dockerfile")
    findings = scanner.run()
    
    # Check for specific rule IDs we expect to find
    rule_ids = [f['rule'] for f in findings]
    assert "DS-0001" in rule_ids  # Latest tag
    assert "DS-0002" in rule_ids  # Root user

def test_terraform_scanner():
    """Verify that Checkov detects issues in the TF file."""
    scanner = SecurityScanner("./tests/main.tf")
    findings = scanner.run()
    
    rule_ids = [f['rule'] for f in findings]
    # Checkov IDs for S3 Public and EBS Encryption
    assert any("CKV_AWS_19" in rid or "CKV_AWS_20" in rid for rid in rule_ids)

# 2. Test the Remediator (Dry Run)
def test_remediator_dry_run():
    """Verify that Semgrep proposes fixes without changing the file."""
    remediator = Remediator("./tests/Dockerfile")
    # Get modification time before run
    mtime_before = os.path.getmtime("./tests/Dockerfile")
    
    results = remediator.apply_fixes(dry_run=True)
    
    # Ensure it proposed a diff
    assert any("Proposed Diff" in str(res) for res in results)
    # Ensure file was NOT modified
    assert os.path.getmtime("./tests/Dockerfile") == mtime_before

# 3. Test Rule Matching for Requirements
def test_requirements_fix_match():
    """Verify that our 'generic' rules match vulnerable python packages."""
    remediator = Remediator("./tests/requirements.txt")
    results = remediator.apply_fixes(dry_run=True)
    
    combined_results = "".join(results)
    assert "flask==2.3.3" in combined_results
    assert "requests==2.31.0" in combined_results

