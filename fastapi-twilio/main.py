from fastapi import FastAPI
import requests
from dotenv import load_dotenv
from pydantic import BaseModel
import os


load_dotenv()


class Message(BaseModel):
    Body: str
    To: str

app = FastAPI()


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
    
    try:
        response = requests.post(url=url, data=payload, auth=(twilio_account_sid, twilio_auth_token))
        if response.status_code == 201:
            return {"message": "SMS sent successfully!"}
        else:
            return {"message": "Failed to send SMS. Please check the provided phone number."}
    except Exception as e:
        return {"message": str(e)}
