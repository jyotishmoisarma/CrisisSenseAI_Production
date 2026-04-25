import os
from dotenv import find_dotenv, load_dotenv

# Load the .env file if it exists
load_dotenv(find_dotenv())

# 1. Fetch the URL from environment (Render/Supabase) or fallback to local
RAW_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./users.db")

# 2. THE POSTGRES FIX: 
# SQLAlchemy 1.4+ requires 'postgresql://' but many platforms (Supabase/Render) 
# provide 'postgres://'. We fix it here so the rest of the app doesn't crash.
if RAW_DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = RAW_DATABASE_URL.replace("postgres://", "postgresql://", 1)
else:
    DATABASE_URL = RAW_DATABASE_URL

# 3. API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")