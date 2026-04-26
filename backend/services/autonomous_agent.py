import json
import logging
import time
#from duckduckgo_search import DDGS
from google import genai
from openai import OpenAI
from config.settings import GEMINI_API_KEY, OPENROUTER_API_KEY

# Configure logging
logger = logging.getLogger("AutonomousAgent")

def find_local_responder(action_name: str, location_name: str):
    """
    Requirement 8 & 9: Autonomous tool.
    Uses DuckDuckGo to find REAL local emergency contacts.
    Primary: Gemini 2.5 Flash Preview
    Fallback: NVIDIA Nemotron (Reasoning Enabled via OpenRouter)
    """
    search_results = []
    try:
        # 1. Scrape live web data for local responders
        with DDGS() as ddgs:
            search_query = f"emergency {action_name} contact phone number and address in {location_name}"
            results = ddgs.text(search_query, max_results=3)
            search_results = [r for r in results]
        
        if not search_results:
            return f"Agent could not find specific local contacts for '{action_name}' in {location_name}."

    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        return f"Autonomous search failed. Please use manual emergency dialing."

    # 2. Analyze results with AI
    agent_prompt = f"""
    ROLE: Autonomous Emergency Dispatcher. 
    SERVICE NEEDED: {action_name}
    LOCATION: {location_name}
    WEB SEARCH DATA: {json.dumps(search_results)}
    
    TASK: Extract the most reliable local contact number and address.
    If no number is found, provide the name of the nearest facility.
    Return a clear, short report for the user.
    """

    # --- TIER 1: GEMINI (With Exponential Backoff) ---
    max_retries = 5
    for attempt in range(max_retries):
        try:
            client = genai.Client(api_key=GEMINI_API_KEY)
            # Using the required preview model for this environment
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=agent_prompt
            )
            if response.text:
                return response.text.strip()
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            logger.warning(f"Gemini agent analysis failed: {str(e)}. Switching to Nemotron fallback...")
            break

    # --- TIER 2: NVIDIA NEMOTRON FALLBACK ---
    try:
        fallback_client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
        )

        fallback_response = fallback_client.chat.completions.create(
            model="nvidia/nemotron-nano-12b-v2-vl:free",
            messages=[{"role": "user", "content": agent_prompt}],
            extra_body={"reasoning": {"enabled": True}} # Enable chain-of-thought for extraction
        )
        
        return fallback_response.choices[0].message.content.strip()

    except Exception as fallback_error:
        logger.error(f"All agent analysis tiers exhausted: {str(fallback_error)}")
        return "Autonomous analysis unavailable. Please proceed with manual emergency contact."