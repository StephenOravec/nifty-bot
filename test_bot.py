# test_bot.py
import json
from api import bot

# Simulate a request from Nifty Island
fake_event_gm = {"body": json.dumps({"text": "gm"})}
fake_event_hello = {"body": json.dumps({"text": "hello"})}

# Test "gm"
result = bot.handler(fake_event_gm, None)
print("Test 'gm':", result["body"])

# Test "hello"
result = bot.handler(fake_event_hello, None)
print("Test 'hello':", result["body"])
