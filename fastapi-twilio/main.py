from fastapi import FastAPI, Request
from fastapi.responses import Response
from urllib.parse import quote
import requests
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()
app = FastAPI()

class Message(BaseModel):
    Body: str
    To: str

@app.post('/send-sms/')
def send_sms(data: Message):
    twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    twilio_phone_number = os.getenv('TWILIO_NUMBER')
    url = f'https://api.twilio.com/2010-04-01/Accounts/{twilio_account_sid}/Messages.json'
    payload = {
        'Body': data.Body,
        'From': twilio_phone_number,
        'To': data.To
    }
    response = requests.post(url=url, data=payload, auth=(twilio_account_sid, twilio_auth_token))
    if response.status_code == 201:
        return {"message": "SMS sent successfully!"}
    return {"message": "Failed to send SMS.", "details": response.text}

@app.post("/make-call/")
def make_call(data: Message):
    # Get Twilio credentials and your Twilio number from environment variables
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    twilio_number = os.getenv('TWILIO_NUMBER')

    # Get your public ngrok URL from environment variables (should be set manually)
    ngrok_url = os.getenv('NGROK_URL')

    # Create a voice URL with the message as a query param (Twilio will fetch this)
    voice_url = f"{ngrok_url}/voice?message={quote(data.Body)}"

    # Twilio's API endpoint to initiate a voice call
    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Calls.json"

    # Set up the details of the call: who to call, from which number, and what to say
    payload = {
        'To': data.To,             # The number to call
        'From': twilio_number,     # Your Twilio number
        'Url': voice_url           # Twilio fetches this to know what to speak
    }

    # Make a POST request to Twilio to start the call
    response = requests.post(url, data=payload, auth=(account_sid, auth_token))

    # Check if the call was successfully created
    if response.status_code == 201:
        return {"message": "Call initiated successfully!"}
    return {"message": "Failed to make the call.", "details": response.text}


@app.api_route("/voice", methods=["GET", "POST"])
async def voice(request: Request):
    # Extract the 'message' query parameter from the URL, or use a default
    message = request.query_params.get("message", "Hello from Twilio!")

    # Print the message to the console for debugging/logging
    print(f"📞 Twilio is trying to say: {message}")

    # Respond with TwiML (Twilio Markup Language) to tell Twilio what to speak
    response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>{message}</Say>
</Response>"""

    
    return Response(content=response, media_type="application/xml")


# Graceful shutdown
@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down gracefully...")
    
    # Perform any additional cleanup here if needed
    # For example, closing database connections or other resources