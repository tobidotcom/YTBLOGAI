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
        'format': 'worstvideo[ext=mp4]+worstaudio[ext=m4a]/worst[ext=mp4]/worst',
        'outtmpl': output_path,
        'quiet': False,
        'progress_hooks': [log_progress]
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if info is None:
                logging.error(f"Could not extract video info from URL: {url}")
                return False
            
            logging.info(f"Downloading video: {info.get('title', 'Unknown title')}")
            ydl.download([url])
        
        if not os.path.isfile(output_path):
            logging.error(f"Video file was not created at: {output_path}")
            return False
        
        file_size = os.path.getsize(output_path)
        if file_size == 0:
            logging.error(f"Downloaded file is empty: {output_path}")
            return False
        
        logging.info(f"Video downloaded successfully: {output_path} (Size: {file_size} bytes)")
        return True
    except yt_dlp.utils.DownloadError as e:
        logging.error(f"yt-dlp download error: {str(e)}")
    except yt_dlp.utils.ExtractorError as e:
        logging.error(f"yt-dlp extractor error: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error downloading video: {str(e)}")
    return False

def log_progress(d):
    if d['status'] == 'downloading':
        print(f"Downloading: {d['_percent_str']} of {d['_total_bytes_str']} at {d['_speed_str']}")
    elif d['status'] == 'finished':
        print(f"Finished downloading: {d['filename']}")

def extract_audio(video_path, audio_path):
    if not os.path.isfile(video_path):
        logging.error(f"Video file not found: {video_path}")
        return False
    try:
        with VideoFileClip(video_path) as video_clip:
            audio_clip = video_clip.audio
            audio_clip.write_audiofile(audio_path, codec='mp3')
        logging.info(f"Audio extracted successfully: {audio_path}")
        return True
    except Exception as e:
        logging.error(f"Error extracting audio: {e}")
        return False

def transcribe_audio(audio_path, api_key):
    if not os.path.isfile(audio_path):
        logging.error(f"Audio file not found: {audio_path}")
        return None
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {api_key}"}
    with open(audio_path, "rb") as audio_file:
        files = {"file": audio_file}
        data = {"model": "whisper-1", "response_format": "json"}
        try:
            response = requests.post(url, headers=headers, files=files, data=data)
            response.raise_for_status()
            return response.json().get("text")
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
            {"role": "system", "content": "You are a blog post writer."},
            {"role": "user", "content": f"Create a blog post based on the following transcription:\n\n{transcription}"}
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.RequestException as e:
        logging.error(f"Error generating blog post: {e}")
        return None

def main():
    st.title("YouTube Video to Blog Post")

    video_url = st.text_input("Enter the YouTube video URL:")
    openai_api_key = st.text_input("Enter your OpenAI API key:", type="password")

    if st.button("Process"):
        if not video_url or not openai_api_key:
            st.error("Please provide both the YouTube URL and OpenAI API key.")
            return

        video_path = 'video.mp4'
        audio_path = 'audio.mp3'

        with st.spinner("Downloading video..."):
            if not download_video(video_url, video_path):
                st.error("Failed to download the video. Please check the following:")
                st.error("1. Ensure the YouTube URL is correct and the video is accessible.")
                st.error("2. Check your internet connection.")
                st.error("3. Make sure you have the latest version of yt-dlp installed.")
                st.error("4. The video might be restricted or require authentication.")
                return
            st.success("Video downloaded successfully.")

        with st.spinner("Extracting audio..."):
            if not extract_audio(video_path, audio_path):
                st.error("Failed to extract audio from the video.")
                return
            st.success("Audio extracted successfully.")

        with st.spinner("Transcribing audio..."):
            transcription = transcribe_audio(audio_path, openai_api_key)
            if not transcription:
                st.error("Failed to transcribe the audio.")
                return
            st.success("Transcription completed successfully.")

        with st.spinner("Generating blog post..."):
            blog_post = generate_blog_post(transcription, openai_api_key)
            if not blog_post:
                st.error("Failed to generate the blog post.")
                return
            st.success("Blog post generated successfully.")

        st.subheader("Generated Blog Post:")
        st.text_area("", blog_post, height=400)

        # Clean up temporary files
        os.remove(video_path)
        os.remove(audio_path)

if __name__ == "__main__":
    main()
