import customtkinter as ctk
from tkinter import filedialog, messagebox
import yt_dlp
import threading
import requests
from PIL import Image
import io
import os
import sys

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# -----------------------------
# Fix for PyInstaller path
# -----------------------------
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller temp folder
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class DownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🔥 Pro Video & Audio Downloader")
        self.geometry("1000x800")
        self.resizable(True, True)
        self.state("zoomed")  # Full screen open

        self.download_path = ""
        self.queue_list = []

        # Scrollable Frame
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Title
        self.label_title = ctk.CTkLabel(
            self.scroll_frame,
            text="🔥 Pro Video & Audio Downloader",
            font=("Arial", 26, "bold")
        )
        self.label_title.pack(pady=15)

        # URL Entry
        self.url_entry = ctk.CTkEntry(
            self.scroll_frame,
            width=700,
            height=40,
            placeholder_text="Paste video / playlist URL here..."
        )
        self.url_entry.pack(pady=10)

        # Fetch Info Button
        self.fetch_btn = ctk.CTkButton(
            self.scroll_frame,
            text="🔍 Fetch Info (Title + Thumbnail)",
            command=self.start_fetch_info,
            width=300
        )
        self.fetch_btn.pack(pady=10)

        # Video Title Display
        self.video_title_label = ctk.CTkLabel(
            self.scroll_frame,
            text="Title: Not Loaded",
            font=("Arial", 14),
            text_color="lightgray"
        )
        self.video_title_label.pack(pady=5)

        # Thumbnail Display
        self.thumbnail_label = ctk.CTkLabel(self.scroll_frame, text="")
        self.thumbnail_label.pack(pady=10)

        # Quality Dropdown
        self.quality_label = ctk.CTkLabel(
            self.scroll_frame,
            text="Select Quality:",
            font=("Arial", 15, "bold")
        )
        self.quality_label.pack(pady=5)

        self.quality_option = ctk.CTkOptionMenu(
            self.scroll_frame,
            values=["Best", "1080p", "720p", "480p", "360p"]
        )
        self.quality_option.set("Best")
        self.quality_option.pack(pady=10)

        # Choose Folder Button
        self.folder_btn = ctk.CTkButton(
            self.scroll_frame,
            text="📂 Choose Download Folder",
            command=self.choose_folder,
            width=300
        )
        self.folder_btn.pack(pady=10)

        self.folder_label = ctk.CTkLabel(
            self.scroll_frame,
            text="No folder selected",
            text_color="gray"
        )
        self.folder_label.pack(pady=5)

        # Progress Bar
        self.progress = ctk.CTkProgressBar(self.scroll_frame, width=700)
        self.progress.set(0)
        self.progress.pack(pady=20)

        self.status_label = ctk.CTkLabel(
            self.scroll_frame,
            text="Status: Waiting...",
            font=("Arial", 13)
        )
        self.status_label.pack(pady=5)

        # Buttons Frame
        self.btn_frame = ctk.CTkFrame(self.scroll_frame)
        self.btn_frame.pack(pady=15)

        self.video_btn = ctk.CTkButton(
            self.btn_frame,
            text="🎥 Download Video (MP4)",
            command=self.start_video_download,
            width=250
        )
        self.video_btn.grid(row=0, column=0, padx=10, pady=10)

        self.audio_btn = ctk.CTkButton(
            self.btn_frame,
            text="🎵 Download Audio (MP3)",
            command=self.start_audio_download,
            width=250
        )
        self.audio_btn.grid(row=0, column=1, padx=10, pady=10)

        # Playlist button centered
        self.playlist_btn = ctk.CTkButton(
            self.btn_frame,
            text="📃 Download Playlist",
            command=self.start_playlist_download,
            width=520
        )
        self.playlist_btn.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        # Queue System Frame
        self.queue_frame = ctk.CTkFrame(self.scroll_frame)
        self.queue_frame.pack(pady=15)

        self.add_queue_btn = ctk.CTkButton(
            self.queue_frame,
            text="➕ Add to Queue",
            command=self.add_to_queue,
            width=250
        )
        self.add_queue_btn.grid(row=0, column=0, padx=10, pady=10)

        self.start_queue_btn = ctk.CTkButton(
            self.queue_frame,
            text="🚀 Start Queue Download",
            command=self.start_queue_download,
            width=250
        )
        self.start_queue_btn.grid(row=0, column=1, padx=10, pady=10)

        self.clear_queue_btn = ctk.CTkButton(
            self.queue_frame,
            text="🗑 Clear Queue",
            command=self.clear_queue,
            width=520
        )
        self.clear_queue_btn.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        self.queue_label = ctk.CTkLabel(
            self.scroll_frame,
            text="Queue: 0 items",
            font=("Arial", 13),
            text_color="lightblue"
        )
        self.queue_label.pack(pady=5)

    # -----------------------------
    # Choose Folder
    # -----------------------------
    def choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.download_path = folder
            self.folder_label.configure(text=folder, text_color="lightgreen")

    # -----------------------------
    # Format Selection
    # -----------------------------
    def get_format(self):
        quality = self.quality_option.get()

        if quality == "Best":
            return "bestvideo+bestaudio/best"
        elif quality == "1080p":
            return "bestvideo[height<=1080]+bestaudio/best"
        elif quality == "720p":
            return "bestvideo[height<=720]+bestaudio/best"
        elif quality == "480p":
            return "bestvideo[height<=480]+bestaudio/best"
        elif quality == "360p":
            return "bestvideo[height<=360]+bestaudio/best"

        return "bestvideo+bestaudio/best"

    # -----------------------------
    # Progress Hook
    # -----------------------------
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            downloaded = d.get("downloaded_bytes", 0)
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 1)

            percent = downloaded / total
            self.progress.set(percent)

            speed = d.get("speed", 0)
            eta = d.get("eta", 0)

            speed_mb = speed / 1024 / 1024 if speed else 0

            self.status_label.configure(
                text=f"Downloading... {percent*100:.1f}% | Speed: {speed_mb:.2f} MB/s | ETA: {eta}s"
            )

        elif d['status'] == 'finished':
            self.progress.set(1)
            self.status_label.configure(text="Download finished! Processing...")

    # -----------------------------
    # Fetch Info
    # -----------------------------
    def start_fetch_info(self):
        threading.Thread(target=self.fetch_info).start()

    def fetch_info(self):
        url = self.url_entry.get().strip()

        if not url:
            messagebox.showerror("Error", "Please enter a URL!")
            return

        self.status_label.configure(text="Fetching info...")

        try:
            ydl_opts = {'quiet': True, 'skip_download': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

            title = info.get("title", "Unknown Title")
            thumbnail_url = info.get("thumbnail")

            self.video_title_label.configure(text=f"Title: {title}")

            if thumbnail_url:
                response = requests.get(thumbnail_url)
                img_data = response.content

                img = Image.open(io.BytesIO(img_data))
                img = img.resize((450, 250))

                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(450, 250))
                self.thumbnail_label.configure(image=ctk_img, text="")
                self.thumbnail_label.image = ctk_img

            self.status_label.configure(text="Info Loaded Successfully ✅")

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status_label.configure(text="Failed to fetch info ❌")

    # -----------------------------
    # Download Video
    # -----------------------------
    def start_video_download(self):
        threading.Thread(target=self.download_video).start()

    def download_video(self):
        url = self.url_entry.get().strip()

        if not url:
            messagebox.showerror("Error", "Please enter a URL!")
            return

        if not self.download_path:
            messagebox.showerror("Error", "Please choose a download folder!")
            return

        self.progress.set(0)
        self.status_label.configure(text="Starting video download...")

        ydl_opts = {
            'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
            'format': self.get_format(),
            'merge_output_format': 'mp4',
            'progress_hooks': [self.progress_hook],

            # Use bundled ffmpeg.exe
            'ffmpeg_location': resource_path("ffmpeg.exe")
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            messagebox.showinfo("Success", "Video Downloaded Successfully!")
            self.status_label.configure(text="Status: Done ✅")

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status_label.configure(text="Status: Failed ❌")

    # -----------------------------
    # Download Audio
    # -----------------------------
    def start_audio_download(self):
        threading.Thread(target=self.download_audio).start()

    def download_audio(self):
        url = self.url_entry.get().strip()

        if not url:
            messagebox.showerror("Error", "Please enter a URL!")
            return

        if not self.download_path:
            messagebox.showerror("Error", "Please choose a download folder!")
            return

        self.progress.set(0)
        self.status_label.configure(text="Starting audio download...")

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
            'progress_hooks': [self.progress_hook],

            # Use bundled ffmpeg.exe
            'ffmpeg_location': resource_path("ffmpeg.exe"),

            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            messagebox.showinfo("Success", "Audio Downloaded Successfully!")
            self.status_label.configure(text="Status: Done ✅")

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status_label.configure(text="Status: Failed ❌")

    # -----------------------------
    # Playlist Download
    # -----------------------------
    def start_playlist_download(self):
        threading.Thread(target=self.download_playlist).start()

    def download_playlist(self):
        url = self.url_entry.get().strip()

        if not url:
            messagebox.showerror("Error", "Please enter playlist URL!")
            return

        if not self.download_path:
            messagebox.showerror("Error", "Please choose download folder!")
            return

        self.progress.set(0)
        self.status_label.configure(text="Downloading playlist...")

        ydl_opts = {
            'outtmpl': os.path.join(self.download_path, '%(playlist_title)s', '%(title)s.%(ext)s'),
            'format': self.get_format(),
            'merge_output_format': 'mp4',
            'progress_hooks': [self.progress_hook],

            # Use bundled ffmpeg.exe
            'ffmpeg_location': resource_path("ffmpeg.exe")
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            messagebox.showinfo("Success", "Playlist Download Completed!")
            self.status_label.configure(text="Playlist Download Done ✅")

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status_label.configure(text="Playlist Download Failed ❌")

    # -----------------------------
    # Queue System
    # -----------------------------
    def add_to_queue(self):
        url = self.url_entry.get().strip()

        if not url:
            messagebox.showerror("Error", "Enter a URL first!")
            return

        self.queue_list.append(url)
        self.queue_label.configure(text=f"Queue: {len(self.queue_list)} items")
        messagebox.showinfo("Added", "URL added to queue!")

    def clear_queue(self):
        self.queue_list.clear()
        self.queue_label.configure(text="Queue: 0 items")
        messagebox.showinfo("Queue Cleared", "Queue cleared successfully!")

    def start_queue_download(self):
        threading.Thread(target=self.download_queue).start()

    def download_queue(self):
        if not self.queue_list:
            messagebox.showerror("Error", "Queue is empty!")
            return

        if not self.download_path:
            messagebox.showerror("Error", "Choose download folder first!")
            return

        for index, url in enumerate(self.queue_list, start=1):
            self.status_label.configure(text=f"Downloading Queue {index}/{len(self.queue_list)}...")

            ydl_opts = {
                'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
                'format': self.get_format(),
                'merge_output_format': 'mp4',
                'progress_hooks': [self.progress_hook],

                # Use bundled ffmpeg.exe
                'ffmpeg_location': resource_path("ffmpeg.exe")
            }

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
            except Exception as e:
                messagebox.showerror("Queue Error", f"Failed: {url}\n\n{str(e)}")

        self.queue_list.clear()
        self.queue_label.configure(text="Queue: 0 items")
        messagebox.showinfo("Done", "Queue Download Completed!")
        self.status_label.configure(text="Queue Done ✅")


if __name__ == "__main__":
    app = DownloaderApp()
    app.mainloop()
