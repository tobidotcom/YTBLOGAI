import os
import time
import logging
import requests
from moviepy.editor import VideoFileClip
import yt_dlp
import streamlit as st

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
        # Wait until the file is actually created
        while not os.path.isfile(output_path):
            time.sleep(1)
        logging.info(f"Video downloaded: {output_path}")
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
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
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
        logging.info(f"Transcription response: {response.json()}")
        return response.json().get("text", None)
    except requests.RequestException as e:
        logging.error(f"Error transcribing audio: {e}")
        if response:
            logging.error(f"Response status code: {response.status_code}")
            logging.error(f"Response content: {response.text}")
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

# Streamlit app
def main():
    st.title("YouTube Video to Blog Post")

    video_url = st.text_input("Enter the YouTube video URL:")
    openai_api_key = st.text_input("Enter your OpenAI API key:", type="password")

    if st.button("Process"):
        if not video_url or not openai_api_key:
            st.error("Please provide both the YouTube URL and OpenAI API key.")
            return

        # File paths
        video_path = 'video.mp4'
        audio_path = 'audio.mp3'

        # Download the video
        st.write("Downloading video...")
        download_video(video_url, video_path)
        st.write("Video downloaded.")

        # Extract audio
        st.write("Extracting audio...")
        extract_audio(video_path, audio_path)
        st.write("Audio extracted.")

        # Transcribe audio
        st.write("Transcribing audio...")
        transcription = transcribe_audio(audio_path, openai_api_key)
        if transcription:
            st.write("Transcription successful.")

            # Generate blog post
            st.write("Generating blog post...")
            blog_post = generate_blog_post(transcription, openai_api_key)
            if blog_post:
                st.write("Blog Post:")
                st.text_area("Generated Blog Post", blog_post, height=400)
            else:
                st.error("Failed to generate the blog post.")
        else:
            st.error("Failed to transcribe the audio.")
    
if __name__ == "__main__":
    main()
