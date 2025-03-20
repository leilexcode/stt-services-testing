import requests
import os
from dotenv import load_dotenv

load_dotenv()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
AUDIO_FILE = "audio_samples/test_audio.mp3"  # Change this to your file

def transcribe_deepgram(audio_file):
    url = "https://api.deepgram.com/v1/listen"
    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Content-Type": "audio/mpeg"
    }
    
    with open(audio_file, "rb") as audio:
        response = requests.post(url, headers=headers, data=audio)
    
    return response.json()

if __name__ == "__main__":
    result = transcribe_deepgram(AUDIO_FILE)
    print(result)
