import gradio as gr
import json
from pathlib import Path
from deepgram_test import transcribe_deepgram
from assemblyai_test import transcribe_assemblyai
from gladia_test import transcribe_gladia
import time

def process_audio(audio_path):
    """Process audio file and return comparison results."""
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
    except Exception as e:
        results["deepgram"]["error"] = str(e)
    
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
    except Exception as e:
        results["assemblyai"]["error"] = str(e)
    
    # Test Gladia
    try:
        start_time = time.time()
        gladia_result = transcribe_gladia(audio_path)
        gladia_time = time.time() - start_time
        
        transcript = gladia_result.get("transcription", "")
        confidence = gladia_result.get("confidence", 1.0)
        
        results["gladia"] = {
            "transcript": transcript,
            "time": f"{gladia_time:.2f}s",
            "confidence": f"{confidence:.2%}",
            "status": "✅ Success"
        }
        
        # Log the raw response for debugging
        print(f"Gladia raw response: {gladia_result}")
    except Exception as e:
        results["gladia"]["error"] = str(e)
    
    # Format the output
    output = f"""
### Deepgram Results
**Status:** {results['deepgram']['status']}
**Processing Time:** {results['deepgram'].get('time', 'N/A')}
**Confidence:** {results['deepgram'].get('confidence', 'N/A')}
**Transcript:**
{results['deepgram']['transcript']}

### AssemblyAI Results
**Status:** {results['assemblyai']['status']}
**Processing Time:** {results['assemblyai'].get('time', 'N/A')}
**Confidence:** {results['assemblyai'].get('confidence', 'N/A')}
**Transcript:**
{results['assemblyai']['transcript']}

### Gladia Results
**Status:** {results['gladia']['status']}
**Processing Time:** {results['gladia'].get('time', 'N/A')}
**Confidence:** {results['gladia'].get('confidence', 'N/A')}
**Transcript:**
{results['gladia']['transcript']}
"""
    
    return output

# Create Gradio interface
with gr.Blocks(title="STT Service Comparison", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # Speech-to-Text Service Comparison
    Compare transcription results between Deepgram, AssemblyAI, and Gladia
    
    Upload an audio file (MP3 or WAV) to see the transcription results from all services.
    """)
    
    with gr.Row():
        with gr.Column():
            audio_input = gr.Audio(
                label="Upload Audio",
                type="filepath"
            )
    
    with gr.Row():
        transcribe_btn = gr.Button("Transcribe", variant="primary")
    
    with gr.Row():
        output = gr.Markdown(label="Results")
    
    transcribe_btn.click(
        fn=process_audio,
        inputs=[audio_input],
        outputs=[output]
    )

if __name__ == "__main__":
    demo.launch(share=True) 