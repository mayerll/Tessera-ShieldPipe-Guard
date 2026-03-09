
FROM python:3.11-slim

# Install Docker CLI to allow the tool to trigger Trivy/Semgrep containers
RUN apt-get update && apt-get install -y docker.io && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

# Explicitly use python3
ENTRYPOINT ["python3", "main.py"]

