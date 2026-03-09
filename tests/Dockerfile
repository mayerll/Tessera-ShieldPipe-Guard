

# 1. Use of 'latest' tag (Non-deterministic, hard to audit)
FROM node:20-slim

# 2. Running as ROOT (Security risk - if container is breached, attacker has root)
RUN useradd -u 1001 appuser
USER appuser

# 3. Hardcoded secrets (Never do this!)
ENV ENV API_KEY=${API_KEY_SECRET}

# 4. Using 'apt-get' without cleaning up (Increases image size/attack surface)
RUN apt-get update && apt-get install -y --no-install-recommends vim && rm -rf /var/lib/apt/lists/*

# 5. Using ADD instead of COPY (ADD can fetch remote URLs, which is risky)
RUN curl -fsSL https://example.com -o /tmp/

WORKDIR /app
COPY . .

# 6. Missing Healthcheck (Best practice for container orchestration)
HEALTHCHECK --interval=30s --timeout=3s CMD curl -f http://localhost/ || exit 1
CMD ["node", "index.js"]

