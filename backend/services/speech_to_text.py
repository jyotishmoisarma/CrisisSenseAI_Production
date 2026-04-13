import json
from google import genai
from config.settings import GEMINI_API_KEY

def convert_audio(audio_bytes: bytes, mime_type: str = "audio/mp3") -> str:
    """
    Audio Pre-processor (Feature 2).
    Analyzes audio for transcription and environmental sounds.
    """
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        prompt = """
        Analyze this emergency audio clip. 
        Transcribe the words and detect background distress signals.
        Return ONLY a JSON object:
        {
          "transcript": "actual words spoken", 
          "emotional_tone": "panicked/calm/screaming", 
          "background_noise": "fire/sirens/gunshots/wind/none"
        }
        """
        
        response = client.models.generate_content(
            model="gemini-3.1-flash",
            contents=[
                prompt,
                {"inline_data": {"mime_type": mime_type, "data": audio_bytes}}
            ],
            config={"response_mime_type": "application/json"}
        )
        return response.text.strip()
    except Exception as e:
        print(f"Audio Processor Error: {str(e)}")
        return json.dumps({"error": f"Audio processing failed: {str(e)}"})