import subprocess
import json
import logging

class HyprManager:
    def __init__(self, hyprctl_path="hyprctl"):
        self.hyprctl_path = hyprctl_path

    def _run_command(self, args):
        try:
            full_args = [self.hyprctl_path] + args
            result = subprocess.run(full_args, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            logging.error(f"Error running hyprctl: {e}")
            return None
        except FileNotFoundError:
            logging.error(f"hyprctl not found at {self.hyprctl_path}")
            return None
        except (PermissionError, OSError) as e:
            logging.error(f"Unexpected error running hyprctl: {e}")
            return None

    def get_workspaces(self):
        output = self._run_command(["workspaces", "-j"])
        if output:
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                logging.error("Failed to parse hyprctl output as JSON")
        return []

    def switch_to_workspace(self, workspace_id):
        self._run_command(["dispatch", "workspace", str(workspace_id)])

    def get_active_workspace(self):
        output = self._run_command(["activeworkspace", "-j"])
        if output:
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                logging.error("Failed to parse hyprctl output as JSON")
        return None

    def make_floating_and_center(self):
        """Forces the workspace manager window to float and center using class selector."""
        # 'class' in hyprctl corresponds to the app_id in Wayland
        selector = "class:^hypr-ws-manager$"
        self._run_command(["dispatch", "setfloating", selector])
        self._run_command(["dispatch", "centerwindow", selector])
        self._run_command(["dispatch", "pin", selector])
