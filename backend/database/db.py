from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config.settings import DATABASE_URL

# Conditional Engine Arguments:
# 'check_same_thread' is required for SQLite but causes errors in PostgreSQL (Supabase/Render).
# We check the URL string to decide whether to include it.
if "sqlite" in DATABASE_URL:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # For Supabase/PostgreSQL, we use default connection settings
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()