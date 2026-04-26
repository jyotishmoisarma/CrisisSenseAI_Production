/**
 * CRISIS_AI - FULL FEATURE API HANDLER
 * Features: Auth, Profile, Multi-modal Analysis, SOS Sessions, and Agent Actions.
 */

// 1. DYNAMIC ROUTING
const API_BASE_URL = window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost'
  ? 'http://127.0.0.1:8000'
  : 'https://crisissenseai-backend.onrender.com';

// 2. SESSION STATE
let currentUser = JSON.parse(localStorage.getItem('currentUser')) || null;

const Auth = {
  /**
   * SIGNUP: Handles destructuring and sends default values 
   * to satisfy the Supabase/PostgreSQL schema.
   */
  async signup({ name, email, password, phone }) {
    const response = await fetch(`${API_BASE_URL}/users/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name, email, password, phone,
        emergency_contact: "Not Provided",
        blood_group: "Unknown",
        medical_notes: "None"
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail));
    }
    return await response.json();
  },

  async login(email, password) {
    const response = await fetch(`${API_BASE_URL}/users/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Login failed');
    }

    const data = await response.json();
    currentUser = data;
    localStorage.setItem('currentUser', JSON.stringify(data));
    return data;
  },

  logout() {
    currentUser = null;
    localStorage.removeItem('currentUser');
    location.reload();
  },

  getCurrentUser: () => currentUser,
  isLoggedIn: () => currentUser !== null
};

const User = {
  async getProfile(userId) {
    const response = await fetch(`${API_BASE_URL}/users/profile/${userId}`);
    if (!response.ok) throw new Error("Could not fetch profile data");
    return await response.json();
  },

  async updateProfile(userId, profileData) {
    const response = await fetch(`${API_BASE_URL}/users/profile/${userId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(profileData)
    });
    if (!response.ok) throw new Error("Database storage failed");
    return await response.json();
  }
};

const Analysis = {
  async analyze(text = null, image = null, audio = null) {
    if (!currentUser) throw new Error('Authentication required');
    const formData = new FormData();
    formData.append('user_id', currentUser.user_id || currentUser.id);

    if (text) formData.append('text', text);
    if (image) formData.append('image', image);
    if (audio) formData.append('audio', audio);

    const response = await fetch(`${API_BASE_URL}/analyze`, {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Analysis pipeline failed');
    }
    return await response.json();
  }
};

const SOS = {
  async init(analysisResult, lat, lng) {
    const response = await fetch(`${API_BASE_URL}/sos/init`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: currentUser.user_id || currentUser.id,
        analysis_result: analysisResult,
        lat: lat,
        lng: lng,
        auto_allowed: true
      })
    });
    return await response.json();
  },

  async heartbeat(sessionId, lat, lng) {
    return await fetch(`${API_BASE_URL}/sos/heartbeat/${sessionId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lat, lng })
    });
  },

  async executeAgentAction(action, locationStr) {
    const response = await fetch(`${API_BASE_URL}/sos/execute-agent?action=${encodeURIComponent(action)}&location_str=${encodeURIComponent(locationStr)}`, {
      method: 'POST'
    });
    if (!response.ok) throw new Error("Agent execution failed");
    return await response.json();
  }
};

window.CrisisAI = { Auth, User, Analysis, SOS };