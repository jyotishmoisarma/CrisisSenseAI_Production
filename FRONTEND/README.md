# Crisis AI Frontend - Getting Started 

Yo! This is how you connect the pretty website to the backend. Let's go! 

## What Files Do What?

### `api.js`
This is basically your messenger between the website and the server. It talks to the backend so you can log in, send pictures, and all that stuff.

**What you can do with it:**
- `CrisisAI.Auth` - Login, register, logout stuff
- `CrisisAI.User` - Get your profile info
- `CrisisAI.Analysis` - Send pictures/audio/text to analyze crisis
- `CrisisAI.Dashboard` - Get alerts and cool stats

### `style.css`
Just makes things look pretty. Nothing to see here! 

## How to Set It Up

1. **Make sure the backend is running** on `http://localhost:8000`
   - Using a different URL? No problem: `window.CrisisAI.setApiUrl('http://your-url:8000')`

2. **Add this line to your HTML** (we already did it, but just so you know):
   ```html
   <script src="frontend/api.js"></script>
   ```
   That's it! Now your HTML can talk to the API.


## How to Use It (Copy-Paste Code)

### Login (Get Into Your Account)
```javascript
CrisisAI.Auth.login('user@example.com', 'password')
  .then(user => {
    console.log('You in! Welcome:', user.name);
  })
  .catch(error => console.log('Oops, login failed:', error.message));
```

### Sign Up (Make a New Account)
```javascript
CrisisAI.Auth.signup(
  'John Doe',           // your name
  'john@example.com',   // your email
  'password123',        // your password
  '+1234567890',        // phone (optional, skip it if you want)
  'Mom'                 // emergency contact (optional)
)
  .then(result => {
    console.log('Account made! Now login.');
  })
  .catch(error => console.log('Nope, signup failed:', error.message));
```

### Send Stuff to Analyze Crisis (Text, Pictures, Audio)
```javascript
const textInput = 'Flooding in downtown area';
const imageFile = document.getElementById('imageInput').files[0];
const audioFile = document.getElementById('audioInput').files[0];

CrisisAI.Analysis.analyze(textInput, imageFile, audioFile)
  .then(result => {
    console.log('Analysis done:', result);
  })
  .catch(error => console.log('Analysis failed:', error.message));
```

### Get Your Profile Info
```javascript
CrisisAI.User.getProfile()
  .then(profile => {
    console.log('Your profile:', profile);
  })
  .catch(error => console.log('Cant get profile:', error.message));
```

### Check If You're Logged In
```javascript
if (CrisisAI.Auth.isLoggedIn()) {
  const user = CrisisAI.Auth.getCurrentUser();
  console.log('Yup, you logged in as:', user.name);
}
```

### Logout (Get Out)
```javascript
CrisisAI.Auth.logout();
console.log('Later!');
```


## Backend Endpoints (Technical Stuff)

Here's what the backend actually does:

### Login/Register Stuff
- **POST** `/signup` - Make a new account
- **POST** `/login` - Log in to your account

### Getting Your Info
- **GET** `/profile/{user_id}` - Gets all your profile stuff

### Analysis
- **POST** `/analyze` - Send us a picture/audio/text and we'll analyze it

## How We Remember You (localStorage)

Your info gets saved in browser memory so you don't have to login every time you refresh:
- `currentUser` - Your name and user ID
- `apiUrl` - Where your backend is running

## HTML Example (How to Use It In Your Website)

```html
<form onsubmit="handleLogin(event)">
  <input type="email" id="email" placeholder="Your email" required>
  <input type="password" id="password" placeholder="Your password" required>
  <button type="submit">Login</button>
</form>

<script>
  function handleLogin(event) {
    event.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    CrisisAI.Auth.login(email, password)
      .then(user => {
        alert('Welcome back, ' + user.name + '!');
        // Do whatever you want here - redirect, show stuff, etc
      })
      .catch(error => {
        alert('Uh oh: ' + error.message);
      });
  }
</script>
```

## Ready-To-Use Functions (Already In main.html)

We set up some quick functions for you:

- `handleLogin(email, password)` - Log in
- `handleSignup(name, email, password, phone, emergencyContact)` - Create account  
- `analyzeInput(text, imageFile, audioFile)` - Send stuff to analyze
- `loadUserProfile()` - Get your profile
- `loadAlerts()` - Get the alerts list
- `handleLogout()` - Log out


## Handling When Things Go Wrong

When something breaks, you get an error message. Here's what they mean:

```javascript
CrisisAI.Auth.login(email, password)
  .then(user => {
    // Yay! It worked!
  })
  .catch(error => {
    // Oops, something went wrong
    console.log(error.message);
  });
```

Common problems:
- `User not found` - That email doesn't exist. Sign up first!
- `Invalid credentials` - Wrong password, buddy
- `Analysis failed` - Something messed up when analyzing. Try again
- Network error - Your backend ain't running. Start it!

## How to Debug When Stuff Breaks

1. **Open DevTools** - Press F12 in your browser
2. **Go to Console tab** - See all the errors
3. **Look at Network tab** - See what requests the website is sending
4. **Check if backend is running** - Go to `http://localhost:8000` in your browser

### Quick Test With Terminal

```bash
# Test if login works
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass"}'
```

If you get back JSON, it's working!

## Let's Get Started

1. **Start your backend:**
   ```bash
   cd backend
   python main.py
   ```

2. **Open your website:**
   - Open `file:///C:/Users/gogoi/CRISIS_AI/main.html` in your browser
   - Or use a local server

3. **Test it out:**
   - Open DevTools (F12)
   - In the Console, try:
   ```javascript
   CrisisAI.Auth.signup('test', 'test@test.com', 'pass')
   ```

4. **Then login:**
   ```javascript
   CrisisAI.Auth.login('test@test.com', 'pass')
   ```

Boom! You're connected!
