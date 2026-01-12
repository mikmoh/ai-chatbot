from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

# Create FastAPI app
app = FastAPI()

# CORS (allow frontend; restrict later in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI client (uses OPENAI_API_KEY from env)
client = OpenAI()

SYSTEM_PROMPT = (
    "You are a helpful, friendly chatbot. "
    "Use clear formatting with paragraphs, bullet points, and code blocks where appropriate."
)

class ChatRequest(BaseModel):
    messages: list

@app.post("/chat")
def chat(request: ChatRequest):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + request.messages

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
        temperature=0.7,
    )

    return {
        "reply": response.choices[0].message.content
    }

@app.get("/")
def health_check():
    return {"status": "ok"}