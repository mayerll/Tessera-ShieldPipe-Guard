
import subprocess
import os

class Remediator:
    def __init__(self, target: str):
        self.target = target

    def apply_fixes(self, dry_run: bool = False) -> list:
        if not os.path.exists(self.target): return []

        abs_target = os.path.abspath(self.target)
        target_dir = os.path.dirname(abs_target)
        target_file = os.path.basename(abs_target)

        # Resolve rules file absolute path
        project_root = os.getcwd()
        rules_path = os.path.join(project_root, "fix_rules.yaml")

        cmd = [
            "docker", "run", "--rm",
            "-v", f"{target_dir}:/src",
            "-v", f"{rules_path}:/rules.yaml",
            "returntocorp/semgrep", "semgrep",
            "--config", "/rules.yaml", "--autofix", "--quiet", f"/src/{target_file}"
        ]

        if dry_run: cmd.append("--dry-run")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if dry_run:
                return ["DRY-RUN Proposed Diff:", result.stdout] if result.stdout.strip() else ["No changes matched."]
            return [f"Patched {target_file} via Dockerized Semgrep"]
        except Exception as e:
            return [f"Error: {str(e)}"]

