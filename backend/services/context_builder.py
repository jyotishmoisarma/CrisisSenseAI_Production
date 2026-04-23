import json

def build_context(user, text: str = None, image_desc: str = None, audio_text: str = None):

    user_profile = {}
    attributes_to_check = ['name', 'phone', 'emergency_contact', 'blood_group', 'medical_notes']
    
    for attr in attributes_to_check:
        value = getattr(user, attr, None)
        # We check for None, empty strings, and the string "null"
        if value and str(value).strip() != "" and str(value).lower() != "null":
            user_profile[attr] = value

    # Organizes the evaluations from separate AI modules (Image/Text/Audio)
    inputs_context = {}
    
    # Raw user text input
    if text and text.strip():
        inputs_context["user_text"] = text.strip()
        
    # AI evaluation of the Image and Text together
    if image_desc:
        try:
            inputs_context["visual_and_text_analysis"] = json.loads(image_desc)
        except json.JSONDecodeError:
            # Fallback if AI didn't return perfectly formatted JSON
            inputs_context["visual_and_text_analysis"] = image_desc
            
    # AI evaluation of the Audio
    if audio_text:
        try:
            inputs_context["audio_analysis"] = json.loads(audio_text)
        except json.JSONDecodeError:
            # Fallback if AI didn't return perfectly formatted JSON
            inputs_context["audio_analysis"] = audio_text

    return user_profile, inputs_context