import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

# -------------------------
# Load environment variables
# -------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in environment variables!")

# -------------------------
# Initialize OpenAI client
# -------------------------
client = OpenAI(api_key=OPENAI_API_KEY)

# -------------------------
# FastAPI setup
# -------------------------
app = FastAPI()

# Replace this with your actual Vercel frontend URL
FRONTEND_URL = "https://ai-chatbot-frontend-liard.vercel.app/"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # for local dev
        FRONTEND_URL              # for deployed frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Data model
# -------------------------
class ChatRequest(BaseModel):
    message: str

# -------------------------
# Health check
# -------------------------
@app.get("/")
def root():
    return {"status": "backend running"}

# -------------------------
# Chat endpoint
# -------------------------
@app.post("/chat")
def chat(request: ChatRequest):
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",  # change model if needed
            messages=[
                {"role": "system", "content": "You are a helpful, friendly chatbot."},
                {"role": "user", "content": request.message}
            ],
            temperature=0.7,
        )
        answer = response.choices[0].message.content
        return {"reply": answer}
    except Exception as e:
        # Catch all errors and return JSON-friendly message
        raise HTTPException(status_code=500, detail=str(e))