# CrisisSenseAI Frontend - Complete Documentation

Welcome! Here's everything you need to know about the frontend structure and how to use it.

---

## 📁 File Organization

### **3 Main Sections:**

#### 🏠 **HOMEPAGE** (`homepage.html`)
- Public landing page with features overview
- Links to login and other sections
- Includes incident ticker and how-it-works guide
- Styles: `homepage.css`

#### 🔐 **AUTH** (`auth.html`)
- Login & Signup forms
- Global incident briefing ticker
- Auto-redirects to dashboard if logged in
- Styles: `auth.css`

#### 📊 **MAIN DASHBOARD** (`index.html` / referred to as `main.html`)
- Crisis incident reporting interface
- Real-time camera + photo + audio capture
- AI analysis & triage
- User profile management
- Styles: `index.css` + `style.css`

---

## 🔌 API Integration

### `api.js` - Your Backend Messenger
This is the glue between frontend and backend. It's loaded by all HTML files.

**What you can do with it:**
- `CrisisAI.Auth` - Login, register, logout
- `CrisisAI.User` - Get/update profile info
- `CrisisAI.Analysis` - Send pictures/audio/text for analysis
- `CrisisAI.SOS` - Emergency response coordination

### API Base URL
- **Local:** `http://127.0.0.1:8000`
- **Production:** `https://crisissenseai-backend.onrender.com`
- Auto-detects based on your hostname

---

## 🚀 Setup & Connection

### 1. **Start Your Backend**
```bash
cd backend
python main.py
```
The API will run on `http://localhost:8000`

### 2. **Open Frontend in Browser**
- Simple way: Double-click `homepage.html` or open in your browser
- Better way: Use a local server (avoids CORS issues)
  ```bash
  # Using Python (any version)
  python -m http.server 8000
  # Then open http://localhost:8000/CrisisSenseAI_Production/FRONTEND/
  ```

### 3. **Test the Connection**
1. Open DevTools (F12)
2. Go to Console tab
3. Try this:
   ```javascript
   CrisisAI.Auth.isLoggedIn()  // Should return false
   ```
   If it works, you're connected!


---

## 📖 Complete API Reference

### **Auth Module** - `CrisisAI.Auth`

#### Login
```javascript
CrisisAI.Auth.login('user@example.com', 'password')
  .then(user => console.log('Welcome!', user.name))
  .catch(error => console.log('Error:', error.message));
```

#### Sign Up
```javascript
CrisisAI.Auth.signup({ 
  name: 'John Doe',
  email: 'john@example.com',
  password: 'password123',
  phone: '+1234567890'
})
  .then(result => console.log('Account created!'))
  .catch(error => console.log('Error:', error.message));
```

#### Check Login Status
```javascript
if (CrisisAI.Auth.isLoggedIn()) {
  const user = CrisisAI.Auth.getCurrentUser();
  console.log('Logged in as:', user.name);
}
```

#### Logout
```javascript
CrisisAI.Auth.logout();  // Clears session and reloads page
```

---

### **User Profile Module** - `CrisisAI.User`

#### Get Profile
```javascript
const userId = CrisisAI.Auth.getCurrentUser().user_id;
CrisisAI.User.getProfile(userId)
  .then(profile => {
    console.log('Blood Group:', profile.blood_group);
    console.log('Emergency Contact:', profile.emergency_contact);
  })
  .catch(error => console.log('Error:', error.message));
```

#### Update Profile
```javascript
const userId = CrisisAI.Auth.getCurrentUser().user_id;
CrisisAI.User.updateProfile(userId, {
  emergency_contact: 'Mom +1234567890',
  blood_group: 'O+',
  medical_notes: 'Allergic to penicillin'
})
  .then(result => console.log('Profile updated!'))
  .catch(error => console.log('Error:', error.message));
```

---

### **Analysis Module** - `CrisisAI.Analysis`

