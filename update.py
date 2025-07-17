import requests
import os
import argparse

DEFAULT_VERSION_URL = "https://raw.githubusercontent.com/rock3tsprocket/cube/refs/heads/main/current_version.json"
LOCAL_VERSION_FILE = "current_version.json"
SCRIPT_FILE = "bot.py"

choice = input("This updater is not recommended for use, especially if you already cloned Cube from GitHub. In that case, run \"git pull\". If you're sure you want to use this (for example if you can't use Git), you can continue anyway. [y/N] ")
if choice == "y" or choice == "Y":
    def get_latest_version_info(DEFAULT_VERSION_URL):
        """Fetch the latest version information from the server."""
        try:
            global response
            response = requests.get(DEFAULT_VERSION_URL, timeout=5)
            response.raise_for_status()  # Will raise HTTPError for bad responses
            return response.json()
        except requests.RequestException as e:
            print(f"Error: Unable to connect to the update server. {e}")
            return None

    def get_local_version():
        """Read the current version from the local file."""
        if os.path.exists(LOCAL_VERSION_FILE):
            with open(LOCAL_VERSION_FILE, "r") as f:
                return json.loads(f.read().strip())["version"]
        return "0.0.0"

    def save_local_version(version):
        """Save the current version to the local file."""
        with open(LOCAL_VERSION_FILE, "w") as f:
            f.write(version)

    def download_file(url, destination):
        """Download a file from the given URL and save it to the destination."""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Will raise HTTPError for bad responses
            with open(destination, "wb") as f:
                f.write(response.content)
            print(f"Successfully downloaded the file to {destination}.")
        except requests.RequestException as e:
            print(f"Error: Failed to download the file from {url}. {e}")

    def check_for_update(DEFAULT_VERSION_URL):
        """Check if a new version is available and update the script if needed."""
        latest_version_info = get_latest_version_info(DEFAULT_VERSION_URL)
        if not latest_version_info:
            print("Could not fetch update information.")
            return
        latest_version = latest_version_info.get("version")
        download_url = "https://raw.githubusercontent.com/rock3tsprocket/cube/refs/heads/main/bot.py"
        example_env = "https://raw.githubusercontent.com/rock3tsprocket/cube/refs/heads/main/example.env"
        if not latest_version or not download_url or not example_env:
            print("Error: Invalid version information received from server.")
        local_version = get_local_version()
        if local_version != latest_version:
            print(f"New version available: {latest_version} (Current: {local_version})")
            print("Downloading the new version...")
            download_file(download_url, SCRIPT_FILE)
            if not os.path.exists(".env"):
                download_file(example_env, "example.env")
            save_local_version(response.text)
            print("Update complete! Restart the bot to use the new version, or if you downloaded it for the first time, modify example.env and rename it to .env.\nIf you want, go check out the cogs at https://github.com/rock3tsprocket/cube/tree/main/cogs!")
            if not os.path.exists("cogs/"):
                os.mkdir("cogs")
                return
        else:
            print(f"You're using the latest version: {local_version}")

    if __name__ == "__main__":
        parser = argparse.ArgumentParser(description="Check for updates and download the latest version of the bot.")
        parser.add_argument("--host", type=str, help="Custom version URL", default=DEFAULT_VERSION_URL)

    args = parser.parse_args()
    check_for_update(args.host)
else:
    exit(0)
