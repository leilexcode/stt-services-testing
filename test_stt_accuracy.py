import os
import time
import json
import logging
from typing import Dict, Any
from pathlib import Path
from datetime import datetime
from deepgram_test import transcribe_deepgram
from assemblyai_test import transcribe_assemblyai

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stt_test_results.log'),
        logging.StreamHandler()
    ]
)

class STTAccuracyTester:
    def __init__(self, audio_dir: str = "audio_samples"):
        self.audio_dir = Path(audio_dir)
        self.results_dir = Path("test_results")
        self.results_dir.mkdir(exist_ok=True)
        
    def process_audio_file(self, audio_file: Path) -> Dict[str, Any]:
        """Process a single audio file with both services and return results."""
        results = {
            "file_name": audio_file.name,
            "file_size": audio_file.stat().st_size,
            "timestamp": datetime.now().isoformat(),
            "services": {}
        }
        
        # Test Deepgram
        try:
            start_time = time.time()
            deepgram_result = transcribe_deepgram(str(audio_file))
            deepgram_time = time.time() - start_time
            
            results["services"]["deepgram"] = {
                "transcript": deepgram_result.get("results", {}).get("channels", [{}])[0].get("alternatives", [{}])[0].get("transcript", ""),
                "processing_time": deepgram_time,
                "confidence": deepgram_result.get("results", {}).get("channels", [{}])[0].get("alternatives", [{}])[0].get("confidence", 0),
                "success": True
            }
        except Exception as e:
            logging.error(f"Deepgram error processing {audio_file.name}: {str(e)}")
            results["services"]["deepgram"] = {
                "error": str(e),
                "success": False
            }
        
        # Test AssemblyAI
        try:
            start_time = time.time()
            assemblyai_result = transcribe_assemblyai(str(audio_file))
            assemblyai_time = time.time() - start_time
            
            results["services"]["assemblyai"] = {
                "transcript": assemblyai_result.get("text", ""),
                "processing_time": assemblyai_time,
                "confidence": assemblyai_result.get("confidence", 0),
                "success": True
            }
        except Exception as e:
            logging.error(f"AssemblyAI error processing {audio_file.name}: {str(e)}")
            results["services"]["assemblyai"] = {
                "error": str(e),
                "success": False
            }
        
        return results
    
    def save_results(self, results: Dict[str, Any], audio_file: Path):
        """Save test results to a JSON file."""
        result_file = self.results_dir / f"{audio_file.stem}_results.json"
        with open(result_file, 'w') as f:
            json.dump(results, f, indent=2)
        logging.info(f"Results saved to {result_file}")
    
    def run_tests(self):
        """Run tests on all audio files in the audio directory."""
        audio_files = list(self.audio_dir.glob("*.mp3")) + list(self.audio_dir.glob("*.wav"))
        
        if not audio_files:
            logging.error("No audio files found in the audio_samples directory")
            return
        
        logging.info(f"Found {len(audio_files)} audio files to test")
        
        for audio_file in audio_files:
            logging.info(f"Processing {audio_file.name}")
            results = self.process_audio_file(audio_file)
            self.save_results(results, audio_file)
            
            # Print summary
            if results["services"]["deepgram"]["success"]:
                logging.info(f"Deepgram transcript: {results['services']['deepgram']['transcript'][:100]}...")
            if results["services"]["assemblyai"]["success"]:
                logging.info(f"AssemblyAI transcript: {results['services']['assemblyai']['transcript'][:100]}...")

if __name__ == "__main__":
    tester = STTAccuracyTester()
    tester.run_tests() 