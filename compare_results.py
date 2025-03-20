from deepgram_test import transcribe_deepgram
from assemblyai_test import transcribe_assemblyai

AUDIO_FILE = "audio_samples/test_audio.mp3"

deepgram_result = transcribe_deepgram(AUDIO_FILE)
assemblyai_result = transcribe_assemblyai(AUDIO_FILE)

print("\n🔹 Deepgram Transcription:")
print(deepgram_result.get("results", {}).get("channels", [{}])[0].get("alternatives", [{}])[0].get("transcript", "No transcript found."))

print("\n🔹 AssemblyAI Transcription:")
print(assemblyai_result.get("text", "No transcript found."))
