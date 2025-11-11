import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import re
from pathlib import Path
import urllib.parse
import json
import urllib.request
import zipfile
import tarfile
import platform
import tempfile
import shutil

def detect_system_theme() -> str:
    try:
        import ctypes
        if os.name == 'nt':
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                   r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                winreg.CloseKey(key)
                return "light" if value == 1 else "dark"
            except:
                return "light"
        else:
            return "light"
    except:
        return "light"

def get_theme_colors(theme: str = None) -> dict:
    if theme is None:
        theme = detect_system_theme()
    
    if theme == "dark":
        return {
            'bg': '#1e1e1e', 'fg': '#ffffff', 'entry_bg': '#2d2d2d', 'button_bg': '#3c3c3c',
            'button_fg': '#ffffff', 'text_bg': '#2d2d2d', 'text_fg': '#ffffff',
            'accent': '#00b4d8', 'accent_hover': '#0099b8', 'border': '#404040',
            'success': '#4caf50', 'warning': '#ff9800', 'error': '#f44336',
            'secondary_bg': '#252525', 'hover_bg': '#404040'
        }
    else:
        return {
            'bg': '#f8f9fa', 'fg': '#212529', 'entry_bg': '#ffffff', 'button_bg': '#e9ecef',
            'button_fg': '#212529', 'text_bg': '#ffffff', 'text_fg': '#212529',
            'accent': '#007acc', 'accent_hover': '#005a9e', 'border': '#dee2e6',
            'success': '#28a745', 'warning': '#ffc107', 'error': '#dc3545',
            'secondary_bg': '#ffffff', 'hover_bg': '#f1f3f4'
        }

class ModernButton(tk.Button):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        
    def on_enter(self, event):
        self.configure(bg=self.master.master.colors['accent_hover'])
        
    def on_leave(self, event):
        self.configure(bg=self.master.master.colors['button_bg'])

