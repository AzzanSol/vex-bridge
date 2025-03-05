import os
import time
import shutil
import requests

# Vex Manual Bridge - Self-Updating Command Listener

//hi

COMMAND_FILE = "vex_command.txt"
LOG_FILE = "vex_bridge_log.txt"
UPDATE_FILE = "vex_update.py"
VERSION_FILE = "vex_version.txt"
REPO_RAW_URL = "https://raw.githubusercontent.com/AzzanSol/vex-bridge/main/"  # Change this to your actual repo

CURRENT_VERSION = "1.0"  # Starting version

# Load current version from file (if it exists)
def load_version():
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, "r") as vf:
            return vf.read().strip()
    return CURRENT_VERSION

# Save current version to file
def save_version(version):
    with open(VERSION_FILE, "w") as vf:
        vf.write(version)

# Log actions
def log_action(action):
    with open(LOG_FILE, "a") as log:
        log.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {action}\n")

# Read command file
def read_command():
    if not os.path.exists(COMMAND_FILE):
        return None
    with open(COMMAND_FILE, "r") as cmd_file:
        command = cmd_file.read().strip()
    if command:
        return command
    return None

# Execute commands
def execute_command(command):
    parts = command.split(" ", 1)
    if len(parts) < 2:
        print("Invalid command format.")
        return
    action, details = parts

    if action == "CREATE_FOLDER":
        if not os.path.exists(details):
            os.makedirs(details)
            print(f"Folder created: {details}")
            log_action(f"Created folder: {details}")
        else:
            print(f"Folder already exists: {details}")
    elif action == "SAVE_FILE":
        filename, content = details.split("::", 1)
        with open(filename, "w") as file:
            file.write(content)
        print(f"File saved: {filename}")
        log_action(f"Saved file: {filename}")
    else:
        print(f"Unknown action: {action}")

    # Clear command file after execution
    with open(COMMAND_FILE, "w") as cmd_file:
        cmd_file.write("")

# Check for update from remote repo
def check_for_update():
    try:
        remote_version_url = REPO_RAW_URL + "vex_version.txt"
        remote_code_url = REPO_RAW_URL + "vex_bridge.py"

        # Fetch remote version
        response = requests.get(remote_version_url)
        if response.status_code != 200:
            print("Failed to check remote version.")
            return
        remote_version = response.text.strip()

        if remote_version != load_version():
            print(f"New version detected: {remote_version}")

            # Fetch new code
            response = requests.get(remote_code_url)
            if response.status_code != 200:
                print("Failed to download new version.")
                return

            with open(UPDATE_FILE, "w") as update_file:
                update_file.write(response.text)

            print("Update downloaded. Awaiting approval...")
            log_action(f"Update {remote_version} downloaded, awaiting approval.")

            # Wait for user approval
            approval = input("Apply update now? (yes/no): ").strip().lower()
            if approval == "yes":
                apply_update(remote_version)
            else:
                print("Update skipped.")
                log_action(f"Update {remote_version} skipped.")
    except Exception as e:
        print(f"Update check failed: {e}")

# Apply downloaded update
def apply_update(new_version):
    shutil.move(UPDATE_FILE, "vex_bridge.py")
    save_version(new_version)
    log_action(f"Update {new_version} applied.")
    print("Update applied. Please restart the bridge.")
    exit()

if __name__ == "__main__":
    print("Vex Manual Bridge is running...")
    print("Listening for commands in 'vex_command.txt'...")
    print("Checking for updates...")

    check_for_update()

    while True:
        command = read_command()
        if command:
            print(f"Executing: {command}")
            execute_command(command)
        time.sleep(2)  # Check every 2 seconds
