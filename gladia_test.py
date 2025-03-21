import requests
import os
from dotenv import load_dotenv
import logging

# Configure logging to show only INFO and above
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'  # Simplified format to show only the message
)
logger = logging.getLogger(__name__)

load_dotenv()

GLADIA_API_KEY = os.getenv("GLADIA_API_KEY")
AUDIO_FILE = "audio_samples/test_audio.mp3"

def transcribe_gladia(audio_path):
    """Transcribe audio using Gladia API."""
    try:
        # Get API key
        api_key = os.getenv("GLADIA_API_KEY")
        if not api_key:
            raise ValueError("GLADIA_API_KEY not found in environment variables")

        # Check if file exists
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        logger.info(f"Processing: {os.path.basename(audio_path)}")

        # API endpoint
        url = "https://api.gladia.io/audio/text/transcription"
        
        # Headers
        headers = {
            "x-gladia-key": api_key
        }
        
        # Upload and transcribe
        with open(audio_path, 'rb') as f:
            files = {'audio': f}
            response = requests.post(url, files=files, headers=headers)
            
            if response.status_code not in [200, 201]:
                raise Exception(f"Request failed: {response.text}")
            
            result = response.json()
            logger.info("Transcription completed successfully")
            
            return {
                "text": result.get("transcription", ""),
                "confidence": result.get("confidence", 0)
            }
                
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    result = transcribe_gladia(AUDIO_FILE)
    print(result) 