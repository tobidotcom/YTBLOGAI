from pytube import YouTube
from pydub import AudioSegment
import requests
import streamlit as st
import os
import sys
import traceback

def download_audio_as_mp3(url, output_path):
    try:
        yt = YouTube(url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        audio_file = audio_stream.download(filename='temp_audio')
        
        # Convert to MP3
        audio = AudioSegment.from_file(audio_file)
        audio.export(output_path, format='mp3')
        
        # Clean up temporary file
        os.remove(audio_file)
        
        if not os.path.isfile(output_path):
            st.error(f"Audio file was not created at: {output_path}")
            return False

        file_size = os.path.getsize(output_path)
        if file_size == 0:
            st.error(f"Downloaded file is empty: {output_path}")
            return False

        st.success(f"Audio downloaded and converted successfully: {output_path} (Size: {file_size} bytes)")
        return True
    except Exception as e:
        st.error(f"Error downloading or converting audio: {str(e)}")
        st.text("Full traceback:")
        st.text(traceback.format_exc())
    return False

def transcribe_audio(audio_path, openai_api_key):
    try:
        headers = {
            'Authorization': f'Bearer {openai_api_key}',
        }
        files = {
            'file': open(audio_path, 'rb'),
        }
        response = requests.post('https://api.openai.com/v1/audio/transcriptions', headers=headers, files=files)
        response.raise_for_status()
        return response.json().get('text', '')
    except Exception as e:
        st.error(f"Error transcribing audio: {str(e)}")
        return None

def summarize_text(text, openai_api_key):
    try:
        headers = {
            'Authorization': f'Bearer {openai_api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            'model': 'text-davinci-003',
            'prompt': f"Summarize the following text:\n\n{text}",
            'max_tokens': 150
        }
        response = requests.post('https://api.openai.com/v1/completions', headers=headers, json=data)
        response.raise_for_status()
        return response.json().get('choices', [{}])[0].get('text', '').strip()
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
            st.error("Failed to download and convert the audio. Please check the error messages above for more details.")
            st.text("Debug information:")
            st.text(f"Python version: {sys.version}")
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


