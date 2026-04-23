import time
import uuid

# In-memory session store
tracking_sessions = {}

def evaluate_trigger(result: dict, allow_auto: bool) -> str:
    """
    Determines if the system should trigger automatically.
    Logic: Confidence > 0.9 AND Severity >= 8.
    """
    severity = result.get("severity_score", 0)
    confidence = result.get("confidence_score", 0)
    
    if confidence > 0.9 and severity >= 8 and allow_auto:
        return "AUTO"
    return "MANUAL"

def create_sos_session(user_id: str, lat: float, lng: float):
    """
    Initializes a unique emergency tracking session.
    """
    session_id = f"SOS-{uuid.uuid4().hex[:6].upper()}"
    tracking_sessions[session_id] = {
        "user_id": user_id,
        "start_time": time.time(),
        "expires_at": time.time() + 600, # 10 minute expiry
        "last_location": {"lat": lat, "lng": lng},
        "history": [{"lat": lat, "lng": lng, "timestamp": time.time()}],
        "status": "ACTIVE"
    }
    maps_link = f"https://www.google.com/maps?q={lat},{lng}"
    return session_id, maps_link

def update_session_heartbeat(session_id: str, lat: float, lng: float):
    """
    Updates the live location and extends the 10-minute expiry window.
    """
    if session_id in tracking_sessions:
        session = tracking_sessions[session_id]
        
        # Check if already expired
        if time.time() > session["expires_at"]:
            session["status"] = "EXPIRED"
            return False
        
        # Update data
        session["last_location"] = {"lat": lat, "lng": lng}
        session["history"].append({"lat": lat, "lng": lng, "timestamp": time.time()})
        
        # Reset the 10-minute timer from the current moment
        session["expires_at"] = time.time() + 600 
        return True
    return False