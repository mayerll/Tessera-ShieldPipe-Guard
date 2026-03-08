
import subprocess
import json
import os

class SecurityScanner:
    def __init__(self, target_path: str):
        self.target_path = target_path

    def run(self) -> list:
        """Main entry point for scanning logic."""
        if not os.path.exists(self.target_path):
            return [{"rule": "ERROR", "severity": "CRITICAL", "message": f"Path not found: {self.target_path}"}]

        # Route to specific scanner based on file type
        if self.target_path.endswith(".tf") or (os.path.isdir(self.target_path) and any(f.endswith('.tf') for f in os.listdir(self.target_path))):
            return self._scan_terraform()
        elif "Dockerfile" in self.target_path:
            return self._scan_dockerfile()

        return []

    def _get_mapped_severity(self, check_id: str, check_name: str, raw_severity: str) -> str:
        """Helper to ensure Severity is never empty by mapping keywords if null."""
        if raw_severity and raw_severity.strip():
            return raw_severity.upper()

        # Heuristic mapping for open-source Checkov results
        identity = (check_id + check_name).upper()
        if any(k in identity for k in ["PUBLIC", "ACL", "SECRET", "PASSWORD", "KEY", "ACCESS_BLOCK"]):
            return "HIGH"
        if any(k in identity for k in ["ENCRYPT", "LOGGING", "VERSIONING", "PORT", "SSH"]):
            return "MEDIUM"

        return "LOW"

    def _scan_terraform(self):
        """Uses Checkov to scan Terraform files with enhanced Severity parsing."""
        try:
            is_file = os.path.isfile(self.target_path)
            cmd = ["checkov", "-f" if is_file else "-d", self.target_path, "--output", "json", "--quiet"]

            # Run checkov. Note: checkov exits with code 1 if issues are found,
            # so we capture output regardless of returncode.
            result = subprocess.run(cmd, capture_output=True, text=True)

            if not result.stdout.strip():
                return []

            data = json.loads(result.stdout)

            # Checkov can return a list of reports or a single report object
            failed_checks = []
            if isinstance(data, list):
                for report in data:
                    failed_checks.extend(report.get("results", {}).get("failed_checks", []))
            else:
                failed_checks = data.get("results", {}).get("failed_checks", [])

            processed = []
            for c in failed_checks:
                processed.append({
                    "rule": c.get("check_id"),
                    "severity": self._get_mapped_severity(
                        c.get("check_id", ""),
                        c.get("check_name", ""),
                        c.get("severity")
                    ),
                    "message": c.get("check_name")
                })
            return processed
        except Exception as e:
            return [{"rule": "SCAN_ERR", "severity": "HIGH", "message": f"Checkov failed: {str(e)}"}]

    def _scan_dockerfile(self):
        """Attempts local Hadolint scan, falls back to Docker-based Trivy on failure."""
        try:
            # 1. Try Hadolint (Fast, local)
            res = subprocess.run(["hadolint", self.target_path, "-f", "json"], capture_output=True, text=True)
            if res.returncode in [0, 1] and res.stdout.strip():
                data = json.loads(res.stdout)
                return [{
                    "rule": i['code'],
                    "severity": i.get('level', 'MEDIUM').upper(),
                    "message": i['message']
                } for i in data]
        except:
            pass # Move to fallback

        # 2. Fallback to Trivy via Docker (Solves macOS 10.15 'Symbol not found' error)
        return self._docker_fallback_trivy()

    def _docker_fallback_trivy(self):
        """Runs Trivy in a container to scan the Dockerfile safely."""
        try:
            abs_path = os.path.abspath(self.target_path)
            dir_name = os.path.dirname(abs_path)
            file_name = os.path.basename(abs_path)

            # Mount local dir to /apps in container
            cmd = [
                "docker", "run", "--rm",
                "-v", f"{dir_name}:/apps",
                "aquasec/trivy", "config", f"/apps/{file_name}",
                "--format", "json", "--quiet"
            ]

            res = subprocess.run(cmd, capture_output=True, text=True)
            data = json.loads(res.stdout)

            findings = []
            results = data.get("Results", [])
            for r in results:
                for m in r.get("Misconfigurations", []):
                    findings.append({
                        "rule": m.get('ID'),
                        "severity": m.get('Severity', 'MEDIUM').upper(),
                        "message": m.get('Title')
                    })
            return findings
        except Exception as e:
            return [{"rule": "DOCKER_ERR", "severity": "HIGH", "message": f"Trivy fallback failed: {str(e)}"}]

