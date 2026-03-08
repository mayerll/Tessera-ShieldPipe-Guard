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

