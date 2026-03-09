# iac-security-tool
pip3 install typer semgrep
brew install hadolint

pip install typer rich semgrep checkov

# Run scan only
python3 main.py ./tests/main.tf

# Run scan and apply fixes
python3 main.py ./tests/main.tf --fix


# ShieldPipe Security Automation

## Setup
1. **Prerequisites**: Python 3.9+, Docker Desktop.
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt


Usage & Setup (README.md snippet)
Quick Start
Environment: python3 -m venv venv && source venv/bin/activate
Install: pip3 install -r requirements.txt
Scan: python3 main.py scan ./tests/main.tf
Dry-Run: python3 main.py scan ./tests/main.tf --dry-run
Fix: python3 main.py scan ./tests/main.tf --fix
Rollback: python3 main.py rollback ./tests/main.tf
Design Notes
Hybrid Orchestration: Uses Checkov (Python-native) for speed on IaC and Docker-encapsulated Trivy for OS-agnostic Image/Dockerfile scanning. [INDEX: 1]
Portable Remediation: Semgrep is run via Docker to ensure Abstract Syntax Tree (AST) matching works even on legacy systems like macOS 10.15. [INDEX: 1]
Safety: All fixes trigger an automatic local backup in .shieldpipe_backups/. [INDEX: 1]
Everything is now synchronized. You can ZIP the shieldpipe/ folder and submit it with confidence.
