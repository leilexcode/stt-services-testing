import gradio as gr
import os
from pathlib import Path
from deepgram_test import transcribe_deepgram
from assemblyai_test import transcribe_assemblyai
from gladia_test import transcribe_gladia
import time

def process_audio(audio_file):
    """Process audio through all three services and return formatted results"""
    results = {
        "deepgram": {"status": "❌ Failed"},
        "assemblyai": {"status": "❌ Failed"},
        "gladia": {"status": "❌ Failed"}
    }
    
    try:
        # Process with Deepgram
        start_time = time.time()
        deepgram_result = transcribe_deepgram(audio_file)
        deepgram_time = time.time() - start_time
        
        # Extract just the transcript from Deepgram's response
        transcript = deepgram_result.get("results", {}).get("channels", [{}])[0].get("alternatives", [{}])[0].get("transcript", "")
        confidence = deepgram_result.get("results", {}).get("channels", [{}])[0].get("alternatives", [{}])[0].get("confidence", 0)
        
        results["deepgram"] = {
            "status": "✅ Success",
            "transcript": transcript,
            "time": f"{deepgram_time:.2f}s",
            "confidence": f"{confidence:.2%}"
        }
    except Exception as e:
        results["deepgram"]["error"] = str(e)
    
    try:
        # Process with AssemblyAI
        start_time = time.time()
        assemblyai_result = transcribe_assemblyai(audio_file)
        assemblyai_time = time.time() - start_time
        
        transcript = assemblyai_result.get("text", "")
        confidence = assemblyai_result.get("confidence", 0)
        
        results["assemblyai"] = {
            "status": "✅ Success",
            "transcript": transcript,
            "time": f"{assemblyai_time:.2f}s",
            "confidence": f"{confidence:.2%}"
        }
    except Exception as e:
        results["assemblyai"]["error"] = str(e)
    
    try:
        # Process with Gladia
        start_time = time.time()
        gladia_result = transcribe_gladia(audio_file)
        gladia_time = time.time() - start_time
        
        # Handle Gladia response structure
        transcript = ""
        confidence = 1.0  # Default confidence
        
        if isinstance(gladia_result, dict):
            if "transcription" in gladia_result:
                transcript = gladia_result["transcription"]
            elif "text" in gladia_result:
                transcript = gladia_result["text"]
            elif "prediction" in gladia_result:
                transcript = gladia_result["prediction"]
            
            confidence = gladia_result.get("confidence", 1.0)
        
        results["gladia"] = {
            "status": "✅ Success",
            "transcript": transcript,
            "time": f"{gladia_time:.2f}s",
            "confidence": f"{confidence:.2%}"
        }
    except Exception as e:
        results["gladia"]["error"] = str(e)
    
    # Format results as markdown
    markdown = """
# Transcription Results

## Deepgram
**Status**: {deepgram[status]}
**Processing Time**: {deepgram[time]}
**Confidence**: {deepgram[confidence]}
**Transcript**:
{deepgram[transcript]}

## AssemblyAI
**Status**: {assemblyai[status]}
**Processing Time**: {assemblyai[time]}
**Confidence**: {assemblyai[confidence]}
**Transcript**:
{assemblyai[transcript]}

## Gladia
**Status**: {gladia[status]}
**Processing Time**: {gladia[time]}
**Confidence**: {gladia[confidence]}
**Transcript**:
{gladia[transcript]}
""".format(**results)
    
    return markdown

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

    gr.Markdown("""
    ### Notes:
    - Supported formats: MP3, WAV
    - For best results, use clear audio with minimal background noise
    - Processing may take a few seconds
    """)

if __name__ == "__main__":
    demo.launch(
        share=True,  # Enable public URL
        server_name="0.0.0.0",  # Allow external connections
        server_port=7860,  # Use default port
        show_error=True,  # Show detailed error messages
        debug=True  # Enable debug mode for more information
    ) 