import requests
import os
from dotenv import load_dotenv
import time
from pathlib import Path

load_dotenv()

ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
AUDIO_FILE = "audio_samples/test_audio.mp3"

def transcribe_assemblyai(audio_file):
    """Transcribe audio using AssemblyAI API."""
    # Check if file exists
    if not os.path.exists(audio_file):
        raise Exception(f"Audio file not found: {audio_file}")
    
    print(f"Processing file: {audio_file}")
    print(f"File size: {os.path.getsize(audio_file)} bytes")
    
    # First, upload the file to get a URL
    upload_url = "https://api.assemblyai.com/v2/upload"
    transcribe_url = "https://api.assemblyai.com/v2/transcript"
    
    headers = {
        "authorization": ASSEMBLYAI_API_KEY,
        "content-type": "application/json"
    }
    
    # Upload the file first
    with open(audio_file, "rb") as audio:
        files = {"file": (os.path.basename(audio_file), audio, "audio/mpeg")}
        print("Sending upload request...")
        upload_response = requests.post(upload_url, headers={"authorization": ASSEMBLYAI_API_KEY}, files=files)
        print(f"Upload response status: {upload_response.status_code}")
        print(f"Upload response: {upload_response.text}")
        
        if upload_response.status_code != 200:
            raise Exception(f"AssemblyAI upload error: {upload_response.status_code} - {upload_response.text}")
        
        response_data = upload_response.json()
        audio_url = response_data.get("upload_url")
        if not audio_url:
            raise Exception("Failed to get audio URL from upload response")
        
        print(f"Got audio URL: {audio_url}")
    
    # Request transcription using the audio URL
    json_data = {"audio_url": audio_url}
    response = requests.post(transcribe_url, headers=headers, json=json_data)
    print(f"Transcription request status: {response.status_code}")
    print(f"Transcription response: {response.text}")
    
    if response.status_code != 200:
        raise Exception(f"AssemblyAI transcription error: {response.status_code} - {response.text}")
    
    result = response.json()
    transcript_id = result.get("id")
    
    if not transcript_id:
        raise Exception("No transcript ID received")
    
    print(f"Got transcript ID: {transcript_id}")
    
    # Poll for the transcription result
    while True:
        status_url = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
        status_response = requests.get(status_url, headers=headers)
        print(f"Status check response: {status_response.text}")
        
        if status_response.status_code != 200:
            raise Exception(f"AssemblyAI status check error: {status_response.status_code} - {status_response.text}")
        
        status_result = status_response.json()
        status = status_result.get("status")
        
        if status == "completed":
            return status_result
        elif status == "error":
            raise Exception(f"Transcription failed: {status_result.get('error', 'Unknown error')}")
        
        time.sleep(1)  # Wait 1 second before polling again

if __name__ == "__main__":
    result = transcribe_assemblyai(AUDIO_FILE)
    print(result)
