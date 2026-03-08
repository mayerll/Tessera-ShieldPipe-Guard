
import subprocess
import os

class Remediator:
    def __init__(self, target: str):
        self.target = target

    def apply_fixes(self, dry_run: bool = False) -> list:
        if not os.path.exists(self.target): return []

        fixes = []
        abs_p = os.path.abspath(self.target)
        dir_p = os.path.dirname(abs_p)
        file_n = os.path.basename(abs_p)

        # Use Docker to run Semgrep to avoid macOS compatibility issues
        cmd = [
            "docker", "run", "--rm",
            "-v", f"{dir_p}:/src",
            "-v", f"{os.getcwd()}/fix_rules.yaml:/fix_rules.yaml",
            "returntocorp/semgrep", "semgrep",
            "--config", "/fix_rules.yaml",
            "--autofix",
            "--quiet",
            f"/src/{file_n}"
        ]

        if dry_run:
            cmd.append("--dry-run")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)

            if dry_run:
                fixes.append("DRY-RUN: Proposed changes (Diff):")
                # Semgrep output usually contains the diff
                fixes.append(result.stdout if result.stdout else "No changes matched the patterns.")
            else:
                fixes.append(f"Auto-remediation applied to {file_n} via Docker")
        except Exception as e:
            fixes.append(f"Remediation failed: {str(e)}")

        return fixes

