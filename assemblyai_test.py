import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
AUDIO_FILE = "audio_samples/test_audio.mp3"

def transcribe_assemblyai(audio_file):
    upload_url = "https://api.assemblyai.com/v2/upload"
    transcribe_url = "https://api.assemblyai.com/v2/transcript"
    
    headers = {"Authorization": ASSEMBLYAI_API_KEY}
    
    # Upload the file
    with open(audio_file, "rb") as audio:
        response = requests.post(upload_url, headers=headers, files={"file": audio})
        audio_url = response.json()["upload_url"]
    
    # Request transcription
    json_data = {"audio_url": audio_url}  # Using default model
    response = requests.post(transcribe_url, headers=headers, json=json_data)
    transcript_id = response.json()["id"]
    
    # Poll for completion
    while True:
        response = requests.get(f"{transcribe_url}/{transcript_id}", headers=headers)
        status = response.json()["status"]
        
        if status == "completed":
            return response.json()
        elif status == "error":
            raise Exception(f"Transcription failed: {response.json().get('error', 'Unknown error')}")
        
        time.sleep(1)  # Wait 1 second before polling again

if __name__ == "__main__":
    result = transcribe_assemblyai(AUDIO_FILE)
    print(result)
