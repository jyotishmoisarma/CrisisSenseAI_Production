
const API_BASE_URL = localStorage.getItem('apiUrl') || 'http://localhost:8000';

// user session
let currentUser = JSON.parse(localStorage.getItem('currentUser')) || null;


const Auth = {
  async signup(name, email, password, phone = '', emergencyContact = '') {
    try {
      const response = await fetch(`${API_BASE_URL}/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name,
          email,
          password,
          phone,
          emergency_contact: emergencyContact
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Signup failed');
      }

      return await response.json();
    } catch (error) {
      console.error('Signup error:', error);
      throw error;
    }
  },

  async login(email, password) {
    try {
      const response = await fetch(`${API_BASE_URL}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Login failed');
      }

      const data = await response.json();
      currentUser = data;
      localStorage.setItem('currentUser', JSON.stringify(data));
      return data;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  },

  async logout() {
    currentUser = null;
    localStorage.removeItem('currentUser');
  },

  getCurrentUser() {
    return currentUser;
  },

  isLoggedIn() {
    return currentUser !== null;
  }
};


const User = {
  async getProfile(userId = null) {
    const id = userId || currentUser?.user_id;
    if (!id) throw new Error('No user logged in');

    try {
      const response = await fetch(`${API_BASE_URL}/profile/${id}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to fetch profile');
      }

      return await response.json();
    } catch (error) {
      console.error('Profile fetch error:', error);
      throw error;
    }
  }
};


const Analysis = {
  async analyze(text = null, image = null, audio = null) {
    if (!currentUser) throw new Error('User not logged in');
    if (!text && !image && !audio) throw new Error('At least one input is required');

    try {
      const formData = new FormData();
      formData.append('user_id', currentUser.user_id);
      
      if (text) formData.append('text', text);
      if (image) formData.append('image', image);
      if (audio) formData.append('audio', audio);

      const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Analysis failed');
      }

      return await response.json();
    } catch (error) {
      console.error('Analysis error:', error);
      throw error;
    }
  }
};


const Dashboard = {
  
  async getAlerts() {
    return {
      alerts: [
        {
          id: 1,
          title: 'Urban Flooding Risk - Sector 7',
          severity: 'high',
          status: 'open',
          timestamp: 'now'
        },
        {
          id: 2,
          title: 'Road Accident Cluster - NH Corridor',
          severity: 'medium',
          status: 'investigating',
          timestamp: '14 min ago'
        },
        {
          id: 3,
          title: 'Power Outage - Emergency Ward Grid',
          severity: 'low',
          status: 'resolved',
          timestamp: '31 min ago'
        }
      ]
    };
  },
  async getStats() {
    return {
      activeAlerts: 12,
      resolvedCases: 148,
      aiConfidence: 97.8,
      responseTime: '02:14'
    };
  }
};


function setApiUrl(url) {
  localStorage.setItem('apiUrl', url);
  location.reload();
}

window.CrisisAI = {
  Auth,
  User,
  Analysis,
  Dashboard,
  setApiUrl,
  API_BASE_URL
};
