import requests
import os
from dotenv import load_dotenv
import time
from pathlib import Path

load_dotenv()

GLADIA_API_KEY = os.getenv("GLADIA_API_KEY")
AUDIO_FILE = "audio_samples/test_audio.mp3"

def transcribe_gladia(audio_file):
    """Transcribe audio using Gladia API."""
    # Check if file exists
    if not os.path.exists(audio_file):
        raise Exception(f"Audio file not found: {audio_file}")
    
    print(f"Processing file: {audio_file}")
    print(f"File size: {os.path.getsize(audio_file)} bytes")
    
    # First, upload the file to get a URL
    upload_url = "https://api.gladia.io/v2/upload"
    transcribe_url = "https://api.gladia.io/v2/pre-recorded"
    
    headers = {
        "x-gladia-key": GLADIA_API_KEY
    }
    
    # Upload the file first
    with open(audio_file, "rb") as audio:
        files = {"audio": (os.path.basename(audio_file), audio, "audio/mpeg")}
        print("Sending upload request...")
        upload_response = requests.post(upload_url, headers=headers, files=files)
        print(f"Upload response status: {upload_response.status_code}")
        print(f"Upload response: {upload_response.text}")
        
        if upload_response.status_code != 200:
            raise Exception(f"Gladia upload error: {upload_response.status_code} - {upload_response.text}")
        
        response_data = upload_response.json()
        audio_url = response_data.get("audio_url")
        if not audio_url:
            raise Exception("Failed to get audio URL from upload response")
        
        print(f"Got audio URL: {audio_url}")
    
    # Request transcription using the audio URL
    json_data = {"audio_url": audio_url}
    response = requests.post(transcribe_url, headers=headers, json=json_data)
    print(f"Transcription request status: {response.status_code}")
    print(f"Transcription response: {response.text}")
    
    # Accept both 200 and 201 as success status codes
    if response.status_code not in [200, 201]:
        raise Exception(f"Gladia transcription error: {response.status_code} - {response.text}")
    
    result = response.json()
    transcription_id = result.get("id")
    
    if not transcription_id:
        raise Exception("No transcription ID received")
    
    print(f"Got transcription ID: {transcription_id}")
    
    # Poll for the transcription result
    while True:
        status_url = f"https://api.gladia.io/v2/pre-recorded/{transcription_id}"
        status_response = requests.get(status_url, headers=headers)
        print(f"Status check response: {status_response.text}")
        
        if status_response.status_code != 200:
            raise Exception(f"Gladia status check error: {status_response.status_code} - {status_response.text}")
        
        status_result = status_response.json()
        status = status_result.get("status")
        
        if status == "completed":
            return status_result
        elif status == "error":
            raise Exception(f"Transcription failed: {status_result.get('error', 'Unknown error')}")
        
        time.sleep(1)  # Wait 1 second before polling again

if __name__ == "__main__":
    result = transcribe_gladia(AUDIO_FILE)
    print(result) 