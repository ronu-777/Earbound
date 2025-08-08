import os
import subprocess
import sys

# Try to import tkinter for folder selection
try:
    from tkinter import Tk, filedialog
except ImportError:
    print("\n🚫 'tkinter' not found. Install Python from https://www.python.org/downloads")
    input("Press Enter to exit...")
    sys.exit()

def install_spotdl():
    try:
        print("🧪 Checking for spotDL...")
        subprocess.run(["spotdl", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ spotDL is already installed.\n")
    except FileNotFoundError:
        print("📦 spotDL not found. Installing now...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "spotdl"])
        print("✅ spotDL installed successfully!\n")

def choose_download_folder():
    print("\n📁 Choose where to save your downloads...")

    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    selected_path = filedialog.askdirectory(title="Select Download Location")
    root.destroy()

    if not selected_path:
        print("❌ No folder selected. Exiting.")
        input("Press Enter to exit...")
        sys.exit()

    return selected_path

def main():
    print("🎵 Universal Spotify Downloader with spotDL\n")

    install_spotdl()

    # Ask for Spotify content URL (track, album, artist, playlist)
    spotify_url = input("🔗 Paste any Spotify link (track, album, playlist, or artist): ").strip()

    if not spotify_url.startswith("https://open.spotify.com/"):
        print("❌ Invalid Spotify URL.")
        input("Press Enter to exit...")
        return

    # Pick folder
    download_path = choose_download_folder()

    # Build command
    cmd = ["spotdl", spotify_url, "--output", download_path]

    try:
        print(f"\n📥 Downloading into:\n{download_path}\n")
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        print(result.stderr)
        print(f"\n✅ Done! Songs saved in:\n{download_path}")
    except Exception as e:
        print("❌ Something went wrong:", e)

    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
