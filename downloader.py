import yt_dlp

def download_youtube_video(url, filename="video.mp4"):
    ydl_opts = {
        'outtmpl': filename,
        'format': 'mp4[ext=mp4][acodec!=none][vcodec!=none]/best',
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return filename