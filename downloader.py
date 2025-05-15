import yt_dlp
import os
import base64

os.environ.get("YT_COOKIES_BASE64")

def write_cookies_file():
    cookies_base64 = os.environ.get("YT_COOKIES_BASE64")
    if not cookies_base64:
        raise ValueError("YT_COOKIES_BASE64 environment variable not set")

    cookies = base64.b64decode(cookies_base64)
    with open("cookies.txt", "wb") as f:
        f.write(cookies)
    print("[INFO] cookies.txt written")

def download_youtube_video(url, filename="video.mp4"):
    write_cookies_file()

    ydl_opts = {
        'outtmpl': filename,
        'format': 'mp4[ext=mp4][acodec!=none][vcodec!=none]/best',
        'cookies': 'cookies.txt',
        'quiet': True,
    }
    print("COOKIES FILE EXISTS?", os.path.exists("cookies.txt"))

    with open("cookies.txt", "rb") as f:
        print(f.read(500).decode('utf-8', errors='replace'))

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return filename