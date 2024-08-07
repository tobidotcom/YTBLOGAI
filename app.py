import yt_dlp
import traceback
import streamlit as st
import os
import sys
import io
import logging
import openai

# Custom logger to capture yt-dlp output
class LogCapture:
    def __init__(self):
        self.log = io.StringIO()
        self.handler = logging.StreamHandler(self.log)
        self.logger = logging.getLogger('yt-dlp')
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.DEBUG)

    def get_log(self):
        return self.log.getvalue()

def download_audio_as_mp3(url, output_path):
    log_capture = LogCapture()

    ydl_opts = {
        'format': 'bestaudio/best',  # Download the best audio available
        'extractaudio': True,        # Extract audio only
        'audioformat': 'mp3',        # Save as mp3
        'outtmpl': output_path,      # Output file path
        'quiet': True,               # Suppress unnecessary output
        'no_warnings': True,         # Suppress warnings
        'logger': log_capture.logger, # Custom logger
        'noplaylist': True,          # Download only the single video
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if not os.path.isfile(output_path):
            st.error(f"Audio file was not created at: {output_path}")
            return False

        file_size = os.path.getsize(output_path)
        if file_size == 0:
            st.error(f"Downloaded file is empty: {output_path}")
            return False

        st.success(f"Audio downloaded successfully: {output_path} (Size: {file_size} bytes)")
        return True
    except Exception as e:
        st.error(f"Error downloading audio: {str(e)}")
        st.text("Full traceback:")
        st.text(traceback.format_exc())
        st.text("yt-dlp log:")
        st.text(log_capture.get_log())  # Capture the yt-dlp log
    return False

def transcribe_audio(audio_path, openai_api_key):
    openai.api_key = openai_api_key
    try:
        response = openai.Audio.create(
            file=open(audio_path, 'rb'),
            model="whisper-1",  # Example model; choose the one that fits your needs
            prompt="Transcribe the audio",
        )
        return response['text']
    except Exception as e:
        st.error(f"Error transcribing audio: {str(e)}")
        return None

def summarize_text(text, openai_api_key):
    openai.api_key = openai_api_key
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Summarize the following text:\n\n{text}",
            max_tokens=150
        )
        return response.choices[0].text.strip()
    except Exception as e:
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

        mp3_path = 'audio.mp3'

        st.text("Starting audio download process...")
        success = download_audio_as_mp3(video_url, mp3_path)
        
        if not success:
            st.error("Failed to download the audio. Please check the error messages above for more details.")
            st.text("Debug information:")
            st.text(f"Python version: {sys.version}")
            st.text(f"yt-dlp version: {yt_dlp.__version__}")
            return

        st.text("Transcribing audio...")
        transcription = transcribe_audio(mp3_path, openai_api_key)
        
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