#### Analyze Crisis (Text, Image, Audio)
```javascript
const text = 'Flooding in downtown area';
const imageFile = document.getElementById('imageInput').files[0];
const audioFile = document.getElementById('audioInput').files[0];

CrisisAI.Analysis.analyze(text, imageFile, audioFile)
  .then(response => {
    const result = response.result;
    console.log('Severity:', result.status_level);  // CRITICAL/URGENT/STABLE
    console.log('Summary:', result.situation_analysis);
    console.log('Steps:', result.actionable_steps);
    console.log('Actions:', result.action_buttons);
  })
  .catch(error => console.log('Error:', error.message));
```

---

### **Emergency Response Module** - `CrisisAI.SOS`

#### Initialize Emergency Session
```javascript
const analysisResult = { /* from Analysis.analyze() */ };
const lat = 40.7128;  // New York
const lng = -74.0060;

CrisisAI.SOS.init(analysisResult, lat, lng)
  .then(sos => console.log('SOS initialized:', sos))
  .catch(error => console.log('Error:', error.message));
```

#### Execute Emergency Action
```javascript
CrisisAI.SOS.executeAgentAction('CALL_AMBULANCE', 'Downtown, Main St')
  .then(result => console.log('Action executed:', result))
  .catch(error => console.log('Error:', error.message));
```

---

## 🛠️ Backend Endpoints Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/users/signup` | POST | Create new account |
| `/users/login` | POST | Log in to account |
| `/users/profile/{user_id}` | GET | Fetch user profile |
| `/users/profile/{user_id}` | PUT | Update user profile |
| `/analyze` | POST | Analyze crisis (text/image/audio) |
| `/sos/init` | POST | Initialize SOS session |
| `/sos/heartbeat/{session_id}` | POST | Send location update |
| `/sos/execute-agent` | POST | Execute emergency action |

---

## 💾 Browser Storage

Your session is saved in `localStorage`:
- **`currentUser`** - Logged-in user data (JSON)
- Used to persist login across page refreshes
- Cleared on logout

---

## 🎯 Common Issues & Solutions

| Problem | Solution |
|---------|----------|
| "Network error" | Start backend: `python main.py` |
| "User not found" | Sign up first, then login |
| "Invalid credentials" | Check email/password spelling |
| CORS errors | Use local server instead of file:// |
| Camera not working | Check browser permissions |
| Images not uploading | Check file size (max 5 images) |

---

## 📝 User Journey

```
START
  ↓
[homepage.html] - Landing page
  ↓
  User clicks "Login"
  ↓
[auth.html] - Login/Signup
  ├─ New user? → Sign up
  └─ Existing? → Login
  ↓
[index.html] - Main Dashboard
  ├─ Report incident (photos, audio, text)
  ├─ AI analysis
  ├─ View results
  ├─ Manage profile ("My Profile")
  └─ Logout
  ↓
Back to [auth.html]
```

---

## ✨ Key Features by Page

### Homepage (`homepage.html`)
- Landing page with features overview
- Real-time global incident ticker
- "How it works" guide
- Links to login and features

### Auth Page (`auth.html`)
- Flip-card login/signup forms
- Global incident briefing sidebar
- Category filters
- Auto-redirect if logged in

### Main Dashboard (`index.html`)
- **Reporting Section:**
  - Live camera feed
  - Photo capture & upload (max 5)
  - Text description
  - Audio recording
- **Analysis Results:**
  - Severity classification
  - Situation summary
  - Actionable steps
  - Manual/Auto action buttons
- **Profile Management:**
  - View/edit personal info
  - Emergency contact
  - Blood group
  - Medical notes

---

## 🚀 Quick Start Commands

```bash
# Start backend
cd backend
python main.py

# Serve frontend locally (from root directory)
python -m http.server 8000

# Then open in browser
# http://localhost:8000/CrisisSenseAI_Production/FRONTEND/homepage.html
```

---

## 📚 For More Details

See **`FRONTEND_STRUCTURE.md`** for complete file organization and detailed linking map.
