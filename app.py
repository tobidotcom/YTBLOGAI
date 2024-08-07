import requests
import streamlit as st
import os
import sys
import traceback

# Function to download audio from YouTube using yt-to-mp3 API
def download_audio_as_mp3(url, output_path):
    api_url = "https://youtube-to-mp315.p.rapidapi.com/download"
    querystring = {"url": url, "format": "mp3"}
    headers = {
        "x-rapidapi-key": "e4f02f4cbemshf4900cfd2d28d8ep15b2b0jsnac923a3be9f7",
        "x-rapidapi-host": "youtube-to-mp315.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(api_url, headers=headers, params=querystring)
        response.raise_for_status()
        data = response.json()

        if data.get('status') == 'success':
            download_url = data.get('url')
            if download_url:
                audio_response = requests.get(download_url, stream=True)
                audio_response.raise_for_status()

                with open(output_path, 'wb') as f:
                    for chunk in audio_response.iter_content(chunk_size=8192):
                        f.write(chunk)

                if not os.path.isfile(output_path):
                    st.error(f"Audio file was not created at: {output_path}")
                    return False

                file_size = os.path.getsize(output_path)
                if file_size == 0:
                    st.error(f"Downloaded file is empty: {output_path}")
                    return False

                st.success(f"Audio downloaded successfully: {output_path} (Size: {file_size} bytes)")
                return True
            else:
                st.error("No download URL received from API.")
                return False
        else:
            st.error(f"Error from yt-to-mp3 API: {data.get('message', 'Unknown error')}")
            return False

    except requests.RequestException as e:
        st.error(f"Request error: {str(e)}")
        st.text("Full traceback:")
        st.text(traceback.format_exc())
        return False

# Function to transcribe audio using OpenAI API with raw requests
def transcribe_audio(audio_path, openai_api_key):
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "multipart/form-data"
    }
    files = {
        'file': ('audio.mp3', open(audio_path, 'rb')),
        'model': 'whisper-1'
    }

    try:
        response = requests.post(url, headers=headers, files=files)
        response.raise_for_status()
        result = response.json()
        return result['text']
    except requests.RequestException as e:
        st.error(f"Error transcribing audio: {str(e)}")
        return None

# Function to summarize text using OpenAI API with raw requests
def summarize_text(text, openai_api_key):
    url = "https://api.openai.com/v1/completions"
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "text-davinci-003",
        "prompt": f"Summarize the following text:\n\n{text}",
        "max_tokens": 150
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['text'].strip()
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

        st.text("Starting audio download process...")
        success = download_audio_as_mp3(video_url, audio_path)
        
        if not success:
            st.error("Failed to download the audio. Please check the error messages above for more details.")
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


