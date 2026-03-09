
import subprocess
import os

class Remediator:
    def __init__(self, target: str):
        self.target = target

    def apply_fixes(self, dry_run: bool = False) -> list:
        if not os.path.exists(self.target):
            return [f"Error: Target {self.target} not found."]

        abs_target = os.path.abspath(self.target)
        target_dir = os.path.dirname(abs_target)
        target_file = os.path.basename(abs_target)

        # Resolve rules file absolute path
        project_root = os.getcwd()
        rules_path = os.path.join(project_root, "fix_rules.yaml")

        if not os.path.exists(rules_path):
            return [f"Error: fix_rules.yaml missing at {rules_path}"]

        # Ensure Docker runs as current user so it has permission to overwrite host files
        uid = os.getuid()
        gid = os.getgid()

        # Semgrep command for Docker
        # -u: Match host permissions
        # :rw: Explicitly allow writing back to the directory
        cmd = [
            "docker", "run", "--rm",
            "-u", f"{uid}:{gid}",
            "-v", f"{target_dir}:/src:rw",
            "-v", f"{rules_path}:/rules.yaml:ro",
            "returntocorp/semgrep", "semgrep",
            "scan",
            "--config", "/rules.yaml",
            "--autofix",
            f"/src/{target_file}"
        ]

        if dry_run:
            cmd.append("--dryrun")

        try:
            # Capture both stdout and stderr because Semgrep fix logs vary by version
            result = subprocess.run(cmd, capture_output=True, text=True)
            output_log = (result.stdout + result.stderr).strip()

            # Handle Permission Errors
            if "Operation not permitted" in output_log or "Sys_error" in output_log:
                return [
                    f"Permission Error: Docker cannot write to {target_file}.",
                    f"Try: chmod 666 {self.target}"
                ]

            if dry_run:
                if result.stdout.strip():
                    return ["DRY-RUN Proposed Diff:", result.stdout]
                return ["No fixes matched the current rules (Dry-run)."]

            # Success Detection Logic
            # Semgrep may output "Fixed X findings" to either stdout or stderr
            success_keywords = ["Fixed", "Autofixed", "modified", "applied"]
            if any(word in output_log for word in success_keywords):
                return [f"Successfully patched {target_file} via Semgrep"]

            # If the command finished but no specific 'Fixed' message was found
            return [f"Fix attempt finished for {target_file}. Verify with 'diff'."]

        except Exception as e:
            return [f"Execution Failed: {str(e)}"]



