import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
import uvicorn
import logging
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables from a `.env` file
load_dotenv()


# Twilio credentials (set these in your `.env` file for security)
# OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
TWILIO_ACCOUNT_SID = os.getenv('ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('AUTH_TOKEN')
TWILIO_NUMBER = os.getenv('TWILIO_NUMBER')
PORT = int(os.getenv('PORT', 8000))

app = FastAPI()


client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# ye backend hai fastapi 



@app.get("/")
def index():
    return {"message": "Hello, World!"}


@app.get("/api/make_call")
async def make_call(to_number: str = "+916239305919"):
    """
    Initiates a call to the specified number using Twilio.
    """
    try:
        call = client.calls.create(
            url="https://0e40-2404-7c80-64-a240-7d75-b984-c734-51a7.ngrok-free.app/incoming-call",
            to=to_number,
            from_=TWILIO_NUMBER,
        )
        return {"message": "Call initiated", "call_sid": call.sid}
    except Exception as e:
        return {"error": str(e)}

@app.get("/send_message")
async def send_message(to_number: str = "+918077937203"):
    message =client.messages.create(
        to=to_number,
        from_=TWILIO_NUMBER,
        body="Hello, this is a test message from Twilio. by prakhar deep for the complete integration of twilio with fastapi "
    )
    return {"message": "Message sent", "message_sid": message.sid}

@app.api_route("/incoming-call", methods=["GET", "POST"])
async def handle_incoming_call(request: Request):
    """
    Handles incoming calls by responding with Twilio VoiceResponse instructions.
    """
    logging.info("in the handle incoming call")
    response = VoiceResponse()
    response.say("Connecting to the AI assistant.")
    response.say("Hello, how can I help you today?")
    response.say("this call is from prakhar deep about updating the succefull call initailizinf from twilio")
    return str(response)


# Ensure the script runs the server only when executed directly
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)