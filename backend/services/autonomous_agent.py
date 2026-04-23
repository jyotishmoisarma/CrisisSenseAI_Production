import json
from duckduckgo_search import DDGS
from google import genai
from config.settings import GEMINI_API_KEY

def find_local_responder(action_name: str, location_name: str):
    """
    Requirement 8 & 9: Autonomous tool.
    Uses DuckDuckGo to find REAL local emergency contacts.
    """
    try:
        with DDGS() as ddgs:
            search_query = f"emergency {action_name} contact phone number and address in {location_name}"
            results = [r for r in ddgs.text(search_query, max_results=3)]
        
        # Use AI to analyze the scraped web data
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        agent_prompt = f"""
        You are an Autonomous Emergency Dispatcher. 
        The user needs: {action_name}
        Location: {location_name}
        Web Results: {json.dumps(results)}
        
        TASK: Extract the most reliable contact number and address from the search results.
        If no number is found, give the nearest hospital or station name.
        Return a clear, short report for the user.
        """
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=agent_prompt
        )
        return response.text
    except Exception as e:
        return f"Autonomous search failed: {str(e)}. Please use manual dial."