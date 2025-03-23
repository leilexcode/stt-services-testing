import os
import requests
import logging
from pathlib import Path
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def transcribe_assemblyai(audio_file):
    """Transcribe audio using AssemblyAI API with enhanced configuration"""
    try:
        # Check if file exists
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"Audio file not found: {audio_file}")
        
        # Log file size for diagnostics
        file_size = os.path.getsize(audio_file)
        logger.info(f"Processing file: {audio_file} (Size: {file_size/1024/1024:.2f} MB)")
        
        # AssemblyAI API configuration
        API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
        if not API_KEY:
            raise ValueError("ASSEMBLYAI_API_KEY not found in environment variables")
        
        # API endpoints
        UPLOAD_URL = "https://api.assemblyai.com/v2/upload"
        TRANSCRIPT_URL = "https://api.assemblyai.com/v2/transcript"
        
        # Headers
        headers = {
            "authorization": API_KEY,
            "content-type": "application/json"
        }
        
        # Upload the audio file
        with open(audio_file, "rb") as f:
            upload_response = requests.post(
                UPLOAD_URL,
                headers={"authorization": API_KEY},
                data=f
            )
        
        if upload_response.status_code != 200:
            raise Exception(f"Upload failed: {upload_response.text}")
        
        audio_url = upload_response.json()["upload_url"]
        logger.info("Audio file uploaded successfully")
        
        # Configure transcription request
        transcript_request = {
            "audio_url": audio_url,
            "language_code": "en",  # Specify language for better accuracy
            "punctuate": True,      # Enable punctuation
            "format_text": True,    # Format text for readability
            "boost_param": "high",  # High quality transcription
            "word_boost": [],       # Add specific words to boost if needed
            "filter_profanity": False,  # Keep profanity for accuracy
            "redact_pii": False,    # Don't redact personal information
            "speaker_labels": True, # Enable speaker diarization
            "utterances": True,     # Split into utterances
            "auto_chapters": True,  # Generate chapters
            "entity_detection": True,  # Detect entities
            "sentiment_analysis": True,  # Analyze sentiment
            "content_safety": True,  # Check content safety
            "iab_categories": True,  # Categorize content
            "custom_spelling": {},  # Custom spelling corrections
            "throttled": False,     # Don't throttle processing
            "audio_enhancement": True  # Enhance audio quality
        }
        
        # Request transcription
        transcript_response = requests.post(
            TRANSCRIPT_URL,
            json=transcript_request,
            headers=headers
        )
        
        if transcript_response.status_code != 200:
            raise Exception(f"Transcription request failed: {transcript_response.text}")
        
        transcript_id = transcript_response.json().get("id")
        if not transcript_id:
            raise Exception("No transcript ID received")
        
        logger.info(f"Transcription started with ID: {transcript_id}")
        
        # Poll for completion
        while True:
            polling_response = requests.get(
                f"{TRANSCRIPT_URL}/{transcript_id}",
                headers=headers
            )
            
            if polling_response.status_code != 200:
                raise Exception(f"Polling failed: {polling_response.text}")
            
            polling_result = polling_response.json()
            status = polling_result.get("status")
            
            if status == "completed":
                logger.info("Transcription completed successfully")
                return polling_result
            elif status == "error":
                raise Exception(f"Transcription failed: {polling_result.get('error')}")
            
            time.sleep(3)  # Wait before polling again
        
    except Exception as e:
        logger.error(f"AssemblyAI transcription error: {str(e)}")
        raise

if __name__ == "__main__":
    result = transcribe_assemblyai("audio_samples/test_audio.mp3")
    print(result)
