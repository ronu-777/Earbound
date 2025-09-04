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
    """Detect system theme (dark/light)"""
    try:
        import ctypes
        if os.name == 'nt':  # Windows
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                   r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                winreg.CloseKey(key)
                return "light" if value == 1 else "dark"
            except:
                return "light"  # Default fallback
        else:  # macOS/Linux
            return "light"  # Default fallback
    except:
        return "light"  # Default fallback

def get_theme_colors(theme: str = None) -> dict:
    """Get color scheme based on theme"""
    if theme is None:
        theme = detect_system_theme()
    
    if theme == "dark":
        return {
            'bg': '#1e1e1e',
            'fg': '#ffffff',
            'entry_bg': '#2d2d2d',
            'button_bg': '#3c3c3c',
            'button_fg': '#ffffff',
            'text_bg': '#2d2d2d',
            'text_fg': '#ffffff',
            'accent': '#00b4d8',
            'accent_hover': '#0099b8',
            'border': '#404040',
            'success': '#4caf50',
            'warning': '#ff9800',
            'error': '#f44336',
            'secondary_bg': '#252525',
            'hover_bg': '#404040'
        }
    else:  # light theme
        return {
            'bg': '#f8f9fa',
            'fg': '#212529',
            'entry_bg': '#ffffff',
            'button_bg': '#e9ecef',
            'button_fg': '#212529',
            'text_bg': '#ffffff',
            'text_fg': '#212529',
            'accent': '#007acc',
            'accent_hover': '#005a9e',
            'border': '#dee2e6',
            'success': '#28a745',
            'warning': '#ffc107',
            'error': '#dc3545',
            'secondary_bg': '#ffffff',
            'hover_bg': '#f1f3f4'
        }

