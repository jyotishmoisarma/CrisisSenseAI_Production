import io
import json
import logging
import PIL.Image
from google import genai
from config.settings import GEMINI_API_KEY

# Initialize logger
logger = logging.getLogger(__name__)

def analyze_image_and_text(image_bytes: bytes = None, user_text: str = None) -> str:
   
    if not image_bytes and not user_text:
        return json.dumps({"status": "No image or text provided for visual analysis."})

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        prompt = """
        You are an emergency triage vision assistant. 
        Your task is to analyze the provided user text and/or emergency image content.
        Provide a detailed situational evaluation for a follow-up triage engine.
        
        Focus on:
        1. Visible Hazards: Fire, smoke, weapons, chemicals, structural damage, water.
        2. Visible Injuries: Bleeding, unconsciousness, burns, trauma.
        3. Environment: Is the user indoors, on a road, in a forest, or a public building?
        4. Intent: Based on the text, what is the user asking for or panicking about?
        
        Return ONLY a valid JSON object:
        {
          "visual_hazards": "string describing hazards", 
          "visible_injuries": "string describing medical evidence", 
          "environment_type": "indoors/outdoors/commercial/residential/road",
          "context_summary": "brief summary of the visual/text evidence"
        }
        """
        
        contents = [prompt]
        
        if user_text:
            contents.append(f"USER TEXT DESCRIPTION: {user_text}")
            
        if image_bytes:
            try:
                img = PIL.Image.open(io.BytesIO(image_bytes))
                contents.append(img)
            except Exception as img_err:
                logger.error(f"Failed to process image bytes: {str(img_err)}")
                contents.append("[Image provided but could not be parsed by PIL]")
            
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config={
                "response_mime_type": "application/json"
            }
        )
        
        if not response or not hasattr(response, 'text'):
            raise ValueError("No text returned from Gemini vision model.")
            
        return response.text.strip()
        
    except Exception as e:
        logger.error(f"Image/Text analysis failed: {str(e)}")
        return json.dumps({
            "error": "Visual processing failed", 
            "details": str(e)
        })