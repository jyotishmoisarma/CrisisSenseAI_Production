/**
 * CRISIS_AI - PRODUCTION READY API HANDLER
 */

// ============================
// 1. BASE URL
// ============================
const API_BASE_URL =
  window.location.hostname === "127.0.0.1" ||
  window.location.hostname === "localhost"
    ? "http://127.0.0.1:8000"
    : "https://crisissenseai-backend.onrender.com";

// ============================
// 2. SESSION STATE
// ============================
let currentUser = JSON.parse(localStorage.getItem("currentUser")) || null;

// Normalize user object
if (currentUser) {
  currentUser = {
    ...currentUser,
    id: currentUser.user_id || currentUser.id,
  };
}

// ============================
// 3. HELPERS
// ============================

const JSON_HEADERS = {
  "Content-Type": "application/json",
};

function createTimeoutSignal(timeout = 10000) {
  const controller = new AbortController();
  setTimeout(() => controller.abort(), timeout);
  return controller.signal;
}

async function handleResponse(response) {
  const data = await response.json();

  if (!response.ok) {
    let message = "Something went wrong";

    if (Array.isArray(data.detail)) {
      const err = data.detail[0];

      if (err.loc?.includes("phone")) {
        message = "Enter a valid phone number (e.g. 919876543210)";
      } else {
        message = err.msg || message;
      }
    } else if (typeof data.detail === "string") {
      message = data.detail;
    }

    throw new Error(message);
  }

  return data;
}

// ============================
// 4. AUTH
// ============================

const Auth = {
  async signup({ name, email, password, phone }) {
    const response = await fetch(`${API_BASE_URL}/users/signup`, {
      method: "POST",
      headers: JSON_HEADERS,
      signal: createTimeoutSignal(),
      body: JSON.stringify({
        name,
        email,
        password,
        phone,
        emergency_contact: "Not Provided",
        blood_group: "Unknown",
        medical_notes: "None",
      }),
    });

    return await handleResponse(response);
  },

  async login(email, password) {
    const response = await fetch(`${API_BASE_URL}/users/login`, {
      method: "POST",
      headers: JSON_HEADERS,
      signal: createTimeoutSignal(),
      body: JSON.stringify({ email, password }),
    });

    const data = await handleResponse(response);

    currentUser = {
      ...data,
      id: data.user_id || data.id,
    };

    localStorage.setItem("currentUser", JSON.stringify(currentUser));

    return currentUser;
  },

  logout() {
    currentUser = null;
    localStorage.removeItem("currentUser");
    location.reload();
  },

  getCurrentUser: () => currentUser,
  isLoggedIn: () => currentUser !== null,
};

// ============================
// 5. USER
// ============================

const User = {
  async getProfile(userId) {
    const response = await fetch(
      `${API_BASE_URL}/users/profile/${userId}`,
      { signal: createTimeoutSignal() }
    );

    return await handleResponse(response);
  },

  async updateProfile(userId, profileData) {
    const response = await fetch(
      `${API_BASE_URL}/users/profile/${userId}`,
      {
        method: "PUT",
        headers: JSON_HEADERS,
        signal: createTimeoutSignal(),
        body: JSON.stringify(profileData),
      }
    );

    return await handleResponse(response);
  },
};

// ============================
// 6. ANALYSIS (GUEST ENABLED)
// ============================

const Analysis = {
  async analyze(text = null, image = null, audio = null) {
    const formData = new FormData();

    if (currentUser) {
      formData.append("user_id", currentUser.id);
    } else {
      formData.append("guest", true);
    }

    if (text) formData.append("text", text);
    if (image) formData.append("image", image);
    if (audio) formData.append("audio", audio);

    const response = await fetch(`${API_BASE_URL}/analyze`, {
      method: "POST",
      signal: createTimeoutSignal(15000),
      body: formData,
    });

    return await handleResponse(response);
  },
};

// ============================
// 7. SOS (AUTH REQUIRED)
// ============================

const SOS = {
  async init(analysisResult, lat, lng) {
    if (!currentUser) throw new Error("Login required for SOS");

    const response = await fetch(`${API_BASE_URL}/sos/init`, {
      method: "POST",
      headers: JSON_HEADERS,
      signal: createTimeoutSignal(),
      body: JSON.stringify({
        user_id: currentUser.id,
        analysis_result: analysisResult,
        lat,
        lng,
        auto_allowed: true,
      }),
    });

    return await handleResponse(response);
  },

  async heartbeat(sessionId, lat, lng) {
    if (!currentUser) throw new Error("Login required");

    const response = await fetch(
      `${API_BASE_URL}/sos/heartbeat/${sessionId}`,
      {
        method: "POST",
        headers: JSON_HEADERS,
        signal: createTimeoutSignal(),
        body: JSON.stringify({ lat, lng }),
      }
    );

    return await handleResponse(response);
  },

  async executeAgentAction(action, locationStr) {
    if (!currentUser) throw new Error("Login required");

    const response = await fetch(
      `${API_BASE_URL}/sos/execute-agent?action=${encodeURIComponent(
        action
      )}&location_str=${encodeURIComponent(locationStr)}`,
      {
        method: "POST",
        signal: createTimeoutSignal(),
      }
    );

    return await handleResponse(response);
  },
};

// ============================
// 8. EXPORT
// ============================

window.CrisisAI = {
  Auth,
  User,
  Analysis,
  SOS,
};