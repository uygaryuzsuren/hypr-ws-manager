#!/usr/bin/env python3
import os
import socket
import json
import time
import threading
import subprocess
from pathlib import Path

# Paths
CACHE_DIR = Path.home() / ".cache" / "hypr-ws-manager"
ACTIVITY_FILE = CACHE_DIR / "activity.json"
SUPPRESS_FILE = CACHE_DIR / "suppress.json"

def get_socket_path():
    runtime_dir = os.environ.get("XDG_RUNTIME_DIR")
    instance_sig = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
    if not runtime_dir or not instance_sig:
        return None
    return f"{runtime_dir}/hypr/{instance_sig}/.socket2.sock"

class ActivityTracker:
    def __init__(self):
        self.activity = {}
        self.lock = threading.Lock()
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.load_state()

    def load_state(self):
        if ACTIVITY_FILE.exists():
            try:
                with open(ACTIVITY_FILE, 'r') as f:
                    self.activity = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.activity = {}

    def save_state(self):
        with self.lock:
            try:
                # Atomic write
                temp_file = ACTIVITY_FILE.with_suffix(".tmp")
                with open(temp_file, 'w') as f:
                    json.dump(self.activity, f)
                temp_file.replace(ACTIVITY_FILE)
            except IOError:
                pass

    def update_activity(self, address):
        if not address: return
        # Ensure address is in 0x... format
        if not address.startswith("0x"):
            address = f"0x{address}"
        
        # Check for suppression
        if self.is_suppressed(address):
            print(f"DEBUG: Ignoring suppressed focus for {address}")
            return

        with self.lock:
            self.activity[address] = int(time.time())
        self.save_state()

    def is_suppressed(self, address):
        """Checks if a window address is in the suppression list and removes it if found."""
        if not SUPPRESS_FILE.exists():
            return False
            
        try:
            with open(SUPPRESS_FILE, 'r') as f:
                suppressed = json.load(f)
            
            if not isinstance(suppressed, list):
                return False

            if address in suppressed:
                suppressed.remove(address)
                # Atomic update of suppression file
                temp_file = SUPPRESS_FILE.with_suffix(".tmp")
                with open(temp_file, 'w') as f:
                    json.dump(suppressed, f)
                temp_file.replace(SUPPRESS_FILE)
                return True
        except (json.JSONDecodeError, IOError):
            pass
        return False

    def remove_window(self, address):
        if not address: return
        if not address.startswith("0x"):
            address = f"0x{address}"
        with self.lock:
            if address in self.activity:
                del self.activity[address]
        self.save_state()

    def initialize_existing_windows(self):
        """Seeds activity data for all currently open windows."""
        try:
            output = subprocess.check_output(["hyprctl", "clients", "-j"], text=True)
            clients = json.loads(output)
            now = int(time.time())
            with self.lock:
                for client in clients:
                    addr = client.get('address')
                    if addr and addr not in self.activity:
                        self.activity[addr] = now
            self.save_state()
            print(f"Initialized {len(clients)} existing windows with timestamp {now}")
        except (subprocess.CalledProcessError, json.JSONDecodeError, Exception) as e:
            print(f"Failed to initialize existing windows: {e}")

    def listen(self):
        # Seed data before listening
        self.initialize_existing_windows()

        sock_path = get_socket_path()
        if not sock_path:
            print("Hyprland socket not found. Is Hyprland running?")
            return

        while True:
            try:
                with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                    s.connect(sock_path)
                    print(f"Connected to {sock_path}")
                    while True:
                        data = s.recv(4096).decode('utf-8')
                        if not data:
                            break
                        
                        for line in data.split('\n'):
                            if not line: continue
                            
                            # focuswindow>>ADDRESS,TITLE
                            # activewindowv2>>ADDRESS
                            # closewindow>>ADDRESS
                            
                            if '>>' not in line: continue
                            event, payload = line.split('>>', 1)
                            
                            if event in ('focuswindow', 'activewindowv2'):
                                address = payload.split(',')[0]
                                self.update_activity(address)
                            elif event == 'closewindow':
                                self.remove_window(payload)
                                
            except (socket.error, Exception) as e:
                print(f"Socket error: {e}. Retrying in 5 seconds...")
                time.sleep(5)

if __name__ == "__main__":
    tracker = ActivityTracker()
    tracker.listen()
