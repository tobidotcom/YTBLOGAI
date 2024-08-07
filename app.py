import yt_dlp
import traceback
import streamlit as st
import os
import sys

def download_video(url, output_path):
    ydl_opts = {
        'format': 'mp4',  # Simply request an MP4 format
        'outtmpl': output_path,
        'quiet': False,
        'progress_hooks': [log_progress],
        'verbose': True  # Enable verbose output
    }
    try:
        st.text("Initializing YouTube downloader...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            st.text("Extracting video info...")
            info = ydl.extract_info(url, download=False)
            if info is None:
                st.error(f"Could not extract video info from URL: {url}")
                return False
            
            st.text(f"Downloading video: {info.get('title', 'Unknown title')}")
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
    except yt_dlp.utils.DownloadError as e:
        st.error(f"yt-dlp download error: {str(e)}")
        st.text("Full traceback:")
        st.text(traceback.format_exc())
    except yt_dlp.utils.ExtractorError as e:
        st.error(f"yt-dlp extractor error: {str(e)}")
        st.text("Full traceback:")
        st.text(traceback.format_exc())
    except Exception as e:
        st.error(f"Unexpected error downloading video: {str(e)}")
        st.text("Full traceback:")
        st.text(traceback.format_exc())
    return False

def log_progress(d):
    if d['status'] == 'downloading':
        st.text(f"Downloading: {d['_percent_str']} of {d['_total_bytes_str']} at {d['_speed_str']}")
    elif d['status'] == 'finished':
        st.text(f"Finished downloading: {d['filename']}")

# The main function remains largely the same, but let's add a bit more debug info:

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
            st.text(f"yt-dlp version: {yt_dlp.version.__version__}")
            return

        # ... (rest of the code remains the same)

if __name__ == "__main__":
    main()
