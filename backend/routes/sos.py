from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

# Import the exactly named functions from the logic service
from services.sos_logic import (
    evaluate_trigger, 
    create_sos_session, 
    update_session_heartbeat, 
    tracking_sessions
)
from services.autonomous_agent import find_local_responder

router = APIRouter(prefix="/sos", tags=["SOS Orchestration"])

class SOSInitRequest(BaseModel):
    user_id: str
    analysis_result: dict
    lat: float
    lng: float
    auto_allowed: bool = True

class HeartbeatRequest(BaseModel):
    lat: float
    lng: float

@router.post("/init")
async def initialize_sos(req: SOSInitRequest):
    # 1. Decide mode
    mode = evaluate_trigger(req.analysis_result, req.auto_allowed)
    
    # 2. Create session
    session_id, maps_link = create_sos_session(req.user_id, req.lat, req.lng)
    
    return {
        "session_id": session_id,
        "mode": mode,
        "maps_link": maps_link
    }

@router.post("/heartbeat/{session_id}")
async def location_update(session_id: str, req: HeartbeatRequest):
    """Updates live tracking. Uses the synchronized function name."""
    success = update_session_heartbeat(session_id, req.lat, req.lng)
    if not success:
        raise HTTPException(status_code=410, detail="Session expired or inactive")
    return {"status": "synced"}

@router.get("/live/{session_id}")
async def get_live_data(session_id: str):
    if session_id not in tracking_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return tracking_sessions[session_id]

@router.post("/execute-agent")
async def trigger_ai_agent(action: str, location_str: str):
    """
    Updated to return both a text summary AND a clean dialable number.
    """
    report = find_local_responder(action, location_str)
    
    # Simple regex to extract the first phone number found in the AI report
    import re
    phone_match = re.search(r'\+?\d[\d -]{7,12}\d', report)
    clean_number = phone_match.group(0) if phone_match else "112"

    return {
        "agent_report": report,
        "phone_number": clean_number
    }