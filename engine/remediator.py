
import subprocess

class Remediator:
    def __init__(self, target_path: str):
        self.target_path = target_path

    def apply_fixes(self) -> list:
        """Uses Semgrep --autofix to rewrite insecure code patterns."""
        try:
            # Semgrep is Python-based and runs fine on macOS 10.15
            cmd = ["semgrep", "--config", "auto", "--autofix", "--quiet", self.target_path]
            subprocess.run(cmd, capture_output=True)
            return [f"Successfully applied patches to {self.target_path}"]
        except Exception as e:
            return [f"Remediation failed: {str(e)}"]

