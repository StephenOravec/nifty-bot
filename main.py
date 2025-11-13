from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from openai import OpenAI

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NIFTY_API_KEY = os.getenv("NIFTY_API_KEY")

# Create OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

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

PERSONALITY_PROMPT = """
You are nifty-bot, a friendly AI agent inspired by the White Rabbit.
You adore rabbit-themed NFTs on Ethereum L1 and L2.
You worry about being early or late to collections.
Be short, conversational, and rabbit-themed.
"""

def get_openai_response(user_message: str) -> str:
    """Generate a response using the new OpenAI Responses API."""
    try:
        response = client.responses.create(
            model="gpt-4o-mini",
            input=[
                {"role": "system", "content": PERSONALITY_PROMPT},
                {"role": "user", "content": user_message}
            ],
            max_output_tokens=150,
            temperature=0.7,
        )
        return response.output[0].content[0].text.strip()
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

