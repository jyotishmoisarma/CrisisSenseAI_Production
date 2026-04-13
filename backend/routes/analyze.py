from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from database.db import SessionLocal
from database.crud import get_user_by_id
from services.context_builder import build_context
from services.image_analysis import analyze_image
from services.llm_engine import analyze_with_ai
from services.speach_to_text import convert_audio

import traceback

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
        user = get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        image_desc = "No image provided"
        if image:
            try:
                image_desc = analyze_image(image)
            except Exception as e:
                image_desc = f"Image processing failed: {str(e)}"

        audio_text = None
        if audio:
            try:
                audio_text = convert_audio(audio)
            except Exception as e:
                audio_text = f"Audio processing failed: {str(e)}"

        context = build_context(user, text, image_desc, audio_text)

        ai_output = analyze_with_ai(context)

        # Step 6: Return result
        return {"success": True, "result": ai_output}

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Analysis failed: {str(e)}"
        )
