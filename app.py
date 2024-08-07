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

def download_video(url, output_path):
    log_capture = LogCapture()

    ydl_opts = {
        'format': 'mp4',
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
        'logger': log_capture.logger,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if info is None:
                st.error(f"Could not extract video info from URL: {url}")
                return False

            ydl.download([url])

        if not os.path.isfile(output_path):
            st.error(f"Video file was not created at: {output_path}")
            return False

        file_size = os.path.getsize(output_path)
        if file_size == 0:
            st.error(f"Downloaded file is empty: {output_path}")
            return False

        st.success(f"Video downloaded successfully: {output_path} (Size: {file_size} bytes)")
        return True
    except Exception as e:
        st.error(f"Error downloading video: {str(e)}")
        st.text("Full traceback:")
        st.text(traceback.format_exc())
        st.text("yt-dlp log:")
        st.text(log_capture.get_log())  # Capture the yt-dlp log
    return False

def transcribe_video(audio_path, openai_api_key):
    # Dummy implementation: Replace with actual transcription logic
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

        video_path = 'video.mp4'
        audio_path = 'audio.mp3'

        st.text("Starting video download process...")
        success = download_video(video_url, video_path)
        
        if not success:
            st.error("Failed to download the video. Please check the error messages above for more details.")
            st.text("Debug information:")
            st.text(f"Python version: {sys.version}")
            st.text(f"yt-dlp version: {yt_dlp.__version__}")
            return

        st.text("Extracting audio...")
        # Placeholder for audio extraction logic (e.g., using ffmpeg)
        # For demonstration purposes, let's assume the audio extraction was successful
        audio_extracted = True

        if audio_extracted:
            st.text("Transcribing audio...")
            transcription = transcribe_video(audio_path, openai_api_key)
            
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
        else:
            st.error("Failed to extract audio from the video.")

if __name__ == "__main__":
    main()