class ModernButton(tk.Button):
    """Custom modern button with hover effects"""
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
        self.root.title("🎵 Earbound - Universal Music Downloader")
        self.root.geometry("700x600")
        
        # Detect system theme and apply colors
        self.theme = detect_system_theme()
        self.colors = get_theme_colors(self.theme)
        self.root.configure(bg=self.colors['bg'])
        
        # Set icon and make it look modern
        self.root.resizable(True, True)
        self.root.minsize(600, 500)
        
        # Variables
        self.download_folder = tk.StringVar()
        self.link_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready to download")
        self.progress_var = tk.DoubleVar()
        self.theme_var = tk.StringVar(value="default")
        self.is_downloading = False
        
        self.setup_ui()
        self.apply_theme()
        self.check_dependencies()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Header frame
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        header_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(header_frame, text="🎵 EARBOUND 🎵", 
                               font=('Segoe UI', 24, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 5))
        
        # Subtitle
        subtitle_label = ttk.Label(header_frame, text="Bringing Back the MP3 Era", 
                                  font=('Segoe UI', 12), foreground='gray')
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        
        # Theme selector
        theme_frame = ttk.Frame(header_frame)
        theme_frame.grid(row=2, column=0, columnspan=2, pady=(0, 10))
        
        ttk.Label(theme_frame, text="Theme:", font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=(0, 5))
        
        theme_combo = ttk.Combobox(theme_frame, textvariable=self.theme_var, 
                                  values=["default", "light", "dark"], 
                                  state="readonly", width=10)
        theme_combo.pack(side=tk.LEFT)
        theme_combo.bind('<<ComboboxSelected>>', self.on_theme_change)
        
        # Current theme indicator
        self.theme_label = ttk.Label(theme_frame, text=f"Current: {self.theme.title()}", 
                                    font=('Segoe UI', 9), foreground=self.colors['accent'])
        self.theme_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Download folder selection
        folder_frame = ttk.Frame(main_frame)
        folder_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        folder_frame.columnconfigure(1, weight=1)
        
        ttk.Label(folder_frame, text="Download Folder:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        folder_entry = ttk.Entry(folder_frame, textvariable=self.download_folder, font=('Segoe UI', 10))
        folder_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=5)
        
        browse_btn = ttk.Button(folder_frame, text="Browse", command=self.browse_folder, style='Accent.TButton')
        browse_btn.grid(row=0, column=2, padx=(5, 0), pady=5)
        
        # Link input section
        link_frame = ttk.Frame(main_frame)
        link_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        link_frame.columnconfigure(1, weight=1)
        
        ttk.Label(link_frame, text="Paste your music link here:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        link_entry = ttk.Entry(link_frame, textvariable=self.link_var, font=('Segoe UI', 10))
        link_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=5)
        link_entry.bind('<Return>', lambda e: self.start_download())  # Press Enter to download
        
        # Supported platforms info
        platforms_text = "Supported: Spotify, YouTube, YouTube Music (Tracks, Albums & Playlists)"
        platforms_label = ttk.Label(link_frame, text=platforms_text, 
                                   font=('Segoe UI', 9), foreground='gray')
        platforms_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(5, 0))
        
        # Download button
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=15)
        
        self.download_btn = ttk.Button(button_frame, text="🎵 Download Music", 
                                      command=self.start_download, style='Accent.TButton')
        self.download_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear log button
        clear_btn = ttk.Button(button_frame, text="🗑️ Clear Log", 
                              command=self.clear_log)
        clear_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Open folder button
        open_folder_btn = ttk.Button(button_frame, text="📁 Open Folder", 
                                    command=self.open_download_folder)
        open_folder_btn.pack(side=tk.LEFT)
        
        # Progress section
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        progress_frame.columnconfigure(0, weight=1)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, length=500, style='Accent.Horizontal.TProgressbar')
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(progress_frame, textvariable=self.status_var, 
                                     font=('Segoe UI', 10))
        self.status_label.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Log area
        log_frame = ttk.Frame(main_frame)
        log_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Text widget for logs with better styling
        self.log_text = tk.Text(log_frame, height=10, width=80, 
                               font=('Consolas', 9), wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure main frame row weights
        main_frame.rowconfigure(5, weight=1)
        
        # Set default download folder
        default_folder = str(Path.home() / "Music" / "Earbound")
        if not os.path.exists(default_folder):
            # Try Music/Earbound first
            music_folder = Path.home() / "Music"
            if music_folder.exists():
                default_folder = str(music_folder / "Earbound")
            else:
                # Fallback to Documents/Earbound
                default_folder = str(Path.home() / "Documents" / "Earbound")
        self.download_folder.set(default_folder)
        
    def apply_theme(self):
        """Apply the current theme to all widgets"""
        # Update colors based on theme
        if self.theme_var.get() == "default":
            self.theme = detect_system_theme()
        else:
            self.theme = self.theme_var.get()
            
        self.colors = get_theme_colors(self.theme)
        
        # Apply to root window
        self.root.configure(bg=self.colors['bg'])
        
        # Update theme label
        self.theme_label.configure(text=f"Current: {self.theme.title()}", foreground=self.colors['accent'])
        
        # Apply to text widget
        self.log_text.configure(
            bg=self.colors['text_bg'],
            fg=self.colors['text_fg'],
            insertbackground=self.colors['fg'],
            selectbackground=self.colors['accent'],
            selectforeground=self.colors['text_bg']
        )
        
        # Configure ttk styles
        style = ttk.Style()
        style.theme_use('clam')  # Use clam theme as base
        
        # Configure colors for ttk widgets
        style.configure('TFrame', background=self.colors['bg'])
        style.configure('TLabel', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('TButton', 
                       background=self.colors['button_bg'], 
                       foreground=self.colors['button_fg'],
                       borderwidth=1,
                       focuscolor='none')
        style.configure('Accent.TButton', 
                       background=self.colors['accent'], 
                       foreground=self.colors['text_bg'],
                       borderwidth=1,
                       focuscolor='none')
        style.configure('TEntry', 
                       fieldbackground=self.colors['entry_bg'],
                       foreground=self.colors['fg'],
                       borderwidth=1)
        style.configure('TCombobox', 
                       fieldbackground=self.colors['entry_bg'],
                       background=self.colors['entry_bg'],
                       foreground=self.colors['fg'],
                       borderwidth=1)
        style.configure('TLabelframe', 
                       background=self.colors['bg'],
                       foreground=self.colors['fg'])
        style.configure('TLabelframe.Label', 
                       background=self.colors['bg'],
                       foreground=self.colors['fg'])
        style.configure('TProgressbar', 
                       background=self.colors['accent'],
                       troughcolor=self.colors['secondary_bg'])
        style.configure('Accent.Horizontal.TProgressbar', 
                       background=self.colors['accent'],
                       troughcolor=self.colors['secondary_bg'])
        
    def on_theme_change(self, event=None):
        """Handle theme change"""
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
        """Clear the log text area"""
        self.log_text.delete(1.0, tk.END)
        self.log_message("📝 Log cleared")
        
    def open_download_folder(self):
        """Open the download folder in file explorer"""
        folder = self.download_folder.get().strip()
        if folder and os.path.exists(folder):
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(folder)
                elif os.name == 'posix':  # macOS/Linux
                    subprocess.run(['open', folder] if sys.platform == 'darwin' else ['xdg-open', folder])
                self.log_message(f"📁 Opened folder: {folder}")
            except Exception as e:
                self.log_message(f"❌ Could not open folder: {str(e)}")
        else:
            self.log_message("❌ Download folder does not exist")
        
    def check_dependencies(self):
        """Check if required packages are available and auto-install if missing"""
        self.log_message("🔍 Checking dependencies...")

        # Initialize ffmpeg path
        self.ffmpeg_path = None

        # Check and install spotdl
        if not self._check_spotdl():
            if not self._install_spotdl():
                self.log_message("⚠️ spotdl installation failed - Spotify downloads may not work")

        # Check and install yt-dlp
        if not self._check_ytdlp():
            if not self._install_ytdlp():
                self.log_message("⚠️ yt-dlp installation failed - YouTube downloads may not work")

        # Check FFmpeg and auto-download if needed
        if not self._check_ffmpeg():
            if not self._download_ffmpeg():
                self.log_message("⚠️ FFmpeg download failed - MP3 conversion may not work")

        self.log_message("🚀 Ready to download!")

    def _check_spotdl(self):
        """Check if spotdl is available"""
        try:
            result = subprocess.run(["spotdl", "--version"], capture_output=True, check=True, timeout=5, text=True)
            version = result.stdout.strip()
            self.log_message(f"✅ spotdl is available (version: {version})")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired, OSError):
            return False

    def _check_ytdlp(self):
        """Check if yt-dlp is available"""
        try:
            result = subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True, timeout=5, text=True)
            version = result.stdout.strip()
            self.log_message(f"✅ yt-dlp is available (version: {version})")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired, OSError):
            return False

    def _check_ffmpeg(self):
        """Check if FFmpeg is available"""
        # First check system FFmpeg
        try:
            result = subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True, timeout=3, text=True)
            self.ffmpeg_path = "ffmpeg"  # Use system ffmpeg
            self.log_message("✅ FFmpeg is available for MP3 conversion")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired, OSError):
            pass

        # Check for local FFmpeg binary
        bin_dir = Path(__file__).parent / "bin"
        local_ffmpeg = bin_dir / ("ffmpeg.exe" if os.name == 'nt' else "ffmpeg")

        if local_ffmpeg.exists():
            try:
                result = subprocess.run([str(local_ffmpeg), "-version"], capture_output=True, check=True, timeout=3, text=True)
                self.ffmpeg_path = str(local_ffmpeg)
                self.log_message("✅ Local FFmpeg binary found")
                return True
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
                pass

        self.log_message("ℹ️ FFmpeg not found - will attempt to download automatically")
        return False

    def _install_spotdl(self):
        """Install spotdl"""
        self.log_message("📦 Installing spotdl...")
        try:
            # Upgrade pip first
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
                          capture_output=True, check=True, timeout=30)

            # Install spotdl
            result = subprocess.run([sys.executable, "-m", "pip", "install", "spotdl"],
                                   capture_output=True, check=True, timeout=120, text=True)

            # Verify installation
            if self._check_spotdl():
                self.log_message("✅ spotdl installed successfully")
                return True
            else:
                self.log_message("❌ spotdl installation verification failed")
                return False

        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            self.log_message(f"❌ Failed to install spotdl: {str(e)}")
            self.log_message("💡 Please install manually: pip install spotdl")
            return False

    def _install_ytdlp(self):
        """Install yt-dlp"""
        self.log_message("📦 Installing yt-dlp...")
        try:
            # Upgrade pip first
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
                          capture_output=True, check=True, timeout=30)

            # Install yt-dlp
            result = subprocess.run([sys.executable, "-m", "pip", "install", "yt-dlp"],
                                   capture_output=True, check=True, timeout=60, text=True)

            # Verify installation
            if self._check_ytdlp():
                self.log_message("✅ yt-dlp installed successfully")
                return True
            else:
                self.log_message("❌ yt-dlp installation verification failed")
                return False

        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            self.log_message(f"❌ Failed to install yt-dlp: {str(e)}")
            self.log_message("💡 Please install manually: pip install yt-dlp")
            return False

    def _download_ffmpeg(self):
        """Download static FFmpeg binary for the current platform"""
        self.log_message("📥 Downloading FFmpeg...")

        try:
            bin_dir = Path(__file__).parent / "bin"
            bin_dir.mkdir(exist_ok=True)

            system = platform.system().lower()
            machine = platform.machine().lower()

            if system == "windows":
                # Windows FFmpeg download
                url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
                zip_path = bin_dir / "ffmpeg.zip"

                self.log_message("📥 Downloading FFmpeg for Windows...")
                urllib.request.urlretrieve(url, zip_path, self._download_progress)

                self.log_message("📦 Extracting FFmpeg...")
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    # Find the ffmpeg.exe in the extracted files
                    for file_info in zip_ref.filelist:
                        if file_info.filename.endswith('ffmpeg.exe'):
                            # Extract just the ffmpeg.exe file
                            with zip_ref.open(file_info) as source, open(bin_dir / "ffmpeg.exe", "wb") as target:
                                shutil.copyfileobj(source, target)
                            break

                zip_path.unlink()  # Delete the zip file

            elif system == "linux":
                # Linux FFmpeg download (Ubuntu/Debian static build)
                if "x86_64" in machine or "amd64" in machine:
                    url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
                else:
                    url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-i686-static.tar.xz"

                tar_path = bin_dir / "ffmpeg.tar.xz"

                self.log_message("📥 Downloading FFmpeg for Linux...")
                urllib.request.urlretrieve(url, tar_path, self._download_progress)

                self.log_message("📦 Extracting FFmpeg...")
                with tarfile.open(tar_path, 'r:xz') as tar_ref:
                    # Find and extract ffmpeg binary
                    for member in tar_ref.getmembers():
                        if member.name.endswith('/ffmpeg') and member.isfile():
                            with tar_ref.extractfile(member) as source, open(bin_dir / "ffmpeg", "wb") as target:
                                shutil.copyfileobj(source, target)
                            # Make executable
                            os.chmod(bin_dir / "ffmpeg", 0o755)
                            break

                tar_path.unlink()  # Delete the tar file

            elif system == "darwin":  # macOS
                # macOS FFmpeg download
                url = "https://evermeet.cx/ffmpeg/ffmpeg-5.1.2.zip"
                zip_path = bin_dir / "ffmpeg.zip"

                self.log_message("📥 Downloading FFmpeg for macOS...")
                urllib.request.urlretrieve(url, zip_path, self._download_progress)

                self.log_message("📦 Extracting FFmpeg...")
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    # Extract ffmpeg binary
                    with zip_ref.open('ffmpeg') as source, open(bin_dir / "ffmpeg", "wb") as target:
                        shutil.copyfileobj(source, target)
                    # Make executable
                    os.chmod(bin_dir / "ffmpeg", 0o755)

                zip_path.unlink()  # Delete the zip file

            else:
                self.log_message(f"❌ Unsupported platform: {system}")
                return False

            # Verify the downloaded FFmpeg
            if self._check_ffmpeg():
                self.log_message("✅ FFmpeg downloaded and ready!")
                return True
            else:
                self.log_message("❌ FFmpeg download verification failed")
                return False

        except Exception as e:
            self.log_message(f"❌ Failed to download FFmpeg: {str(e)}")
            return False

    def _download_progress(self, block_num, block_size, total_size):
        """Show download progress for FFmpeg"""
        if total_size > 0:
            downloaded = block_num * block_size
            percent = min(100, (downloaded / total_size) * 100)
            self.status_var.set(f"Downloading FFmpeg... {percent:.1f}%")
            self.root.update_idletasks()
                    
    def validate_link(self, link):
        """Validate if the link is supported and detect content type"""
        if not link.strip():
            return False, "Please enter a link"

        # Check for Spotify links
        if re.search(r'spotify\.com', link, re.IGNORECASE):
            content_type = self._detect_spotify_content_type(link)
            return True, f"spotify_{content_type}"

        # Check for YouTube links
        if re.search(r'(youtube\.com|youtu\.be|music\.youtube\.com)', link, re.IGNORECASE):
            content_type = self._detect_youtube_content_type(link)
            return True, f"youtube_{content_type}"

        return False, "Unsupported link. Please provide a Spotify or YouTube link."

    def _detect_spotify_content_type(self, link):
        """Detect if Spotify link is for playlist, album, or single track"""
        if re.search(r'/playlist/', link, re.IGNORECASE):
            return "playlist"
        elif re.search(r'/album/', link, re.IGNORECASE):
            return "album"
        elif re.search(r'/track/', link, re.IGNORECASE):
            return "track"
        else:
            # Default to track for other Spotify links
            return "track"

    def _detect_youtube_content_type(self, link):
        """Detect if YouTube link is for playlist or single video"""
        if re.search(r'[?&]list=', link, re.IGNORECASE) or re.search(r'/playlist', link, re.IGNORECASE):
            return "playlist"
        else:
            return "video"

    def _get_organized_download_path(self, base_path, link_type, link):
        """Get organized download path based on content type"""
        try:
            base_path = Path(base_path)

            if link_type.startswith("spotify_playlist") or link_type.startswith("spotify_album"):
                # Spotify playlists and albums go into Spotify_Playlist folder
                organized_path = base_path / "Spotify_Playlist"
                organized_path.mkdir(exist_ok=True)
                return str(organized_path)

            elif link_type.startswith("youtube_playlist"):
                # YouTube playlists need playlist name detection
                playlist_name = self._get_youtube_playlist_name(link)
                if playlist_name:
                    organized_path = base_path / "YouTube_Playlist" / self._sanitize_filename(playlist_name)
                    organized_path.mkdir(parents=True, exist_ok=True)
                    return str(organized_path)
                else:
                    # Fallback to generic YouTube_Playlist folder
                    organized_path = base_path / "YouTube_Playlist"
                    organized_path.mkdir(exist_ok=True)
                    return str(organized_path)

            else:
                # Single tracks/videos go to main folder
                return str(base_path)

        except Exception as e:
            self.log_message(f"⚠️ Error organizing folders: {str(e)}, using base path")
            return str(base_path)

    def _get_youtube_playlist_name(self, link):
        """Try to get YouTube playlist name using yt-dlp"""
        try:
            # Quick check for playlist title
            cmd = ["yt-dlp", "--print", "%(playlist_title)s", "--playlist-items", "1", link]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip().split('\n')[0]
            else:
                return None
        except Exception:
            return None

    def _sanitize_filename(self, filename):
        """Sanitize filename to remove invalid characters"""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')

        # Remove multiple spaces and trim
        filename = re.sub(r'\s+', ' ', filename).strip()

        # Limit length
        if len(filename) > 100:
            filename = filename[:97] + "..."

        return filename
        
    def start_download(self):
        if self.is_downloading:
            return
            
        # Validate inputs
        if not self.download_folder.get().strip():
            messagebox.showerror("Error", "Please select a download folder")
            return
            
        if not self.link_var.get().strip():
            messagebox.showerror("Error", "Please enter a music link")
            return
            
        # Validate link
        is_valid, link_type = self.validate_link(self.link_var.get())
        if not is_valid:
            messagebox.showerror("Error", link_type)
            return
            
        # Start download in separate thread
        self.is_downloading = True
        self.download_btn.config(state='disabled')
        self.progress_var.set(0)
        self.status_var.set("Starting download...")
        
        download_thread = threading.Thread(target=self.download_music, args=(link_type,))
        download_thread.daemon = True
        download_thread.start()
        
    def download_music(self, link_type):
        try:
            link = self.link_var.get().strip()
            base_download_path = self.download_folder.get().strip()

            # Validate base download path
            if not os.path.exists(base_download_path):
                os.makedirs(base_download_path, exist_ok=True)
                self.log_message(f"📁 Created base download folder: {base_download_path}")

            # Get organized download path based on content type
            download_path = self._get_organized_download_path(base_download_path, link_type, link)

            self.log_message(f"🚀 Starting download from {link_type}...")
            self.log_message(f"📂 Download path: {download_path}")
            self.status_var.set(f"Downloading from {link_type}...")
            self.progress_var.set(10)

            # Check for potential duplicates
            if self._check_for_duplicates(link, download_path):
                response = messagebox.askyesno("Duplicate Detected",
                    "Similar content may already exist in the download folder. Continue anyway?",
                    icon='warning')
                if not response:
                    self.log_message("🚫 Download cancelled by user (duplicate detected)")
                    self.status_var.set("Download cancelled")
                    return

            if link_type.startswith("spotify"):
                self.download_spotify(link, download_path, link_type)
            elif link_type.startswith("youtube"):
                self.download_youtube(link, download_path, link_type)

        except Exception as e:
            self.log_message(f"❌ Error: {str(e)}")
            self.status_var.set("❌ Download failed")
            messagebox.showerror("Error", f"Download failed: {str(e)}")
        finally:
            self.is_downloading = False
            self.download_btn.config(state='normal')

    def _check_for_duplicates(self, link, download_path):
        """Check if similar content might already exist"""
        try:
            # Extract potential filename patterns from the link
            if "spotify.com" in link:
                # For Spotify, check if any audio files exist in the target directory
                if os.path.exists(download_path):
                    audio_extensions = ['.mp3', '.m4a', '.webm', '.ogg', '.wav', '.flac']
                    existing_files = [f for f in os.listdir(download_path)
                                    if f.lower().endswith(tuple(audio_extensions))]
                    return len(existing_files) > 0
            elif "youtube.com" in link or "youtu.be" in link:
                # For YouTube, try to get video title and check for similar files
                try:
                    cmd = ["yt-dlp", "--print", "%(title)s", "--no-download", link]
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

                    if result.returncode == 0 and result.stdout.strip():
                        video_title = result.stdout.strip()
                        # Check for files with similar names
                        if os.path.exists(download_path):
                            existing_files = os.listdir(download_path)
                            for existing_file in existing_files:
                                # Simple similarity check (could be improved)
                                if any(word.lower() in existing_file.lower()
                                      for word in video_title.split()[:3]):  # Check first 3 words
                                    return True
                except Exception:
                    pass

            return False
        except Exception:
            return False
            
    def download_spotify(self, link, download_path, link_type="spotify_track"):
        """Download from Spotify using spotdl"""
        self.log_message("🎵 Using spotdl for Spotify download...")
        self.progress_var.set(20)
        
        try:
            # First try with basic command to check if spotdl works
            basic_cmd = ["spotdl", "download", link, "--output", download_path]
            
            # Test basic command first
            test_result = subprocess.run(basic_cmd + ["--help"], capture_output=True, text=True, timeout=5)
            
            # Use spotdl with optimized settings for speed
            cmd = [
                "spotdl",
                "download",
                link,
                "--output", download_path,
                "--format", "mp3"
            ]

            # Add FFmpeg path if available
            if self.ffmpeg_path and self.ffmpeg_path != "ffmpeg":
                cmd.extend(["--ffmpeg", self.ffmpeg_path])

            # Add optional flags if they exist
            try:
                # Test if --audio-quality is supported
                test_cmd = ["spotdl", "download", "--help"]
                help_output = subprocess.run(test_cmd, capture_output=True, text=True, timeout=5)
                if "--audio-quality" in help_output.stdout:
                    cmd.extend(["--audio-quality", "192k"])

                # Test if --threads is supported
                if "--threads" in help_output.stdout:
                    cmd.extend(["--threads", "4"])

                # Test if --save-errors is supported
                if "--save-errors" in help_output.stdout:
                    cmd.extend(["--save-errors", "errors.log"])

                # Test if --retries is supported
                if "--retries" in help_output.stdout:
                    cmd.extend(["--retries", "3"])

            except Exception as e:
                self.log_message(f"⚠️ Some advanced options not available, using basic settings: {str(e)}")
            
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                     universal_newlines=True, bufsize=1)
            
            for line in process.stdout:
                self.log_message(line.strip())
                if "Downloading" in line:
                    self.progress_var.set(50)
                elif "Downloaded" in line:
                    self.progress_var.set(90)
                elif "FFmpegError" in line or "Failed to convert" in line:
                    self.log_message(f"ℹ️ FFmpeg conversion warning (file will still be downloaded): {line.strip()}")
                elif "Error" in line or "Failed" in line:
                    self.log_message(f"⚠️ Warning: {line.strip()}")
                    
            process.wait()
            
            # If the first attempt failed, try with basic command
            if process.returncode != 0:
                self.log_message("🔄 First attempt failed, trying with basic settings...")
                basic_cmd = ["spotdl", "download", link, "--output", download_path]
                
                process = subprocess.Popen(basic_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                         universal_newlines=True, bufsize=1)
                
                for line in process.stdout:
                    self.log_message(line.strip())
                    if "Downloading" in line:
                        self.progress_var.set(50)
                    elif "Downloaded" in line:
                        self.progress_var.set(90)
                    elif "FFmpegError" in line or "Failed to convert" in line:
                        self.log_message(f"ℹ️ FFmpeg conversion warning (file will still be downloaded): {line.strip()}")
                    elif "Error" in line or "Failed" in line:
                        self.log_message(f"⚠️ Warning: {line.strip()}")
                        
                process.wait()
            
            if process.returncode == 0:
                self.log_message("✅ Download completed successfully!")
                self.status_var.set("✅ Download complete!")
                self.progress_var.set(100)
                self._show_download_stats(download_path)
                messagebox.showinfo("Success", "Music downloaded successfully!")
            else:
                # Check if any files were actually downloaded (any audio format)
                audio_extensions = ['.mp3', '.m4a', '.webm', '.ogg', '.wav', '.flac']
                files_downloaded = any(f.lower().endswith(tuple(audio_extensions)) for f in os.listdir(download_path) if os.path.isfile(os.path.join(download_path, f)))
                if files_downloaded:
                    self.log_message("⚠️ Some downloads completed with warnings")
                    self.status_var.set("⚠️ Download completed with warnings")
                    self.progress_var.set(100)
                    self._show_download_stats(download_path)
                    messagebox.showwarning("Warning", "Download completed with some warnings. Check the log for details.")
                else:
                    self.log_message("❌ Download failed - no files were downloaded")
                    self.status_var.set("❌ Download failed")
                    raise Exception("Download process failed - no files downloaded")
                
        except FileNotFoundError:
            raise Exception("spotdl not found. Please install it first.")
        except Exception as e:
            raise Exception(f"Spotify download failed: {str(e)}")
            
    def download_youtube(self, link, download_path, link_type="youtube_video"):
        """Download from YouTube using yt-dlp"""
        self.log_message("🎵 Using yt-dlp for YouTube download...")
        self.progress_var.set(20)
        
        try:
            # Check if aria2c is available for faster downloads
            aria2c_available = False
            try:
                subprocess.run(["aria2c", "--version"], capture_output=True, check=True, timeout=2)
                aria2c_available = True
                self.log_message("🚀 aria2c found - using for faster downloads")
            except:
                self.log_message("ℹ️ aria2c not found - using default downloader")
            
            # Check if FFmpeg is available for MP3 conversion
            ffmpeg_available = False
            try:
                subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True, timeout=2)
                ffmpeg_available = True
                self.log_message("✅ FFmpeg found - will convert to MP3")
            except:
                self.log_message("ℹ️ FFmpeg not found - will download in best available format")
            
            # Base command
            cmd = [
                "yt-dlp",
                "--format", "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio",
                "--output", os.path.join(download_path, "%(title)s.%(ext)s"),
                "--no-post-overwrites",  # Don't overwrite existing files
                "--ignore-errors",  # Continue on errors
                "--concurrent-fragments", "16",  # More parallel downloads for speed
                "--max-downloads", "10",  # More concurrent downloads
                "--retries", "3",  # Retry failed downloads
                "--fragment-retries", "3",  # Retry failed fragments
                "--skip-unavailable-fragments",  # Skip unavailable fragments
                "--max-sleep-interval", "1",  # Reduce sleep between requests
                "--sleep-interval", "0.5",  # Reduce sleep interval
            ]

            # Add FFmpeg path if available
            if self.ffmpeg_path and self.ffmpeg_path != "ffmpeg":
                cmd.extend(["--ffmpeg-location", self.ffmpeg_path])
            
            # Only add audio conversion if FFmpeg is available
            if ffmpeg_available:
                cmd.extend([
                    "--extract-audio",  # Extract audio
                    "--audio-format", "mp3",  # Convert to MP3
                    "--audio-quality", "192k",  # Better quality, still fast
                ])
            else:
                self.log_message("💡 Tip: Install FFmpeg for MP3 conversion: winget install ffmpeg")
            
            # Add aria2c options if available
            if aria2c_available:
                try:
                    # Test if yt-dlp supports these options
                    test_cmd = ["yt-dlp", "--help"]
                    help_output = subprocess.run(test_cmd, capture_output=True, text=True, timeout=5)
                    
                    if "--external-downloader" in help_output.stdout:
                        cmd.extend([
                            "--external-downloader", "aria2c",  # Use aria2c if available
                            "--external-downloader-args", "aria2c:-x 16 -s 16 -k 1M",  # aria2c arguments
                        ])
                    elif "--downloader-args" in help_output.stdout:
                        cmd.extend([
                            "--downloader-args", "aria2c:-x 16 -s 16 -k 1M",  # Use aria2c for faster downloads
                        ])
                except Exception as e:
                    self.log_message(f"⚠️ aria2c integration not available: {str(e)}")
            
            cmd.append(link)
            
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                     universal_newlines=True, bufsize=1)
            
            for line in process.stdout:
                self.log_message(line.strip())
                if "download:" in line:
                    # Parse progress
                    try:
                        progress_info = line.split("download:")[1].strip()
                        downloaded, total = progress_info.split("/")
                        progress = (int(downloaded) / int(total)) * 100
                        self.progress_var.set(20 + (progress * 0.7))  # 20-90%
                    except:
                        pass
                elif "ERROR:" in line or "WARNING:" in line:
                    self.log_message(f"⚠️ {line.strip()}")
                        
            process.wait()
            
            # If the first attempt failed, try with basic command
            if process.returncode != 0:
                self.log_message("🔄 First attempt failed, trying with basic settings...")
                basic_cmd = [
                    "yt-dlp",
                    "--format", "bestaudio",
                    "--output", os.path.join(download_path, "%(title)s.%(ext)s"),
                    link
                ]

                # Add FFmpeg path if available
                if self.ffmpeg_path and self.ffmpeg_path != "ffmpeg":
                    basic_cmd.extend(["--ffmpeg-location", self.ffmpeg_path])

                # Only add audio conversion if FFmpeg is available
                if ffmpeg_available:
                    basic_cmd.extend(["--extract-audio", "--audio-format", "mp3"])
                
                process = subprocess.Popen(basic_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                         universal_newlines=True, bufsize=1)
                
                for line in process.stdout:
                    self.log_message(line.strip())
                    if "download:" in line:
                        # Parse progress
                        try:
                            progress_info = line.split("download:")[1].strip()
                            downloaded, total = progress_info.split("/")
                            progress = (int(downloaded) / int(total)) * 100
                            self.progress_var.set(20 + (progress * 0.7))  # 20-90%
                        except:
                            pass
                    elif "ERROR:" in line or "WARNING:" in line:
                        self.log_message(f"⚠️ {line.strip()}")
                        
                process.wait()
            
            if process.returncode == 0:
                self.log_message("✅ Download completed successfully!")
                self.status_var.set("✅ Download complete!")
                self.progress_var.set(100)
                self._show_download_stats(download_path)
                messagebox.showinfo("Success", "Music downloaded successfully!")
            else:
                # Check if any files were actually downloaded (any audio format)
                audio_extensions = ['.mp3', '.m4a', '.webm', '.ogg', '.wav', '.flac']
                files_downloaded = any(f.lower().endswith(tuple(audio_extensions)) for f in os.listdir(download_path) if os.path.isfile(os.path.join(download_path, f)))
                if files_downloaded:
                    self.log_message("⚠️ Some downloads completed with warnings")
                    self.status_var.set("⚠️ Download completed with warnings")
                    self.progress_var.set(100)
                    self._show_download_stats(download_path)
                    messagebox.showwarning("Warning", "Download completed with some warnings. Check the log for details.")
                else:
                    self.log_message("❌ Download failed - no files were downloaded")
                    self.status_var.set("❌ Download failed")
                    raise Exception("Download process failed - no files downloaded")
                
        except FileNotFoundError:
            raise Exception("yt-dlp not found. Please install it first.")
        except Exception as e:
            raise Exception(f"YouTube download failed: {str(e)}")
    
    def _show_download_stats(self, download_path):
        """Show download statistics"""
        try:
            audio_extensions = ['.mp3', '.m4a', '.webm', '.ogg', '.wav', '.flac']
            audio_files = [f for f in os.listdir(download_path) if f.lower().endswith(tuple(audio_extensions)) and os.path.isfile(os.path.join(download_path, f))]
            total_size = sum(os.path.getsize(os.path.join(download_path, f)) for f in audio_files)
            total_size_mb = total_size / (1024 * 1024)
            
            self.log_message(f"📊 Download Statistics:")
            self.log_message(f"   Files downloaded: {len(audio_files)}")
            self.log_message(f"   Total size: {total_size_mb:.1f} MB")
            
            if audio_files:
                self.log_message(f"   Files:")
                for i, file in enumerate(audio_files[:5]):  # Show first 5 files
                    self.log_message(f"     {i+1}. {file}")
                if len(audio_files) > 5:
                    self.log_message(f"     ... and {len(audio_files) - 5} more")
        except Exception as e:
            self.log_message(f"⚠️ Could not show download stats: {str(e)}")
            
    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    try:
        app = Earbound()
        app.run()
    except Exception as e:
        messagebox.showerror("Fatal Error", f"Application failed to start: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