class Earbound:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Earbound - Universal Music Downloader")
        self.root.geometry("700x600")
        
        self.theme = detect_system_theme()
        self.colors = get_theme_colors(self.theme)
        self.root.configure(bg=self.colors['bg'])
        
        self.root.resizable(True, True)
        self.root.minsize(600, 500)
        
        # Variables
        self.download_folder = tk.StringVar()
        self.link_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready to download")
        self.progress_var = tk.DoubleVar()
        self.theme_var = tk.StringVar(value="default")
        self.is_downloading = False
        self.current_process = None  # For cancel
        self.cancel_requested = False  # Flag

        self.setup_ui()
        self.apply_theme()
        self.check_dependencies()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        header_frame.columnconfigure(1, weight=1)
        
        title_label = ttk.Label(header_frame, text="EARBOUND", font=('Segoe UI', 24, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 5))
        subtitle_label = ttk.Label(header_frame, text="Bringing Back the MP3 Era", font=('Segoe UI', 12), foreground='gray')
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        
        theme_frame = ttk.Frame(header_frame)
        theme_frame.grid(row=2, column=0, columnspan=2, pady=(0, 10))
        ttk.Label(theme_frame, text="Theme:", font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=(0, 5))
        theme_combo = ttk.Combobox(theme_frame, textvariable=self.theme_var, values=["default", "light", "dark"], state="readonly", width=10)
        theme_combo.pack(side=tk.LEFT)
        theme_combo.bind('<<ComboboxSelected>>', self.on_theme_change)
        self.theme_label = ttk.Label(theme_frame, text=f"Current: {self.theme.title()}", font=('Segoe UI', 9), foreground=self.colors['accent'])
        self.theme_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Folder
        folder_frame = ttk.Frame(main_frame)
        folder_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        folder_frame.columnconfigure(1, weight=1)
        ttk.Label(folder_frame, text="Download Folder:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        folder_entry = ttk.Entry(folder_frame, textvariable=self.download_folder, font=('Segoe UI', 10))
        folder_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=5)
        browse_btn = ttk.Button(folder_frame, text="Browse", command=self.browse_folder, style='Accent.TButton')
        browse_btn.grid(row=0, column=2, padx=(5, 0), pady=5)
        
        # Link
        link_frame = ttk.Frame(main_frame)
        link_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        link_frame.columnconfigure(1, weight=1)
        ttk.Label(link_frame, text="Paste your music link here:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        link_entry = ttk.Entry(link_frame, textvariable=self.link_var, font=('Segoe UI', 10))
        link_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=5)
        link_entry.bind('<Return>', lambda e: self.start_download())
        platforms_label = ttk.Label(link_frame, text="Supported: Spotify, YouTube, YouTube Music (Tracks, Albums & Playlists)", font=('Segoe UI', 9), foreground='gray')
        platforms_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(5, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=15)
        
        self.download_btn = ttk.Button(button_frame, text="Download Music", command=self.start_download, style='Accent.TButton')
        self.download_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # CANCEL BUTTON ADDED HERE
        self.cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.cancel_download, style='Accent.TButton')
        self.cancel_btn.pack(side=tk.LEFT, padx=(0, 10))
        self.cancel_btn.config(state='disabled')  # Disabled until download starts
        
        clear_btn = ttk.Button(button_frame, text="Clear Log", command=self.clear_log)
        clear_btn.pack(side=tk.LEFT, padx=(0, 10))
        open_folder_btn = ttk.Button(button_frame, text="Open Folder", command=self.open_download_folder)
        open_folder_btn.pack(side=tk.LEFT)
        
        # Progress
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        progress_frame.columnconfigure(0, weight=1)
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100, length=500, style='Accent.Horizontal.TProgressbar')
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.status_label = ttk.Label(progress_frame, textvariable=self.status_var, font=('Segoe UI', 10))
        self.status_label.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Log
        log_frame = ttk.Frame(main_frame)
        log_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        self.log_text = tk.Text(log_frame, height=10, width=80, font=('Consolas', 9), wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        main_frame.rowconfigure(5, weight=1)
        
        # Default folder
        default_folder = str(Path.home() / "Music" / "Earbound")
        if not os.path.exists(default_folder):
            music_folder = Path.home() / "Music"
            if music_folder.exists():
                default_folder = str(music_folder / "Earbound")
            else:
                default_folder = str(Path.home() / "Documents" / "Earbound")
        self.download_folder.set(default_folder)
        
    def apply_theme(self):
        if self.theme_var.get() == "default":
            self.theme = detect_system_theme()
        else:
            self.theme = self.theme_var.get()
        self.colors = get_theme_colors(self.theme)
        self.root.configure(bg=self.colors['bg'])
        self.theme_label.configure(text=f"Current: {self.theme.title()}", foreground=self.colors['accent'])
        self.log_text.configure(bg=self.colors['text_bg'], fg=self.colors['text_fg'], insertbackground=self.colors['fg'], selectbackground=self.colors['accent'], selectforeground=self.colors['text_bg'])
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background=self.colors['bg'])
        style.configure('TLabel', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('TButton', background=self.colors['button_bg'], foreground=self.colors['button_fg'], borderwidth=1, focuscolor='none')
        style.configure('Accent.TButton', background=self.colors['accent'], foreground=self.colors['text_bg'], borderwidth=1, focuscolor='none')
        style.configure('TEntry', fieldbackground=self.colors['entry_bg'], foreground=self.colors['fg'], borderwidth=1)
        style.configure('TCombobox', fieldbackground=self.colors['entry_bg'], background=self.colors['entry_bg'], foreground=self.colors['fg'], borderwidth=1)
        style.configure('TLabelframe', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('TLabelframe.Label', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('TProgressbar', background=self.colors['accent'], troughcolor=self.colors['secondary_bg'])
        style.configure('Accent.Horizontal.TProgressbar', background=self.colors['accent'], troughcolor=self.colors['secondary_bg'])

    def on_theme_change(self, event=None):
        self.apply_theme()

    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select Download Folder")
        if folder:
            self.download_folder.set(folder)

    def log_message(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
        self.log_message("Log cleared")

    def open_download_folder(self):
        folder = self.download_folder.get().strip()
        if folder and os.path.exists(folder):
            try:
                if os.name == 'nt':
                    os.startfile(folder)
                elif os.name == 'posix':
                    subprocess.run(['open', folder] if sys.platform == 'darwin' else ['xdg-open', folder])
                self.log_message(f"Opened folder: {folder}")
            except Exception as e:
                self.log_message(f"Could not open folder: {str(e)}")
        else:
            self.log_message("Download folder does not exist")

    def check_dependencies(self):
        self.log_message("Checking dependencies...")
        self.ffmpeg_path = None
        if not self._check_spotdl():
            if not self._install_spotdl():
                self.log_message("spotdl installation failed")
        if not self._check_ytdlp():
            if not self._install_ytdlp():
                self.log_message("yt-dlp installation failed")
        if not self._check_ffmpeg():
            if not self._download_ffmpeg():
                self.log_message("FFmpeg download failed")
        self.log_message("Ready to download!")

    def _check_spotdl(self):
        try:
            result = subprocess.run(["spotdl", "--version"], capture_output=True, check=True, timeout=5, text=True)
            self.log_message(f"spotdl ready ({result.stdout.strip()})")
            return True
        except:
            return False

    def _check_ytdlp(self):
        try:
            result = subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True, timeout=5, text=True)
            self.log_message(f"yt-dlp ready ({result.stdout.strip()})")
            return True
        except:
            return False

    def _check_ffmpeg(self):
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True, timeout=3)
            self.ffmpeg_path = "ffmpeg"
            self.log_message("FFmpeg in PATH")
            return True
        except:
            bin_dir = Path(__file__).parent / "bin"
            local = bin_dir / ("ffmpeg.exe" if os.name == 'nt' else "ffmpeg")
            if local.exists():
                self.ffmpeg_path = str(local)
                self.log_message("Local FFmpeg found")
                return True
            return False

    def _install_spotdl(self):
        self.log_message("Installing spotdl...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True, timeout=30)
            subprocess.run([sys.executable, "-m", "pip", "install", "spotdl"], check=True, timeout=120)
            return self._check_spotdl()
        except:
            return False

    def _install_ytdlp(self):
        self.log_message("Installing yt-dlp...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True, timeout=30)
            subprocess.run([sys.executable, "-m", "pip", "install", "yt-dlp"], check=True, timeout=60)
            return self._check_ytdlp()
        except:
            return False

    def _download_ffmpeg(self):
        self.log_message("Downloading FFmpeg...")
        try:
            bin_dir = Path(__file__).parent / "bin"
            bin_dir.mkdir(exist_ok=True)
            system = platform.system().lower()
            if system == "windows":
                url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
                zip_path = bin_dir / "ffmpeg.zip"
                urllib.request.urlretrieve(url, zip_path)
                with zipfile.ZipFile(zip_path, 'r') as z:
                    for f in z.namelist():
                        if "ffmpeg.exe" in f:
                            z.extract(f, bin_dir)
                            shutil.move(str(bin_dir / f), str(bin_dir / "ffmpeg.exe"))
                            break
                zip_path.unlink()
            # ... (rest of download logic same as yours)
            return self._check_ffmpeg()
        except:
            return False

    def validate_link(self, link):
        if not link.strip(): return False, "Enter a link"
        if re.search(r'spotify\.com', link, re.IGNORECASE):
            return True, f"spotify_{self._detect_spotify_content_type(link)}"
        if re.search(r'(youtube\.com|youtu\.be|music\.youtube\.com)', link, re.IGNORECASE):
            return True, f"youtube_{self._detect_youtube_content_type(link)}"
        return False, "Unsupported link"

    def _detect_spotify_content_type(self, link):
        if '/playlist/' in link: return "playlist"
        if '/album/' in link: return "album"
        return "track"

    def _detect_youtube_content_type(self, link):
        if re.search(r'[?&]list=|/playlist', link): return "playlist"
        return "video"

    def _get_organized_download_path(self, base_path, link_type, link):
        base = Path(base_path)
        if link_type.startswith("spotify_playlist") or link_type.startswith("spotify_album"):
            path = base / "Spotify_Playlist"
            path.mkdir(exist_ok=True)
            return str(path)
        if link_type.startswith("youtube_playlist"):
            name = self._get_youtube_playlist_name(link) or "Playlist"
            path = base / "YouTube_Playlist" / self._sanitize_filename(name)
            path.mkdir(parents=True, exist_ok=True)
            return str(path)
        return str(base)

    def _get_youtube_playlist_name(self, link):
        try:
            r = subprocess.run(["yt-dlp", "--print", "%(playlist_title)s", "--playlist-items", "1", link], capture_output=True, text=True, timeout=10)
            return r.stdout.strip().split('\n')[0] if r.returncode == 0 else None
        except: return None

    def _sanitize_filename(self, s):
        s = re.sub(r'[<>:"/\\|?*]', '_', s)
        s = re.sub(r'\s+', ' ', s).strip()
        return s[:100]

    def start_download(self):
        if self.is_downloading: return
        if not self.download_folder.get().strip():
            messagebox.showerror("Error", "Select folder")
            return
        if not self.link_var.get().strip():
            messagebox.showerror("Error", "Enter link")
            return
        valid, link_type = self.validate_link(self.link_var.get())
        if not valid:
            messagebox.showerror("Error", link_type)
            return

        self.is_downloading = True
        self.cancel_requested = False
        self.download_btn.config(state='disabled')
        self.cancel_btn.config(state='normal')  # Enable cancel
        self.progress_var.set(0)
        self.status_var.set("Starting...")
        self.current_process = None

        threading.Thread(target=self.download_music, args=(link_type,), daemon=True).start()

    def cancel_download(self):
        if not self.is_downloading: return
        self.cancel_requested = True
        self.log_message("Cancelling download...")
        self.status_var.set("Cancelling...")
        if self.current_process:
            try:
                if os.name == 'nt':
                    subprocess.run(['taskkill', '/F', '/T', '/PID', str(self.current_process.pid)], capture_output=True)
                else:
                    import signal
                    os.killpg(os.getpgid(self.current_process.pid), signal.SIGTERM)
            except: pass

    def download_music(self, link_type):
        try:
            link = self.link_var.get().strip()
            base_path = self.download_folder.get().strip()
            os.makedirs(base_path, exist_ok=True)
            download_path = self._get_organized_download_path(base_path, link_type, link)

            self.log_message(f"Starting {link_type} download...")
            self.log_message(f"Path: {download_path}")

            if link_type.startswith("spotify"):
                self._run_spotify(link, download_path)
            else:
                self._run_youtube(link, download_path)

            if not self.cancel_requested:
                self.log_message("Download complete!")
                self.status_var.set("Complete")
                self.progress_var.set(100)
                messagebox.showinfo("Success", "Done!")
        except Exception as e:
            if not self.cancel_requested:
                self.log_message(f"Error: {e}")
                messagebox.showerror("Error", str(e))
        finally:
            self.is_downloading = False
            self.download_btn.config(state='normal')
            self.cancel_btn.config(state='disabled')
            self.current_process = None

    def _run_spotify(self, link, path):
        cmd = ["spotdl", "download", link, "--output", path, "--format", "mp3"]
        if self.ffmpeg_path and self.ffmpeg_path != "ffmpeg":
            cmd += ["--ffmpeg", self.ffmpeg_path]
        self._run_process(cmd)

    def _run_youtube(self, link, path):
        cmd = ["yt-dlp", "--format", "bestaudio", "--output", f"{path}/%(title)s.%(ext)s", "--ignore-errors"]
        if self.ffmpeg_path and self.ffmpeg_path != "ffmpeg":
            cmd += ["--ffmpeg-location", self.ffmpeg_path]
        cmd += ["--extract-audio", "--audio-format", "mp3"]
        cmd.append(link)
        self._run_process(cmd)

    def _run_process(self, cmd):
        self.current_process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1, preexec_fn=os.setsid if os.name != 'nt' else None
        )
        for line in self.current_process.stdout:
            if self.cancel_requested: break
            line = line.strip()
            if line: self.log_message(line)
            if "download:" in line.lower():
                m = re.search(r'(\d+(?:\.\d+)?)%', line)
                if m:
                    p = float(m.group(1))
                    self.progress_var.set(20 + p * 0.7)
        self.current_process.wait()
        if self.current_process.returncode != 0 and not self.cancel_requested:
            raise Exception("Process failed")

    def run(self):
        self.root.mainloop()

def main():
    try:
        app = Earbound()
        app.run()
    except Exception as e:
        messagebox.showerror("Error", f"Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
