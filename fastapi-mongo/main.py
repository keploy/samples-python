# app/main.py
from fastapi import FastAPI
from quizzly.routes import parent, quiz, content
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
from quizzly.routes import parent, quiz
from quizzly.core.config import settings


app = FastAPI()
# Read and parse CORS origins
origins_str = settings.CORS_ORIGINS
origins = [origin.strip() for origin in origins_str.split(",") if origin.strip()]

print(origins)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(parent.router, prefix="/parent", tags=["Parent"])
app.include_router(quiz.router, prefix="/quiz", tags=["Quiz"])
app.include_router(content.router, prefix="/content", tags=["Content"])
