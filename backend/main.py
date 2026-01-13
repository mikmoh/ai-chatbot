import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

# -------------------------
# Environment variables
# -------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set")

# -------------------------
# OpenAI client
# -------------------------
client = OpenAI(api_key=OPENAI_API_KEY)

# -------------------------
# FastAPI app
# -------------------------
app = FastAPI()

FRONTEND_URL = "https://ai-chatbot-frontend-liard.vercel.app"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        FRONTEND_URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Models
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
def chat(req: ChatRequest):
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a helpful, friendly chatbot."},
                {"role": "user", "content": req.message},
            ],
            temperature=0.7,
        )
        return {"reply": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))