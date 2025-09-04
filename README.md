# 🎵 Earbound - Universal Music Downloader

> **Bringing Back the MP3 Era** - A modern, cross-platform music downloader with automatic dependency management and smart folder organization.

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com/ronu-777/earbound)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## ✨ Features

- **🎯 Universal Support**: Download from Spotify, YouTube, and YouTube Music
- **📁 Smart Organization**: Automatic folder organization for playlists, albums, and singles
- **🔧 Zero Setup**: Auto-installs all dependencies (spotdl, yt-dlp, FFmpeg)
- **🎨 Modern UI**: Beautiful, responsive interface with dark/light theme support
- **⚡ High Performance**: Optimized download speeds with parallel processing
- **🔄 Duplicate Prevention**: Smart detection to avoid re-downloading existing content
- **💾 MP3 Conversion**: Automatic audio format conversion with FFmpeg
- **⌨️ Keyboard Shortcuts**: Press Enter to start downloads instantly

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- Internet connection for initial setup

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ronu-777/earbound.git
   cd earbound
   ```

2. **Run the application**
   ```bash
   python Earbound.py
   ```

That's it! The app will automatically:
- Install required Python packages (spotdl, yt-dlp)
- Download FFmpeg binary for your platform
- Set up the download environment

## 🎨 Interface Features

- **Modern Design**: Clean, intuitive interface with theme support
- **Theme System**: Automatic dark/light theme detection
- **Real-time Updates**: Live progress tracking and status updates
- **Responsive Layout**: Adapts to different window sizes

## 🎵 Supported Platforms

### Spotify
- ✅ Individual tracks
- ✅ Albums
- ✅ Playlists
- ✅ High-quality MP3 output

### YouTube & YouTube Music
- ✅ Single videos
- ✅ Playlists
- ✅ Audio extraction
- ✅ MP3 conversion

## 📂 Smart Folder Organization

Earbound automatically organizes your downloads:

```
Earbound/
├── Spotify_Playlist/          # Spotify playlists & albums
├── YouTube_Playlist/          # YouTube playlists
│   └── Playlist Name/        # Individual playlist folders
├── Single Track 1.mp3         # Individual tracks/videos
├── Single Track 2.mp3
└── ...
```

## 🛠️ How It Works

### 1. **Dependency Management**
- Automatically detects missing packages
- Installs spotdl and yt-dlp via pip
- Downloads platform-specific FFmpeg binaries

### 2. **Content Detection**
- Analyzes URLs to determine content type
- Routes downloads to appropriate folders
- Handles playlists vs. singles intelligently

### 3. **Download Process**
- Uses optimized settings for speed
- Parallel downloads for playlists
- Real-time progress updates
- Automatic error recovery

### 4. **Post-Processing**
- MP3 conversion with FFmpeg
- Metadata preservation
- Duplicate detection and prevention

## 🎨 Themes

- **Auto-detect**: Automatically matches your system theme
- **Light Theme**: Clean, modern appearance
- **Dark Theme**: Easy on the eyes for night use

## ⌨️ Keyboard Shortcuts

- **Enter**: Start download (when link field is focused)
- **Ctrl+O**: Browse for download folder
- **Ctrl+L**: Clear log

## 🔧 Advanced Features

### FFmpeg Integration
- Automatic binary download for your platform
- Local storage in `bin/` folder
- Seamless MP3 conversion

### Download Optimization
- Parallel fragment downloads
- Retry mechanisms for failed downloads
- Bandwidth optimization

### Error Handling
- Graceful fallbacks for failed operations
- Detailed error logging
- User-friendly error messages

## 📋 Requirements

| Component | Version | Auto-Install |
|-----------|---------|--------------|
| Python    | 3.7+    | ✅ System    |
| spotdl    | Latest  | ✅ Auto      |
| yt-dlp    | Latest  | ✅ Auto      |
| FFmpeg    | Latest  | ✅ Auto      |

## 🚨 Troubleshooting

### Common Issues

**"spotdl not found"**
- The app will auto-install it on first run
- If it fails, run: `pip install spotdl`

**"FFmpeg conversion failed"**
- FFmpeg is automatically downloaded
- Check the log for specific error details

**"Download folder not found"**
- Use the Browse button to select a valid folder
- Ensure you have write permissions

### Manual Installation (if auto-install fails)

```bash
# Install Python packages
pip install spotdl yt-dlp

# Install FFmpeg
# Windows: winget install ffmpeg
# macOS: brew install ffmpeg  
# Linux: sudo apt install ffmpeg
```



## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [spotdl](https://github.com/spotDL/spotify-downloader) - Spotify downloading engine
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube downloading engine
- [FFmpeg](https://ffmpeg.org/) - Audio/video processing
- [tkinter](https://docs.python.org/3/library/tkinter.html) - GUI framework



---

<div align="center">
  <p>Made with ❤️ for music lovers everywhere</p>
  <p><strong>Earbound</strong> - Bringing Back the MP3 Era</p>
  <p>Created by <strong>Ronak Singh Meena</strong></p>
</div>
