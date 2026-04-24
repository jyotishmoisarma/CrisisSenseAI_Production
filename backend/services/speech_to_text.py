import json
import logging
from google import genai
from config.settings import GEMINI_API_KEY

# Configure logging to track AI performance and failures
logger = logging.getLogger(__name__)

def convert_audio(audio_bytes: bytes, mime_type: str = "audio/mp3") -> str:
    """
    Analyzes emergency audio for transcription, emotional tone, and background forensics.
    Synchronized with gemini-2.5-flash to match working environment logs.
    """
    if not audio_bytes:
        return None

    # Robustness: Gemini's audio processing can handle video/mp4 as audio source, 
    # but we ensure the mime_type is valid for the generative model.
    valid_mimes = ["audio/wav", "audio/mp3", "audio/aiff", "audio/aac", "audio/ogg", "audio/flac", "video/mp4", "video/webm"]
    
    current_mime = mime_type if mime_type in valid_mimes else "audio/mp3"

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        # Enhanced prompt for better situational awareness
        prompt = """
        CRITICAL TASK: Analyze this emergency audio.
        1. Transcript: Provide a verbatim transcription of any speech.
        2. Emotion: Identify the speaker's emotional state (Distressed, Panicked, Controlled).
        3. Forensics: Identify background sounds (Fire crackling, sirens, glass breaking, wind).
        
        Return ONLY a valid JSON object:
        {
          "transcript": "string",
          "emotional_tone": "string",
          "background_noise": "string",
          "distress_level": "high/medium/low"
        }
        """
        
        # Using gemini-2.5-flash as it is confirmed working in your logs
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                prompt,
                {"inline_data": {"mime_type": current_mime, "data": audio_bytes}}
            ],
            config={"response_mime_type": "application/json"}
        )
        
        result_text = response.text.strip()
        logger.info(f"Audio analysis (MIME: {current_mime}) successfully processed.")
        return result_text

    except Exception as e:
        logger.error(f"Audio analysis engine failure: {str(e)}")
        # Returns a failsafe JSON string so the rest of the pipeline can continue
        return json.dumps({
            "error": f"Audio service failed: {str(e)}",
            "transcript": "Audio stream unreadable or model overloaded.",
            "emotional_tone": "unknown",
            "distress_level": "medium"
        })