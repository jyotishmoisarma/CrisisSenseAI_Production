import asyncio
import json
import traceback
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

# Database and CRUD imports
from database.db import SessionLocal
from database.crud import get_user_by_id

# Service imports
from services.context_builder import build_context
from services.image_and_text_analysis import analyze_image_and_text
from services.speech_to_text import convert_audio
from services.llm_engine import analyze_with_ai

router = APIRouter()

# Thread pool for running synchronous AI functions without blocking
executor = ThreadPoolExecutor(max_workers=5)

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
    """
    Optimized Pipeline: 
    1. Parallel execution of Vision and Audio pre-processors.
    2. Uses stable model references to prevent 404 errors.
    3. Handles fallback 'result' object for frontend stability.
    """
    try:
        # 1. Fetch user profile
        user = get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        loop = asyncio.get_event_loop()
        
        # Helper to run synchronous AI calls in threads concurrently
        async def run_sync(func, *args):
            return await loop.run_in_executor(executor, func, *args)

        # 2. Prepare parallel tasks
        tasks = []
        visual_text_desc = None
        audio_text = None

        # Process image if provided
        if image:
            image_bytes = await image.read()
            tasks.append(run_sync(analyze_image_and_text, image_bytes, text))
        
        # Process audio if provided
        if audio:
            audio_bytes = await audio.read()
            tasks.append(run_sync(convert_audio, audio_bytes, audio.content_type))

        # 3. Execute tasks simultaneously
        if tasks:
            results = await asyncio.gather(*tasks)
            
            # Map results back based on order of task addition
            current_idx = 0
            if image:
                visual_text_desc = results[current_idx]
                current_idx += 1
            if audio:
                audio_text = results[current_idx]

        # 4. Build consolidated context
        user_profile, inputs_context = build_context(
            user=user,
            text=text,
            image_desc=visual_text_desc, 
            audio_text=audio_text
        )

        if not inputs_context and not text:
            raise HTTPException(status_code=400, detail="No emergency data provided.")

        # 5. Final AI Commander triage
        context_json = json.dumps(inputs_context, indent=2)
        ai_output = analyze_with_ai(context=context_json, user_profile=user_profile)

        return {"success": True, "result": ai_output}

    except Exception as e:
        traceback.print_exc()
        # Fallback 'result' object ensures the frontend doesn't crash on 'status_level'
        return {
            "success": False, 
            "error": str(e),
            "result": {
                "severity_score": 5,
                "status_level": "STABLE",
                "confidence_score": 0.0,
                "situation_analysis": "System processing error. Analyzing manually...",
                "actionable_steps": ["Ensure your safety.", "Stay calm.", "Wait for a manual response."],
                "action_buttons": ["CALL_AMBULANCE"],
                "medical_notes": f"Pipeline Error: {str(e)}"
            }
        }