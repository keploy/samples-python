from fastapi import FastAPI, Form, Response
from contextlib import asynccontextmanager
import logging
import os
import httpx
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from twilio.twiml.messaging_response import MessagingResponse
from fastapi.responses import JSONResponse

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)


# Pydantic model for request validation
class Message(BaseModel):
    Body: str = Field(..., min_length=1, max_length=160)
    To: str = Field(..., pattern=r"^\+\d{10,15}$")





# Lifespan handler (replaces @app.on_event("startup"))
@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Starting FastAPI app...")
    yield
    logging.info("Shutting down gracefully...")



app = FastAPI(lifespan=lifespan)




@app.post("/send-sms/")
async def send_sms(data: Message):
    
    twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    twilio_phone_number = os.getenv('TWILIO_NUMBER')

    if not all([twilio_account_sid, twilio_auth_token, twilio_phone_number]):
        logging.error("Missing Twilio environment variables.")
        return JSONResponse(status_code=500, content={"message": "Twilio credentials are not set properly."})

    url = f"https://api.twilio.com/2010-04-01/Accounts/{twilio_account_sid}/Messages.json"
    payload = {
        'Body': data.Body,
        'From': twilio_phone_number,
        'To': data.To
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                url=url,
                data=payload,
                auth=(twilio_account_sid, twilio_auth_token)
            )
            if response.status_code in [200, 201]:
                return {"message": "SMS sent successfully!"}
            else:
                logging.error(f"Twilio error: {response.status_code} - {response.text}")
                return JSONResponse(status_code=response.status_code, content={
                    "message": "Failed to send SMS",
                    "details": response.text
                })
        except httpx.RequestError as e:
            logging.error(f"HTTPX error: {e}")
            return JSONResponse(status_code=500, content={"message": f"An error occurred: {str(e)}"})

@app.get("/")
async def health_check():
    return {"status": "ok"}
