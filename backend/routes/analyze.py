from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import traceback
import json

# Correct imports based on your provided folder structure
from database.db import SessionLocal
from database.crud import get_user_by_id
from services.context_builder import build_context
from services.image_and_text_analysis import analyze_image_and_text
from services.speech_to_text import convert_audio
from services.llm_engine import analyze_with_ai

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/analyze")
async def analyze(
    user_id: str = Form(...),
    text: str | None = Form(None),
    image: UploadFile | None = File(None),
    audio: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    try:
        # 1. Fetch user from database
        user = get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # 2. Analyze Image and Text together (Feature 3)
        image_bytes = await image.read() if image else None
        
        visual_text_desc = None
        if image_bytes or text:
            # This returns a JSON string evaluating the image/text context
            visual_text_desc = analyze_image_and_text(image_bytes, text)

        # 3. Analyze Audio (Feature 2)
        audio_text = None
        if audio:
            audio_bytes = await audio.read()
            audio_text = convert_audio(audio_bytes, mime_type=audio.content_type)

        # 4. Build Filtered Context (Features 4 & 5)
        # build_context strips null values and organizes everything into dictionaries
        user_profile, inputs_context = build_context(
            user=user, 
            text=text, 
            image_desc=visual_text_desc, 
            audio_text=audio_text
        )

        if not inputs_context:
            raise HTTPException(status_code=400, detail="No emergency inputs provided (text, image, or audio required).")

        # 5. Final AI Evaluation (Feature 1)
        # We pass the inputs context as a JSON string to the final brain
        context_json_string = json.dumps(inputs_context, indent=2)
        ai_output = analyze_with_ai(context=context_json_string, user_profile=user_profile)

        return {"success": True, "result": ai_output}

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Analysis pipeline failed: {str(e)}"
        )