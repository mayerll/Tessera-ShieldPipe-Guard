
import subprocess
import os

class Remediator:
    def __init__(self, target: str):
        self.target = target

    def apply_fixes(self, dry_run: bool = False) -> list:
        """
        Applies automated patches using Semgrep via Docker to avoid OS library issues.
        """
        if not os.path.exists(self.target):
            return [f"Error: Target path '{self.target}' not found."]

        # 1. Resolve Absolute Paths for Docker Volume Mapping
        abs_target = os.path.abspath(self.target)
        target_dir = os.path.dirname(abs_target)
        target_file = os.path.basename(abs_target)

        # Assuming fix_rules.yaml is in the project root (same level as main.py)
        # We use os.getcwd() to find the rules file relative to where the command is run
        project_root = os.getcwd()
        rules_path = os.path.join(project_root, "fix_rules.yaml")

        if not os.path.exists(rules_path):
            return [f"Remediation skipped: 'fix_rules.yaml' not found in {project_root}"]

        messages = []

        # 2. Construct the Docker Command
        # We mount the target directory to /src and the rules file to /rules.yaml
        cmd = [
            "docker", "run", "--rm",
            "-v", f"{target_dir}:/src",
            "-v", f"{rules_path}:/rules.yaml",
            "returntocorp/semgrep", "semgrep",
            "--config", "/rules.yaml",
            "--autofix",
            "--quiet",
            f"/src/{target_file}"
        ]

        # 3. Add Dry-Run flag if requested
        if dry_run:
            cmd.append("--dry-run")

        try:
            # Execute Semgrep
            result = subprocess.run(cmd, capture_output=True, text=True)

            if dry_run:
                # In dry-run mode, Semgrep prints the Unified Diff (+/-) to stdout
                diff_output = result.stdout.strip()
                if diff_output:
                    messages.append("DRY-RUN Proposed Diff:")
                    messages.append(diff_output)
                else:
                    messages.append("No changes matched your fix rules. Check if 'fix_rules.yaml' matches the code.")
            else:
                # Normal mode
                messages.append(f"Successfully applied security patches to {target_file}")

        except Exception as e:
            messages.append(f"Remediation Error: {str(e)}")

        return messages

