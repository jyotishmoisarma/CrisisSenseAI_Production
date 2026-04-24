import io
import json
import logging
import base64
import PIL.Image
from typing import List, Union
from google import genai
from openai import OpenAI
from config.settings import GEMINI_API_KEY, OPENROUTER_API_KEY

# Initialize logger
logger = logging.getLogger(__name__)

def analyze_image_and_text(image_bytes_list: Union[List[bytes], bytes] = None, user_text: str = None) -> str:
    """
    Multimodal Pre-processor that supports multiple images.
    Takes a list of image bytes (or a single bytes object) and the user's text description.
    """
    # FIX: If a single bytes object is passed instead of a list, wrap it in a list.
    if isinstance(image_bytes_list, bytes):
        image_bytes_list = [image_bytes_list]
    
    if not image_bytes_list and not user_text:
        return json.dumps({"status": "No evidence provided for analysis."})

    prompt = """
    You are an emergency triage vision assistant. 
    Analyze the provided user text and ALL provided emergency images.
    Identify hazards, injuries, and environmental risks across all images.
    Return ONLY a valid JSON object:
    {
      "visual_hazards": "string", 
      "visible_injuries": "string", 
      "environment_type": "string",
      "context_summary": "string"
    }
    """

    # --- PRIMARY: GEMINI (Stable Production String) ---
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        contents = [prompt]
        
        if user_text:
            contents.append(f"USER TEXT DESCRIPTION: {user_text}")
            
        if image_bytes_list:
            for img_bytes in image_bytes_list:
                img = PIL.Image.open(io.BytesIO(img_bytes))
                contents.append(img)
            
        response = client.models.generate_content(
            # Switched to stable non-preview string to resolve 404
            model="gemini-2.5-flash",
            contents=contents,
            config={"response_mime_type": "application/json"}
        )
        return response.text.strip()
        
    except Exception as e:
        logger.warning(f"Primary Gemini Vision failed: {str(e)}. Attempting OpenRouter fallback...")
        
        # --- FALLBACK: OPENROUTER (Updated Stable Free Endpoint) ---
        try:
            fallback_client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=OPENROUTER_API_KEY,
            )

            message_content = [{"type": "text", "text": prompt}]
            if user_text:
                message_content.append({"type": "text", "text": f"USER TEXT: {user_text}"})
            
            if image_bytes_list:
                for img_bytes in image_bytes_list:
                    base64_image = base64.b64encode(img_bytes).decode('utf-8')
                    message_content.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    })

            fallback_response = fallback_client.chat.completions.create(
                # Switched to stable production model endpoint
                model="google/gemini-2.0-flash-001",
                messages=[{"role": "user", "content": message_content}],
                response_format={"type": "json_object"}
            )
            
            return fallback_response.choices[0].message.content.strip()

        except Exception as fallback_error:
            logger.error(f"Both Vision pipelines failed: {str(fallback_error)}")
            # Fail gracefully by returning a structured error for the Commander to see
            return json.dumps({
                "error": "Visual forensics unavailable",
                "user_text_only": user_text if user_text else "No text provided"
            })