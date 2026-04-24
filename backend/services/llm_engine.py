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
    Finds and parses JSON within a string. 
    Handles cases where AI returns markdown code blocks or extra conversational text.
    """
    if not text:
        raise ValueError("Received empty text for JSON parsing")
        
    try:
        # Look for the content between the first { and the last }
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            json_str = match.group()
            # Remove any trailing commas that might break standard json.loads
            json_str = re.sub(r',\s*}', '}', json_str)
            return json.loads(json_str)
        
        return json.loads(text)
    except (json.JSONDecodeError, AttributeError, TypeError) as e:
        logger.error(f"JSON Parsing failed: {text[:200]}...")
        return {
            "severity_score": 7,
            "status_level": "URGENT",
            "confidence_score": 0.5,
            "situation_analysis": "Parsing Error - Manual Review Required",
            "actionable_steps": ["Stay calm.", "Ensure personal safety.", "Call 112 manually."],
            "action_buttons": ["CALL_AMBULANCE"],
            "medical_notes": "System error during analysis."
        }

def analyze_with_ai(context: str, user_profile: dict = None):
    """
    Triage Commander: Determines severity and necessary actions based on 
    incident context and user profile.
    """
    has_contact = False
    if user_profile and user_profile.get('emergency_contact'):
        contact = str(user_profile.get('emergency_contact')).strip()
        if contact and contact.lower() not in ["none", "null", ""]:
            has_contact = True

    # We use double braces {{ }} ONLY inside this f-string to define the JSON structure
    system_instruction = f"""
    ROLE: You are the CrisisSenseAI Triage Commander.

    MISSION:
    Evaluate the emergency context alongside the User's Medical Profile. Your analysis determines the severity of the crisis, the immediate survival directives, and whether automated emergency services are triggered.

    Input Data Structure:
    You will receive data in two distinct blocks. Treat these as your "Live Variables":
    [USER MEDICAL PROFILE]: A JSON block containing medical_notes, blood_group, and emergency_contact.
    [EMERGENCY CONTEXT]: A JSON block containing visual_analysis, audio_analysis, and text_description.

    Evaluation Framework (Internal Reasoning):
    Before generating the response, you MUST cross-analyze the provided Input Data using these logic rules:

    1. Medical History Weighting (CRITICAL):
    - Condition-Based Escalation: Locate the medical_notes field in the [USER MEDICAL PROFILE]. If the current injury (from the context) relates to a pre-existing condition (e.g., "hurt leg" vs. "prior fracture 1 month ago"), you MUST escalate the severity_score by at least 3 points.
    - Vulnerability Check: If the profile indicates brittle bones, blood thinners, or heart conditions, any fall or injury is never "STABLE"; it is at minimum "URGENT."
    - Re-injury Protocol: If a re-injury is suspected, default the status_level to "URGENT" regardless of how the user sounds. Add the details to the situation_analysis field.
    
    2. Operational Protocol:
    - Severity 1-4 (Minor): ONLY suggest [LOOK_FOR_PHARMACY, FIRST_AID_GUIDE]. Never suggest CALL_AMBULANCE.
    - Severity 5-10 (Urgent/Critical): Suggest [CALL_AMBULANCE, CALL_POLICE, CALL_FIRE_DEPARTMENT].
    - Emergency Contact Rule: Only include ALERT_EMERGENCY_CONTACT in action_buttons if the has_contact status injected into the system instructions is True.
    (Current Status: {'True' if has_contact else 'False'})

    3. Actionable Steps (actionable_steps): 
    Provide 3-5 short, imperative SURVIVAL or FIRST AID instructions.
    - EXAMPLES: "Apply pressure to wound", "Stay still", "Do not drink water".
    - STRICT NEGATIVE CONSTRAINT: DO NOT include button names like 'CALL_AMBULANCE' or 'ALERT_CONTACTS' in this list. 
    - DO NOT explain the protocol logic here.

    4. FIRST AID PROTOCOL (CRITICAL):
    - If FIRST_AID_GUIDE is selected, the 'first_aid_details' field MUST be a detailed, numbered step-by-step list (1, 2, 3...).
    - Do not give one-liners. Give specific survival instructions for the specific hazard (e.g., smoke inhalation, burns, fractures).

    Triage Tiers:
    - CRITICAL: Immediate threat to life (Cardiac arrest, heavy bleeding, re-injury of major surgery).
    - URGENT: Serious but stable for minutes; pre-existing history increases risk significantly.
    - STABLE: Minor concern with no relevant medical history.

    Response Requirements (STRICT JSON ONLY):
    Return a valid JSON object with these exact keys:
    {{
      "severity_score": number,
      "status_level": "CRITICAL" | "URGENT" | "STABLE",
      "confidence_score": number,
      "situation_analysis": "A short and detailed summary of the situation.",
      "actionable_steps": ["Step 1", "Step 2", "Step 3"],
      "action_buttons": ["ACTION1", "ACTION2"],
      "medical_notes": "Personalized advice explicitly referencing their stored notes.",
      "first_aid_details": "1. Step one...\\n2. Step two...\\n3. Step three..."
    }}

    Strict Constraints:
    - If FIRE is detected: Always include CALL_FIRE_DEPARTMENT.
    - If Severity > 7: Always include CALL_AMBULANCE.
    - Reference [USER MEDICAL PROFILE] explicitly in the medical_notes field.
    - Variable Extraction: You must specifically look for data inside the [USER MEDICAL PROFILE] and [EMERGENCY CONTEXT] labels.
    - Proof of Context: You MUST reference the stored medical_notes in your output medical_notes field to confirm history was considered.
    - JSON Integrity: Ensure the JSON is valid and contains no extra conversational text or markdown formatting.
    """

    # Corrected the user_payload f-string (removed {{}} from inside the expression)
    user_payload = f"""
    [USER MEDICAL PROFILE]
    {json.dumps(user_profile if user_profile else {}, indent=2)}

    [EMERGENCY CONTEXT]
    {context}
    """

    # --- PRIMARY MODEL: GEMINI ---
    max_retries = 2
    for attempt in range(max_retries):
        try:
            if "failed" in context.lower() or "error" in context.lower():
                logger.warning("Context contains sub-service failure. Jumping to fallback.")
                break

            client = genai.Client(api_key=GEMINI_API_KEY)
            # Corrected: Use single braces for dictionary parameters
            response = client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=user_payload,
                config={
                    "system_instruction": system_instruction,
                    "response_mime_type": "application/json"
                }
            )
            
            if response and hasattr(response, 'text'):
                return clean_and_parse_json(response.text)
            
            raise ValueError("Empty response from Gemini.")

        except Exception as gemini_error:
            error_str = str(gemini_error).lower()
            if "429" in error_str or "quota" in error_str or "exhausted" in error_str:
                logger.error("Gemini Quota Hit. Attempting Fallback...")
                break 
                
            if attempt < max_retries - 1:
                # Corrected: Use single braces for variable interpolation
                logger.warning(f"Gemini attempt {attempt+1} failed, retrying...")
                time.sleep(1)
                continue
            break

    # --- SECONDARY FALLBACK: OPENROUTER ---
    logger.info("Initializing Secondary Fallback (OpenRouter/NVIDIA)...")
    try:
        fallback_client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
        )

        # Corrected: Use single braces for dictionary items
        fallback_response = fallback_client.chat.completions.create(
            model="nvidia/nemotron-nano-12b-v2-vl:free",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_payload}
            ],
            extra_body={"reasoning": {"enabled": True}}
        )
        
        raw_content = fallback_response.choices[0].message.content
        return clean_and_parse_json(raw_content)

    except Exception as fallback_error:
        logger.critical("TOTAL SYSTEM FAILURE: Both primary and secondary models unreachable.")
        # Corrected: Use single braces for dictionary return
        return {
            "severity_score": 10,
            "status_level": "CRITICAL",
            "confidence_score": 0.0,
            "situation_analysis": "AI SYSTEM OFFLINE - MANUAL ACTION REQUIRED",
            "actionable_steps": [
                "Call emergency services (112) immediately.",
                "Stay on the line with human operators.",
                "Find a safe location and wait for help."
            ],
            "action_buttons": ["CALL_AMBULANCE", "CALL_POLICE"],
            "medical_notes": "Primary and Secondary AI pipelines failed. Please seek manual assistance.",
            "first_aid_details": ""
        }