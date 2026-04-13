def build_context(user, text, image_desc, audio_text=None):
    return f"""
User Info:
Name: {user.name}
Medical: {user.medical_notes}

User Input: {text}

Audio: {audio_text}

Image: {image_desc}

"""