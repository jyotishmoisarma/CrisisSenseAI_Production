from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from database.db import engine
from models.user_model import Base
from routes import user, analyze, sos

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    # Add both the Live Server port and the React port just in case
    allow_origins=[
        "http://127.0.0.1:5500", 
        "http://localhost:5500",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(analyze.router)
app.include_router(sos.router) # Add this line