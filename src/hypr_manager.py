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

    def get_active_window(self):
        output = self._run_command(["activewindow", "-j"])
        if output:
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                logging.error("Failed to parse hyprctl activewindow output")
        return None

    def get_previously_active_window(self):
        """Finds the window that was active before the manager app took focus."""
        clients = self.get_all_windows()
        # Sort by focusHistoryID (0 is current, 1 is previous)
        # We need the first one that is NOT the manager itself
        clients.sort(key=lambda x: x.get('focusHistoryID', 999))
        for c in clients:
            if c.get('class') != 'hypr-ws-manager':
                return c
        return None

    def make_floating_and_center(self):
        """Forces the workspace manager window to float, center, and resize."""
        selector = "class:^hypr-ws-manager$"
        self._run_command(["dispatch", "setfloating", selector])
        self._run_command(["dispatch", "resizewindowpixel", "exact 400 600", selector])
        self._run_command(["dispatch", "centerwindow", selector])
        self._run_command(["dispatch", "pin", selector])

    def get_all_windows(self):
        output = self._run_command(["clients", "-j"])
        if output:
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                logging.error("Failed to parse hyprctl clients output")
        return []

    def move_window_to_workspace(self, window_address, workspace_id):
        print(f"DEBUG: Moving {window_address} to {workspace_id}")
        self._run_command(["dispatch", "movetoworkspace", f"{workspace_id},address:{window_address}"])

    def close_window(self, address):
        """Closes a window by address."""
        self._run_command(["dispatch", "closewindow", f"address:{address}"])

    def focus_window(self, address):
        """Focuses a window by address."""
        self._run_command(["dispatch", "focuswindow", f"address:{address}"])

    def set_workspace_name(self, workspace_id, name):
        print(f"DEBUG: Renaming workspace {workspace_id} to {name}")
        self._run_command(["dispatch", "renameworkspace", str(workspace_id), name])

    def get_existing_workspace_ids(self):
        workspaces = self.get_workspaces()
        return [ws['id'] for ws in workspaces]
