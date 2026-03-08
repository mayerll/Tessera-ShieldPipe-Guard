# iac-security-tool
pip3 install typer semgrep
brew install hadolint

pip install typer rich semgrep checkov

# Run scan only
python3 main.py ./tests/main.tf

# Run scan and apply fixes
python3 main.py ./tests/main.tf --fix

