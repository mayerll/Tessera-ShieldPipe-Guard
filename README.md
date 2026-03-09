
# Tessera ShieldPipe (Chang'e) Security CI

ShieldPipe is a hybrid security automation orchestrator designed to scan and remediate security misconfigurations across Infrastructure as Code (IaC), Dockerfiles, and Python dependencies. 

It wraps industry-standard engines (**Trivy**, **Checkov**, and **Semgrep**) into a unified developer-friendly interface, providing automated "safe-patching" capabilities.

## Quick Start

### 1. Prerequisites
- **Python 3.10+**
  <img width="518" height="89" alt="image" src="https://github.com/user-attachments/assets/d5533551-f42a-436d-b87d-ef929d22baae" />

- **Docker Desktop** (Must be running, as scanners run in isolated containers)

### 2. Installation
```bash
# Clone the repository
git clone git@github.com:mayerll/Tessera-ShieldPipe-Guard.git
cd Tessera-ShieldPipe-Guard

# Initialize environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

## Usage Guide

### 1. Installation and Environment Setup
Run these commands to initialize your local development environment:

```bash
# Clone the repository
git clone git@github.com:mayerll/Tessera-ShieldPipe-Guard.git
cd Tessera-ShieldPipe-Guard

# Initialize virtual environment
python3 -m venv venv
source venv/bin/activate

# Install required dependencies
pip install -r requirements.txt

## 2. Scanning Targets
Detect security vulnerabilities in Dockerfiles, Terraform configurations, and Python dependencies.

```bash
# Standard scans
python3 main.py scan ./tests/Dockerfile
python3 main.py scan ./tests/main.tf
python3 main.py scan ./tests/requirements.txt
python3 main.py scan python:3.9-slim

# Structured JSON output (for CI/CD integration)
python3 main.py scan ./tests/Dockerfile --json
python3 main.py scan ./tests/main.tf --json
python3 main.py scan ./tests/requirements.txt --json
python3 main.py scan python:3.9-slim --json


## 3. Proposed Fixes (Dry-run)
View proposed code changes in unified diff format without modifying the actual source files.

```bash
python3 main.py scan ./tests/Dockerfile --dry-run 
python3 main.py scan ./tests/main.tf --dry-run 
python3 main.py scan ./tests/requirements.txt --dry-run 

## 4. Automatic Remediation (Fix)
Automatically apply security patches based on fix_rules.yaml. This command creates an automatic backup before modification.

```bash
python3 main.py scan ./tests/Dockerfile --fix  
python3 main.py scan ./tests/main.tf --fix 
python3 main.py scan ./tests/requirements.txt --fix 

## 5. Rollback
Restore a file to its state before the last fix operation using the internal backup directory.

```bash
python3 main.py rollback ./tests/Dockerfile
python3 main.py rollback ./tests/main.tf 
python3 main.py rollback ./tests/requirements.txt

