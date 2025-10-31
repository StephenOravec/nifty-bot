# interactive_bot.py
import json
from api import bot

print("Nifty Island Echo Bot (type 'quit' to exit)")

while True:
    user_input = input("You: ").strip()
    if user_input.lower() == "quit":
        break

    # Simulate Nifty Island event
    fake_event = {"body": json.dumps({"text": user_input})}
    response = bot.handler(fake_event, None)

    # Parse the JSON response to get the text
    bot_reply = json.loads(response["body"])[0]["text"]
    print("Bot:", bot_reply)
