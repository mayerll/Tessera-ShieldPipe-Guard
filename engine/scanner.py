
import subprocess
import json
import os

class SecurityScanner:
    def __init__(self, target: str):
        self.target = target

    def run(self) -> list:
        if os.path.exists(self.target):
            if self.target.endswith(".tf") or os.path.isdir(self.target):
                return self._scan_terraform()
            if "Dockerfile" in self.target:
                return self._scan_dockerfile()
            if "requirements.txt" in self.target:
                return self._scan_dependencies()
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
            failed = []
            if isinstance(data, list):
                for r in data: failed.extend(r.get("results", {}).get("failed_checks", []))
            else:
                failed = data.get("results", {}).get("failed_checks", [])
            return [{"rule": c['check_id'], "severity": self._get_severity(c['check_id'], c['check_name'], c.get('severity')), "message": c['check_name']} for c in failed]
        except: return []

    def _scan_dockerfile(self): return self._docker_trivy_cmd("config")
    def _scan_dependencies(self): return self._docker_trivy_cmd("fs")
    def _scan_container_image(self): return self._docker_trivy_cmd("image")

    def _docker_trivy_cmd(self, mode: str):
        try:
            abs_p = os.path.abspath(self.target)
            if mode in ["config", "fs"]:
                cmd = ["docker", "run", "--rm", "-v", f"{os.path.dirname(abs_p)}:/apps", "aquasec/trivy", mode, f"/apps/{os.path.basename(abs_p)}", "--format", "json", "--quiet"]
            else:
                cmd = ["docker", "run", "--rm", "-v", "/var/run/docker.sock:/var/run/docker.sock", "aquasec/trivy", "image", "--format", "json", "--quiet", self.target]

            res = subprocess.run(cmd, capture_output=True, text=True)
            data = json.loads(res.stdout)
            findings = []
            for r in data.get("Results", []):
                for m in r.get("Misconfigurations", []):
                    findings.append({"rule": m['ID'], "severity": m['Severity'], "message": m['Title']})
                for v in r.get("Vulnerabilities", []):
                    findings.append({"rule": v['VulnerabilityID'], "severity": v['Severity'], "message": f"{v['PkgName']}: {v.get('Title', 'CVE')}"})
            return findings
        except: return [{"rule": "DOCKER_ERR", "severity": "HIGH", "message": "Ensure Docker is running"}]

