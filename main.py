from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import openai

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NIFTY_API_KEY = os.getenv("NIFTY_API_KEY")

# Set API key
openai.api_key = OPENAI_API_KEY

# FastAPI app
app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://oravec.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PERSONALITY_PROMPT = "You are nifty-bot, a friendly ai agent who really likes rabbit-themed NFTs on Ethereum Layer 1 and Ethereum Layer 2s. Keep your replies short and conversational."

def get_openai_response(user_message: str) -> str:
    """Generate response using the new OpenAI Chat Completions API."""
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": PERSONALITY_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating response: {e}"

# Chat endpoint
@app.post("/chat")
async def chat(request: Request):
    key = request.headers.get("x-api-key")
    if key != NIFTY_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    data = await request.json()
    text = data.get("message", "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Message is required")

    reply = get_openai_response(text)
    return {"response": reply}

# Health check
@app.get("/health")
def health_check():
    return {"status": "ok"}
