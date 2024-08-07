import streamlit as st
import requests
import os
from pytube import YouTube
from urllib.error import HTTPError

# Streamlit app title
st.title("YouTube Video to SEO Blog Post")

# Input for OpenAI API key
api_key = st.text_input("Enter your OpenAI API key:", type="password")

# Input for YouTube video URL
video_url = st.text_input("Enter YouTube video URL:")

# Function to download audio from YouTube video
def download_audio(video_url):
    try:
        yt = YouTube(video_url)
        video = yt.streams.filter(only_audio=True).first()
        out_file = video.download(output_path=".")
        base, ext = os.path.splitext(out_file)
        new_file = base + '.mp3'
        os.rename(out_file, new_file)
        return new_file
    except HTTPError as e:
        st.error(f"HTTP Error: {e}")
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Function to transcribe audio using OpenAI API
def transcribe_audio(file_path, api_key):
    with open(file_path, 'rb') as audio_file:
        response = requests.post(
            "https://api.openai.com/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {api_key}"},
            files={"file": audio_file},
            data={"model": "whisper-1", "response_format": "json"}
        )
    response_json = response.json()
    return response_json.get('text', '')

# Function to generate a blog post using OpenAI API
def generate_blog_post(transcription, api_key):
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": "You are an SEO expert and professional blog writer."},
                {"role": "user", "content": f"Create a highly SEO-optimized blog post based on the following transcription:\n\n{transcription}"}
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }
    )
    response_json = response.json()
    return response_json['choices'][0]['message']['content']

if api_key and video_url:
    st.write("Processing...")
    audio_file_path = download_audio(video_url)
    
    if audio_file_path:
        st.write("Audio downloaded successfully.")
        
        transcription = transcribe_audio(audio_file_path, api_key)
        st.write("Transcription completed successfully.")
        st.text_area("Transcription", transcription, height=300)
        
        blog_post = generate_blog_post(transcription, api_key)
        st.write("Blog post generated successfully.")
        st.text_area("SEO Blog Post", blog_post, height=300)
        
        # Adding a copy button for the generated blog post
        st.code(blog_post, language="markdown")
        st.button("Copy to Clipboard")
else:
    st.info("Please enter both your OpenAI API key and YouTube video URL.")
