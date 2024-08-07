import os
import logging
import requests
from moviepy.editor import VideoFileClip
import yt_dlp

# Configure logging
logging.basicConfig(level=logging.INFO)

def download_video(url, output_path):
    ydl_opts = {
        'format': 'worstvideo[ext=mp4]',  # Download the lowest quality MP4 video
        'outtmpl': output_path,
        'quiet': True,  # Suppress output
        'progress_hooks': [log_progress]
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        logging.error(f"Error downloading video: {e}")

def log_progress(d):
    if d['status'] == 'finished':
        logging.info(f"Finished downloading: {d['filename']}")

def extract_audio(video_path, audio_path):
    if not os.path.isfile(video_path):
        logging.error(f"Video file not found: {video_path}")
        return

    try:
        video_clip = VideoFileClip(video_path)
        audio_clip = video_clip.audio
        audio_clip.write_audiofile(audio_path, codec='mp3')
        audio_clip.close()
        video_clip.close()

        if not os.path.isfile(audio_path):
            logging.error(f"Audio file was not created: {audio_path}")
        else:
            logging.info(f"Audio extracted successfully: {audio_path}")

    except Exception as e:
        logging.error(f"Error extracting audio: {e}")

def transcribe_audio(audio_path, api_key):
    if not os.path.isfile(audio_path):
        logging.error(f"Audio file not found: {audio_path}")
        return None

    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    files = {
        "file": open(audio_path, "rb")
    }
    data = {
        "model": "whisper-1",
        "response_format": "json"
    }
    try:
        response = requests.post(url, headers=headers, files=files, data=data)
        response.raise_for_status()
        return response.json()["text"]
    except requests.RequestException as e:
        logging.error(f"Error transcribing audio: {e}")
        return None

def generate_blog_post(transcription, api_key):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4",
        "messages": [
            {
                "role": "system",
                "content": "You are a blog post writer."
            },
            {
                "role": "user",
                "content": f"Create a blog post based on the following transcription:\n\n{transcription}"
            }
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.RequestException as e:
        logging.error(f"Error generating blog post: {e}")
        return None

# Example usage
if __name__ == "__main__":
    video_url = 'https://www.youtube.com/watch?v=YOUR_VIDEO_ID'  # Replace with your YouTube video URL
    video_path = 'video.mp4'
    audio_path = 'audio.mp3'
    openai_api_key = 'your_openai_api_key'  # Replace with your OpenAI API key

    # Step 1: Download the YouTube video
    logging.info("Downloading video...")
    download_video(video_url, video_path)

    # Step 2: Extract audio from the video
    logging.info("Extracting audio...")
    extract_audio(video_path, audio_path)

    # Step 3: Transcribe the audio
    logging.info("Transcribing audio...")
    transcription = transcribe_audio(audio_path, openai_api_key)
    if transcription:
        logging.info("Transcription:", transcription)

        # Step 4: Generate blog post
        logging.info("Generating blog post...")
        blog_post = generate_blog_post(transcription, openai_api_key)
        if blog_post:
            logging.info("Blog Post:", blog_post)

