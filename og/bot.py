import json

def handler(event, context):
    """
    Minimal Nifty Island bot:
    - replies "gm" if user says "gm"
    - replies "I just say 'gm'" for anything else
    """
    # Get text from request body
    body = json.loads(event.get("body", "{}"))
    text = body.get("text", "").strip()

    # Determine response
    if text.lower() == "gm":
        reply = "gm"
    else:
        reply = "I just say 'gm'"

    # Return response in the Nifty Island format
    response = [{
        "text": reply,
        "action": "CHAT",
        "actionContext": None
    }]

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(response)
    }
