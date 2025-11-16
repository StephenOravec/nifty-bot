from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from openai import OpenAI
from google.cloud import firestore

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Initialize Firestore client
db = firestore.Client()

# FastAPI app
app = FastAPI()

# CORS for production front-end domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://oravec.io"],  # production front-end
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

# ----------------------
# Helper Functions
# ----------------------

def get_openai_response(user_message: str, memory_messages: list) -> str:
    """Call OpenAI with memory context."""

    try:
        # Convert memory into OpenAI format
        formatted_memory = []
        for m in memory_messages:
            formatted_memory.append({
                "role": m["role"],
                "content": m["text"]  # convert Firestore 'text' → OpenAI 'content'
            })

        messages = [{"role": "system", "content": PERSONALITY_PROMPT}]
        messages.extend(formatted_memory)
        messages.append({"role": "user", "content": user_message})

        response = client.responses.create(
            model="gpt-4o-mini",
            input=messages,
            max_output_tokens=150,
        )

        return response.output[0].content[0].text.strip()

    except Exception as e:
        return f"Error generating response: {e}"

def get_memory(user_id: str, limit: int = 20):
    """Retrieve last `limit` messages from Firestore for this user."""
    doc_ref = db.collection("sessions").document(user_id)
    doc = doc_ref.get()
    if doc.exists:
        messages = doc.to_dict().get("messages", [])
        return messages[-limit:]  # last N messages
    return []

def save_message(user_id: str, role: str, text: str):
    """Append message to Firestore memory."""
    doc_ref = db.collection("sessions").document(user_id)
    doc_ref.set(
        {
            "messages": firestore.ArrayUnion([{"role": role, "text": text}])
        },
        merge=True
    )

# ----------------------
# Endpoints
# ----------------------

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    message = data.get("message", "").strip()

    if not user_id or not message:
        raise HTTPException(status_code=400, detail="user_id and message required")

    # Retrieve last 20 messages for context
    memory = get_memory(user_id)

    # Generate response
    reply = get_openai_response(message, memory)

    # Save user and assistant messages
    save_message(user_id, "user", message)
    save_message(user_id, "assistant", reply)

    return {"response": reply}

@app.get("/health")
def health_check():
    return {"status": "ok"}


