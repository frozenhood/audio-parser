import yt_dlp
import os
import sys
import requests
import random
import time
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC

# Get cookies path from command line (optional)
cookies_path = None
if len(sys.argv) > 1:
    cookies_path = sys.argv[1]

# =======================
# Load config from environment variables
# =======================
CHANNEL_NAME = os.environ.get("CHANNEL_NAME")
CHANNEL_URL  = os.environ.get("CHANNEL_URL")
OUTPUT_DIR   = os.environ.get("OUTPUT_DIR", "downloads")
TRACK_FILE   = os.environ.get("TRACK_FILE", "downloaded.txt")
COVER_URL    = os.environ.get("COVER_URL")  # URL of cover image
MAX_VIDEOS   = int(os.environ.get("MAX_VIDEOS", 5))  # limit per run
# =======================

if not CHANNEL_NAME or not CHANNEL_URL:
    raise ValueError("CHANNEL_NAME and CHANNEL_URL must be set in environment variables.")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load already downloaded video IDs
if os.path.exists(TRACK_FILE):
    with open(TRACK_FILE, "r") as f:
        downloaded = set(f.read().splitlines())
else:
    downloaded = set()

# yt-dlp options
ydl_opts = {
    'format': 'bestaudio/best',
    'cookies-from-browser': 'cookies.txt',
    'quiet': True,
    'outtmpl': os.path.join(OUTPUT_DIR, '%(title)s.%(ext)s'),
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info_dict = ydl.extract_info(CHANNEL_URL, download=False)
    entries = info_dict.get("entries", [])[:MAX_VIDEOS]  # limit number of videos

    for video in entries:
        video_id = video.get("id")
        if video_id in downloaded:
            continue
        url = f"https://www.youtube.com/watch?v={video_id}"
        print(f"Downloading: {video.get('title')}")
        try:
            ydl.download([url])
            downloaded.add(video_id)
        except yt_dlp.utils.DownloadError as e:
            print(f"Failed to download {video.get('title')}: {e}")
        # Random sleep between 2–6 seconds to avoid 429
        time.sleep(random.randint(2, 6))

# Update downloaded.txt
with open(TRACK_FILE, "w") as f:
    for vid in downloaded:
        f.write(vid + "\n")

# Fetch cover image if URL provided
cover_data = None
if COVER_URL:
    response = requests.get(COVER_URL)
    if response.status_code == 200:
        cover_data = response.content
    else:
        print("Failed to fetch cover image from URL")

# Add ID3 tags and cover
for file in os.listdir(OUTPUT_DIR):
    if file.endswith(".mp3"):
        path = os.path.join(OUTPUT_DIR, file)
        audio = EasyID3(path)
        audio["artist"] = CHANNEL_NAME
        audio["title"] = os.path.splitext(file)[0]
        audio.save()

        if cover_data:
            audio_id3 = ID3(path)
            audio_id3['APIC'] = APIC(
                encoding=3,
                mime='image/jpeg',
                type=3,
                desc='Cover',
                data=cover_data
            )
            audio_id3.save()