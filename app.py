import pytube
import traceback
import streamlit as st
import os
import sys
import io
import logging

# Custom logger to capture pytube output
class LogCapture:
    def __init__(self):
        self.log = io.StringIO()
        self.handler = logging.StreamHandler(self.log)
        self.logger = logging.getLogger('pytube')
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.DEBUG)

    def get_log(self):
        return self.log.getvalue()

def download_video(url, output_path):
    log_capture = LogCapture()
    
    try:
        yt = pytube.YouTube(url)
        stream = yt.streams.filter(file_extension='mp4').first()
        
        if not stream:
            st.error("No suitable video stream found.")
            return False
        
        stream.download(output_path=output_path)
        
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
        st.text("pytube log:")
        st.text(log_capture.get_log())  # Capture the pytube log
    return False

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
            st.text(f"pytube version: {pytube.__version__}")
            return

        # ... (rest of the code remains the same)

if __name__ == "__main__":
    main()
