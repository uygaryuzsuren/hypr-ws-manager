import json
import os
from pathlib import Path

from shutil import which

class Config:
    DEFAULT_CONFIG = {
        "hyprctl_path": which("hyprctl") or "hyprctl",
        "theme": "dark",
        "transparency": 0.9,
        "workspace_names": {}
    }

    def __init__(self):
        self.config_dir = Path.home() / ".config" / "hypr-ws-manager"
        self.config_file = self.config_dir / "config.json"
        self.data = self.DEFAULT_CONFIG.copy()
        # Initialize original_titles if missing in legacy configs
        if "original_titles" not in self.data:
            self.data["original_titles"] = {}
        self.load()

    def load(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    loaded_data = json.load(f)
                    self.data.update(loaded_data)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config: {e}")
        else:
            self.save()

    def save(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.data, f, indent=2)
        except IOError as e:
            print(f"Error saving config: {e}")

    @property
    def hyprctl_path(self):
        return self.data.get("hyprctl_path", "hyprctl")

    @hyprctl_path.setter
    def hyprctl_path(self, value):
        self.data["hyprctl_path"] = value
        self.save()

    @property
    def theme(self):
        return self.data.get("theme", "dark")

    @theme.setter
    def theme(self, value):
        self.data["theme"] = value
        self.save()

    @property
    def transparency(self):
        return self.data.get("transparency", 0.9)

    @transparency.setter
    def transparency(self, value):
        self.data["transparency"] = value
        self.save()

    def get_workspace_name(self, ws_id):
        return self.data.get("workspace_names", {}).get(str(ws_id))

    def set_workspace_name(self, ws_id, name):
        if "workspace_names" not in self.data:
            self.data["workspace_names"] = {}
        self.data["workspace_names"][str(ws_id)] = name
        self.save()

    def set_original_title(self, ws_id, title):
        if "original_titles" not in self.data:
            self.data["original_titles"] = {}
        self.data["original_titles"][str(ws_id)] = title
        self.save()

    def get_original_title(self, ws_id):
        return self.data.get("original_titles", {}).get(str(ws_id))

    def remove_workspace_name(self, ws_id):
        if "workspace_names" in self.data and str(ws_id) in self.data["workspace_names"]:
            del self.data["workspace_names"][str(ws_id)]
        if "original_titles" in self.data and str(ws_id) in self.data["original_titles"]:
            del self.data["original_titles"][str(ws_id)]
        self.save()
