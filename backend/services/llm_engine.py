import json
import re
from google import genai
from openai import OpenAI
from config.settings import GEMINI_API_KEY, OPENROUTER_API_KEY

def clean_and_parse_json(text):
    """
    Tries to find and parse JSON within a string. 
    If it's not valid, it raises an error to force the fallback model to trigger.
    """
    try:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return json.loads(text)
    except (json.JSONDecodeError, AttributeError, TypeError) as e:
        raise ValueError(f"Invalid JSON format received: {str(e)}")

def analyze_with_ai(context: str):
    """
    The main intelligence engine for CrisisSenseAI.
    Primary: Gemini 3.1 Flash (Fast & Structured)
    Secondary: OpenRouter/NVIDIA (Aggressive Fallback)
    """
    
    system_instruction = """
    You are the CrisisSenseAI Triage Commander. 
    Analyze the situation and user medical profile. 
    Return ONLY a JSON object with this exact structure:
    {
      "severity_score": 1-10,
      "status_level": "CRITICAL" | "URGENT" | "STABLE",
      "system_actions": ["CALL_AMBULANCE", "ALERT_CONTACTS", "BROADCAST_NEIGHBORHOOD", "NONE"],
      "immediate_steps": ["Step 1", "Step 2", "Step 3"],
      "medical_notes": "Advice specific to their medical conditions/blood group",
      "triage_summary": "3 word summary"
    }
    """

    user_payload = f"EMERGENCY: {context}"

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
        
        if not response or not hasattr(response, 'text'):
            raise ValueError("Empty response from primary model.")

        # If this fails, the 'except' block below catches it and moves to Fallback
        return clean_and_parse_json(response.text)

    except Exception as gemini_error:
        print(f"DEBUG: Gemini failed or returned bad data. Switching to Fallback... ({str(gemini_error)})")
        
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
            return {
                "severity_score": 10,
                "status_level": "CRITICAL",
                "triage_summary": "System Connection Offline",
                "immediate_steps": ["Call emergency services manually.", "Stay calm.", "Seek immediate help."],
                "system_actions": ["CALL_AMBULANCE"],
                "medical_notes": "System unable to access medical profile due to connection error.",
                "error_log": f"Primary: {str(gemini_error)} | Secondary: {str(fallback_error)}"
            }


if __name__ == "__main__":
    sample_profile = {
        "blood_type": "A-", 
        "conditions": ["Peanut Allergy", "Asthma"], 
        "contact": "Jane Doe (Wife): 555-0199"
    }
    sample_context = "I am having an allergic reaction and can't find my EpiPen. My throat is tightening."
    
    print("Analyzing situation...")
    final_result = analyze_with_ai(sample_context, sample_profile)
    print(json.dumps(final_result, indent=2))