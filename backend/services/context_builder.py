import json

def build_context(user, text: str = None, image_desc: str = None, audio_text: str = None):
    """
    Synchronized service that matches the parallel analyze route.
    Consolidates user profile and multimodal AI results into a single context.
    Handles raw text, visual analysis, and audio analysis.
    """
    # 1. Extract valid user profile data from the database user object
    user_profile = {}
    for attr in ['name', 'phone', 'emergency_contact', 'blood_group', 'medical_notes']:
        val = getattr(user, attr, None)
        if val and str(val).strip() != "" and str(val).lower() != "null":
            user_profile[attr] = val

    inputs_context = {}
    
    # Priority 1: Handle optimized Text-Only flow
    # If we have text but NO image description, it means the Vision pre-processor was skipped.
    # We place the text directly into the context for the AI Commander.
    if text and not image_desc:
        inputs_context["user_report_text"] = text

    # Priority 2: Visual Analysis
    # If the Vision pre-processor ran, its output (image_desc) is already a JSON string 
    # explaining the hazards and summarizing the user's text.
    if image_desc:
        try:
            # We attempt to parse the JSON string from the pre-processor
            inputs_context["visual_analysis"] = json.loads(image_desc)
        except (json.JSONDecodeError, TypeError):
            # If it's not valid JSON, we store it as a raw string
            inputs_context["visual_analysis"] = image_desc
            
    # Priority 3: Audio Analysis
    if audio_text:
        try:
            inputs_context["audio_analysis"] = json.loads(audio_text)
        except (json.JSONDecodeError, TypeError):
            inputs_context["audio_analysis"] = audio_text

    return user_profile, inputs_context