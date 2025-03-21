import os
import time
from pathlib import Path
from deepgram_test import transcribe_deepgram
from assemblyai_test import transcribe_assemblyai
from gladia_test import transcribe_gladia
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

def analyze_stt_services(audio_path):
    """Analyze and compare results from all STT services."""
    results = {
        "deepgram": {"transcript": "", "time": 0, "status": "❌ Failed"},
        "assemblyai": {"transcript": "", "time": 0, "status": "❌ Failed"},
        "gladia": {"transcript": "", "time": 0, "status": "❌ Failed"}
    }
    
    # Test Deepgram
    try:
        start_time = time.time()
        deepgram_result = transcribe_deepgram(audio_path)
        deepgram_time = time.time() - start_time
        
        transcript = deepgram_result.get("results", {}).get("channels", [{}])[0].get("alternatives", [{}])[0].get("transcript", "")
        confidence = deepgram_result.get("results", {}).get("channels", [{}])[0].get("alternatives", [{}])[0].get("confidence", 0)
        
        results["deepgram"] = {
            "transcript": transcript,
            "time": f"{deepgram_time:.2f}s",
            "confidence": f"{confidence:.2%}",
            "status": "✅ Success"
        }
        logger.info("Deepgram transcription completed")
    except Exception as e:
        results["deepgram"]["error"] = str(e)
        logger.error(f"Deepgram error: {str(e)}")
    
    # Test AssemblyAI
    try:
        start_time = time.time()
        assemblyai_result = transcribe_assemblyai(audio_path)
        assemblyai_time = time.time() - start_time
        
        transcript = assemblyai_result.get("text", "")
        confidence = assemblyai_result.get("confidence", 0)
        
        results["assemblyai"] = {
            "transcript": transcript,
            "time": f"{assemblyai_time:.2f}s",
            "confidence": f"{confidence:.2%}",
            "status": "✅ Success"
        }
        logger.info("AssemblyAI transcription completed")
    except Exception as e:
        results["assemblyai"]["error"] = str(e)
        logger.error(f"AssemblyAI error: {str(e)}")
    
    # Test Gladia
    try:
        start_time = time.time()
        gladia_result = transcribe_gladia(audio_path)
        gladia_time = time.time() - start_time
        
        results["gladia"] = {
            "transcript": gladia_result.get("text", ""),
            "time": f"{gladia_time:.2f}s",
            "confidence": f"{gladia_result.get('confidence', 0):.2%}",
            "status": "✅ Success"
        }
        logger.info("Gladia transcription completed")
    except Exception as e:
        results["gladia"]["error"] = str(e)
        logger.error(f"Gladia error: {str(e)}")
    
    return results

def generate_report(results, audio_file):
    """Generate a detailed report of the analysis."""
    report = f"""
# STT Service Analysis Report
Audio File: {os.path.basename(audio_file)}

## Deepgram Results
Status: {results['deepgram']['status']}
Processing Time: {results['deepgram'].get('time', 'N/A')}
Confidence: {results['deepgram'].get('confidence', 'N/A')}
Transcript:
{results['deepgram']['transcript']}

## AssemblyAI Results
Status: {results['assemblyai']['status']}
Processing Time: {results['assemblyai'].get('time', 'N/A')}
Confidence: {results['assemblyai'].get('confidence', 'N/A')}
Transcript:
{results['assemblyai']['transcript']}

## Gladia Results
Status: {results['gladia']['status']}
Processing Time: {results['gladia'].get('time', 'N/A')}
Confidence: {results['gladia'].get('confidence', 'N/A')}
Transcript:
{results['gladia']['transcript']}

## Comparison Summary
1. Processing Speed:
   - Deepgram: {results['deepgram'].get('time', 'N/A')}
   - AssemblyAI: {results['assemblyai'].get('time', 'N/A')}
   - Gladia: {results['gladia'].get('time', 'N/A')}

2. Confidence Scores:
   - Deepgram: {results['deepgram'].get('confidence', 'N/A')}
   - AssemblyAI: {results['assemblyai'].get('confidence', 'N/A')}
   - Gladia: {results['gladia'].get('confidence', 'N/A')}

3. Success Status:
   - Deepgram: {results['deepgram']['status']}
   - AssemblyAI: {results['assemblyai']['status']}
   - Gladia: {results['gladia']['status']}
"""
    return report

def main():
    # Create results directory if it doesn't exist
    results_dir = Path("test_results")
    results_dir.mkdir(exist_ok=True)
    
    # Test audio file
    audio_file = "audio_samples/test_audio.mp3"
    
    # Run analysis
    logger.info("Starting STT service analysis...")
    results = analyze_stt_services(audio_file)
    
    # Generate report
    report = generate_report(results, audio_file)
    
    # Save report
    report_file = results_dir / "stt_analysis_report.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)
    
    logger.info(f"Analysis complete. Report saved to {report_file}")
    print(report)

if __name__ == "__main__":
    main() 