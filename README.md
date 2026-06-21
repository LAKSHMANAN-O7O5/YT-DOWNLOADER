# 🔥 Pro Video & Audio Downloader

A powerful desktop application to download videos, audio, and playlists from YouTube and other platforms.

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?logo=windows)

## ✨ Features

- 🎥 **Video Download** — Download videos in MP4 (Best, 1080p, 720p, 480p, 360p)
- 🎵 **Audio Download** — Extract audio as MP3 (192kbps)
- 📃 **Playlist Support** — Download entire playlists at once
- 📋 **Queue System** — Add multiple URLs and batch download
- 🖼️ **Thumbnail Preview** — Fetch video info and thumbnail before downloading
- 📊 **Live Progress** — Real-time progress bar with speed and ETA

## 📋 Prerequisites

- **Python 3.8+**
- **FFmpeg** — Download from [ffmpeg.org](https://ffmpeg.org/download.html) and place `ffmpeg.exe` in the project root (or add to PATH)

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/YT-DOWNLOADER.git
   cd YT-DOWNLOADER
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download FFmpeg**
   - Download `ffmpeg.exe` from [ffmpeg.org](https://ffmpeg.org/download.html)
   - Place it in the project root directory

4. **Run the app**
   ```bash
   python YT-downloader_final.py
   ```

## 📦 Build Standalone EXE

To create a standalone `.exe` (no Python required for end users):

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=app.ico --add-data "ffmpeg.exe;." YT-downloader_final.py
```

The executable will be in the `dist/` folder.

## 🛠️ Dependencies

| Package | Purpose |
|---------|---------|
| `customtkinter` | Modern dark-themed GUI |
| `yt-dlp` | Video/audio downloading engine |
| `Pillow` | Thumbnail image processing |
| `requests` | Fetching thumbnails |

## 📄 License

This project is licensed under the MIT License.

## ⚠️ Disclaimer

This tool is for personal use only. Please respect copyright laws and the terms of service of the platforms you download from.
