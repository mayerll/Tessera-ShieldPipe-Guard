
## Architecture and Workflow

ShieldPipe follows a "Detect -> Report -> Remediate" cycle.

```mermaid
graph TD
    A[User CLI Input] --> B{Scanner Engine}
    B -->|Dockerfile/Image| C[Trivy]
    B -->|Terraform| D[Checkov]
    B -->|Dependencies| E[Trivy FS]
    C & D & E --> F[Findings Parser]
    F --> G[Rich Console Table]
    F --> H[JSON Output]
    G --> I{Fix Requested?}
    I -->|Yes| J[Semgrep Patch Engine]
    J --> K[Backup Original File]
    K --> L[Apply fix_rules.yaml]
    L --> M[Modified Secure File]


## Implementation Strategy

1. **Hybrid Orchestration**: ShieldPipe leverages Trivy and Checkov via Docker containers to ensure scanning engines remain current with the latest CVE databases without manual maintenance overhead.
2. **Semantic Remediation**: The tool utilizes Semgrep for code patching. Unlike standard Regex-based replacement, Semgrep is syntax-aware and understands code structure, making security fixes more robust and contextually accurate.
3. **Safety Controls**: Mandatory atomic backups are performed before any write operation. The dry-run mode provides a unified diff preview, allowing developers to audit proposed changes before they are committed to disk.
4. **Environment Isolation**: By utilizing Dockerized scanning engines, the host environment remains clean of security tool dependencies, ensuring high portability across different operating systems.


## Roadmap and Bug List (Future Improvements)

1. **Input Validation**: Add strict validation for target paths to prevent directory traversal or malformed image names. This includes validating that local paths exist before triggering expensive Docker processes.
2. **REST API**: Wrap the core orchestration logic in a FastAPI layer to support remote webhook triggers, centralized monitoring, and cross-team integration.
3. **Structured Remediation**: Currently, --fix and --dry-run provide human-readable diffs for developer convenience. Future versions will support structured JSON reporting for all remediation actions taken to facilitate automated auditing.
4. **Validation Step**: Integrate automated syntax checks such as "terraform validate" or "docker build" immediately after a patch is applied to ensure zero syntax regressions.
5. **Enhanced Rollback**: Expand the current single-version rollback system into a multi-version history tracking system stored in a local metadata store.
6. **Command Validation**: Add logic to verify user input commands and prevent execution of conflicting flags (e.g., preventing --fix and --json from running simultaneously without a defined schema).




