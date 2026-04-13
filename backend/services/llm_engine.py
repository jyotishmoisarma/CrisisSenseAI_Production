import json
import re
import time
import logging
from google import genai
from openai import OpenAI
from config.settings import GEMINI_API_KEY, OPENROUTER_API_KEY

# Configure logging for emergency tracking
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TriageCommander")

def clean_and_parse_json(text):
    """
    A bulletproof JSON parser that extracts JSON blocks from AI responses,
    handling markdown backticks, conversational text, and formatting errors.
    """
    if not text:
        raise ValueError("Received empty text for JSON parsing")
        
    try:
        # Step 1: Look for the first { and the last }
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            json_str = match.group()
            # Remove any trailing commas that might break standard json.loads
            json_str = re.sub(r',\s*}', '}', json_str)
            return json.loads(json_str)
        
        # Step 2: Direct load fallback
        return json.loads(text)
    except (json.JSONDecodeError, AttributeError, TypeError) as e:
        logger.error(f"JSON Parsing failed for text: {text[:200]}...")
        raise ValueError(f"Invalid JSON format: {str(e)}")

def analyze_with_ai(context: str, user_profile: dict):
    """
    The CrisisSenseAI Triage Commander (Main Intelligence Engine).
    Coordinates the final decision-making process by combining the
    multi-modal context with the user's filtered medical profile.
    
    This function features aggressive fallback logic to ensure
    an emergency decision is ALWAYS reached.
    """
    
    system_instruction = """
    ROLE: You are the CrisisSenseAI Triage Commander, an elite emergency response intelligence.
    
    MISSION: 
    Evaluate the provided incident context (Visual, Audio, and Text inputs) 
    alongside the User's Medical Profile to provide life-saving instructions.
    
    PROTOCOL:
    1. Severity (1-10): Be objective. 10 is immediate threat to life.
    2. Status: 
       - CRITICAL: Life/limb threat. Requires immediate action.
       - URGENT: Serious but not instantly fatal.
       - STABLE: Minor or situational concern.
    3. System Actions: Select from [CALL_AMBULANCE, ALERT_CONTACTS, BROADCAST_NEIGHBORHOOD, FLASH_LIGHT, NONE].
    4. Steps: Provide 3-5 imperative, short instructions (e.g., 'Apply pressure').
    5. Medical: Tailor advice to their specific blood group/conditions if applicable.
    
    STRICT OUTPUT FORMAT (JSON ONLY):
    {
      "severity_score": number,
      "status_level": "CRITICAL" | "URGENT" | "STABLE",
      "system_actions": ["ACTION1", "ACTION2"],
      "immediate_steps": ["Step 1", "Step 2", "Step 3"],
      "medical_notes": "string",
      "triage_summary": "3 word summary"
    }
    """

    user_payload = f"""
    [USER MEDICAL PROFILE]
    {json.dumps(user_profile, indent=2)}

    [EMERGENCY CONTEXT REPORT]
    {context}
    
    Evaluate now.
    """

    # --- PRIMARY MODEL: GEMINI 3.1 FLASH ---
    for attempt in range(3):  # Simple retry logic for primary
        try:
            client = genai.Client(api_key=GEMINI_API_KEY)
            response = client.models.generate_content(
                model="gemini-3.1-flash", 
                contents=user_payload,
                config={
                    "system_instruction": system_instruction,
                    "response_mime_type": "application/json"
                }
            )
            
            if response and hasattr(response, 'text'):
                return clean_and_parse_json(response.text)
            raise ValueError("Empty response from primary model.")
            
        except Exception as gemini_error:
            logger.warning(f"Primary Gemini attempt {attempt+1} failed: {str(gemini_error)}")
            if attempt < 2:
                time.sleep(1)
                continue
            
            # --- SECONDARY FALLBACK: OPENROUTER / NVIDIA ---
            logger.info("Switching to Secondary Fallback (OpenRouter/NVIDIA)...")
            try:
                fallback_client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=OPENROUTER_API_KEY,
                )

                fallback_response = fallback_client.chat.completions.create(
                    model="nvidia/nemotron-nano-12b-v2-vl:free",
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": user_payload}
                    ],
                    response_format={"type": "json_object"}
                )
                
                raw_content = fallback_response.choices[0].message.content
                return clean_and_parse_json(raw_content)

            except Exception as fallback_error:
                logger.critical("ALL AI ENGINES FAILED. TRIGGERING FAILSAFE MODE.")
                # --- FAILSAFE HARDCODED RESPONSE ---
                return {
                    "severity_score": 10,
                    "status_level": "CRITICAL",
                    "triage_summary": "SYSTEM EMERGENCY OFFLINE",
                    "immediate_steps": [
                        "Manually call emergency services (911/999) immediately.",
                        "Stay on the line with human operators.",
                        "If bleeding, apply direct pressure with a clean cloth.",
                        "Do not move if you suspect neck or back injury."
                    ],
                    "system_actions": ["CALL_AMBULANCE"],
                    "medical_notes": "AI triage unavailable. Manual intervention required.",
                    "error_log": f"Gemini: {str(gemini_error)} | Fallback: {str(fallback_error)}"
                }