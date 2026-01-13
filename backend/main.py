from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from time import time
import logging
import os

# ------------------------
# Logging setup
# ------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ------------------------
# App setup
# ------------------------
app = FastAPI()

FRONTEND_URL = "https://vercel.com/mikhails-projects-5054cde5/ai-chatbot-frontend"  # CHANGE THIS

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ------------------------
# Rate limiting
# ------------------------
RATE_LIMIT = {}
MAX_REQUESTS = 20
WINDOW_SECONDS = 60

def rate_limit(ip: str):
    now = time()
    requests = RATE_LIMIT.get(ip, [])
    requests = [t for t in requests if now - t < WINDOW_SECONDS]

    if len(requests) >= MAX_REQUESTS:
        logger.warning(f"Rate limit exceeded: {ip}")
        raise HTTPException(status_code=429, detail="Too many requests")

    requests.append(now)
    RATE_LIMIT[ip] = requests

# ------------------------
# Request schema
# ------------------------
class ChatRequest(BaseModel):
    message: str

# ------------------------
# Routes
# ------------------------
@app.get("/")
def healthcheck():
    return {"status": "Backend running"}

@app.post("/chat")
def chat(req: ChatRequest, request: Request):
    rate_limit(request.client.host)
    logger.info("Chat request received")

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a helpful chatbot."},
                {"role": "user", "content": req.message},
            ],
        )

        reply = response.choices[0].message.content
        return {"reply": reply}

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")