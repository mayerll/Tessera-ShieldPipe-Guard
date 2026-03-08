
import subprocess
import json
import os

class SecurityScanner:
    def __init__(self, target: str):
        self.target = target

    def run(self) -> list:
        # 1. Check if it's a local file/directory
        if os.path.exists(self.target):
            if self.target.endswith(".tf") or os.path.isdir(self.target):
                return self._scan_terraform()
            if "Dockerfile" in self.target:
                return self._scan_dockerfile()

        # 2. Otherwise, treat it as a Docker Image name
        return self._scan_container_image()

    def _get_severity(self, c_id, c_name, raw):
        if raw and str(raw) != "None": return str(raw).upper()
        ident = (str(c_id) + str(c_name)).upper()
        if any(k in ident for k in ["PUBLIC", "ACL", "SECRET", "CRITICAL"]): return "HIGH"
        return "MEDIUM"

    def _scan_terraform(self):
        try:
            cmd = ["checkov", "-f" if os.path.isfile(self.target) else "-d", self.target, "--output", "json", "--quiet"]
            res = subprocess.run(cmd, capture_output=True, text=True)
            data = json.loads(res.stdout)
            failed = data.get("results", {}).get("failed_checks", []) if isinstance(data, dict) else []
            return [{"rule": c['check_id'], "severity": self._get_severity(c['check_id'], c['check_name'], c.get('severity')), "message": c['check_name']} for c in failed]
        except: return []

    def _scan_dockerfile(self):
        """Uses Trivy via Docker to bypass macOS library issues."""
        return self._docker_trivy_cmd("config")

    def _scan_container_image(self):
        """Scans a full container image for CVEs."""
        return self._docker_trivy_cmd("image")

    def _docker_trivy_cmd(self, mode: str):
        try:
            abs_p = os.path.abspath(self.target)
            if mode == "config":
                # Mount directory for Dockerfile scan
                cmd = ["docker", "run", "--rm", "-v", f"{os.path.dirname(abs_p)}:/apps", "aquasec/trivy", "config", f"/apps/{os.path.basename(abs_p)}", "--format", "json", "--quiet"]
            else:
                # Direct image scan (mount docker sock to see local images)
                cmd = ["docker", "run", "--rm", "-v", "/var/run/docker.sock:/var/run/docker.sock", "aquasec/trivy", "image", "--format", "json", "--quiet", self.target]

            res = subprocess.run(cmd, capture_output=True, text=True)
            data = json.loads(res.stdout)
            findings = []
            for r in data.get("Results", []):
                # Handle Misconfigurations (Dockerfiles)
                for m in r.get("Misconfigurations", []):
                    findings.append({"rule": m['ID'], "severity": m['Severity'], "message": m['Title']})
                # Handle Vulnerabilities (Images)
                for v in r.get("Vulnerabilities", []):
                    findings.append({"rule": v['VulnerabilityID'], "severity": v['Severity'], "message": f"{v['PkgName']}: {v.get('Title', 'CVE')}"})
            return findings
        except:
            return [{"rule": "DOCKER_ERR", "severity": "HIGH", "message": "Ensure Docker is running for this scan"}]

