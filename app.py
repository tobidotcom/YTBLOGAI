import yt_dlp as ytdlp
import requests
import streamlit as st
import os
import sys
import traceback

# Function to download video and extract audio
def download_and_extract_audio(video_url, output_path):
    # Define the options for yt-dlp
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'temp.%(ext)s',  # Temporary filename
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
        'quiet': True,
        'progress_hooks': [lambda d: None]  # Disable progress output
    }

    try:
        # Download video and extract audio
        with ytdlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        
        # Move the file to the desired output path
        temp_file = 'temp.mp3'
        if os.path.exists(temp_file):
            os.rename(temp_file, output_path)
            st.success(f"Audio extracted successfully: {output_path}")
            return True
        else:
            st.error("Failed to extract audio. Temporary file not found.")
            return False
    except Exception as e:
        st.error(f"Error during download or extraction: {str(e)}")
        st.text("Full traceback:")
        st.text(traceback.format_exc())
        return False

# Function to transcribe audio using OpenAI API
def transcribe_audio(audio_path, openai_api_key):
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {
        "Authorization": f"Bearer {openai_api_key}"
    }
    files = {
        'file': ('audio.mp3', open(audio_path, 'rb')),
        'model': (None, 'whisper-1')
    }

    try:
        response = requests.post(url, headers=headers, files=files)
        response.raise_for_status()
        result = response.json()
        return result.get('text')
    except requests.RequestException as e:
        st.error(f"Error transcribing audio: {str(e)}")
        return None

# Function to summarize text using OpenAI API
def summarize_text(text, openai_api_key):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Summarize the following text:\n\n{text}"}
        ],
        "max_tokens": 150
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
    except requests.RequestException as e:
        st.error(f"Error summarizing text: {str(e)}")
        return None

def main():
    st.title("YouTube Video to Blog Post")

    video_url = st.text_input("Enter the YouTube video URL:")
    openai_api_key = st.text_input("Enter your OpenAI API key:", type="password")

    if st.button("Process"):
        if not video_url or not openai_api_key:
            st.error("Please provide both the YouTube URL and OpenAI API key.")
            return

        audio_path = 'audio.mp3'

        st.text("Starting video download and audio extraction process...")
        success = download_and_extract_audio(video_url, audio_path)
        
        if not success:
            st.error("Failed to download and extract the audio. Please check the error messages above for more details.")
            st.text("Debug information:")
            st.text(f"Python version: {sys.version}")
            return

        st.text("Transcribing audio...")
        transcription = transcribe_audio(audio_path, openai_api_key)
        
        if transcription:
            st.text("Transcription complete. Here is the text:")
            st.text(transcription)

            st.text("Summarizing text...")
            summary = summarize_text(transcription, openai_api_key)
            
            if summary:
                st.text("Summary:")
                st.text(summary)
            else:
                st.error("Failed to summarize the text.")
        else:
            st.error("Failed to transcribe the audio.")

if __name__ == "__main__":
    main()


