import os
import json
import base64
import asyncio
from fastapi import FastAPI, WebSocket, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from twilio.twiml.voice_response import VoiceResponse, Connect
from dotenv import load_dotenv
import uvicorn

# Load environment variables from the .env file
load_dotenv()

# Configuration for OpenAI API
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError('Missing the OpenAI API key. Please set it in the .env file.')

# Constants
SYSTEM_MESSAGE = (
    "You are a helpful and bubbly AI assistant who loves to chat about anything the user is interested in."
)
VOICE = 'alloy'

# Initialize FastAPI app and Jinja2 template rendering
app = FastAPI()
templates = Jinja2Templates(directory="frontend")


# Root Endpoint: Displaying the landing page with the "Enter Data" button
@app.api_route("/", methods=["GET"])
async def index_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Incoming call endpoint: This is where the call will be routed by Twilio
@app.api_route("/incoming-call", methods=["GET", "POST"])
async def handle_incoming_call(request: Request):
    """
    This function handles the incoming call and returns a TwiML response.
    If the request is from the browser (i.e., accessing the UI), it displays the page.
    """
    # GET request - if the request is from Twilio, return TwiML
    user_agent = request.headers.get('User-Agent', '')
    if 'Twilio' in user_agent:
        # This request is from Twilio, return TwiML
        response = VoiceResponse()

        response.say("Hi there! We're connecting your call to our AI assistant.")
        response.pause(length=1)
        response.say("O.K. you can start talking!")

        host = request.url.hostname
        connect = Connect()
        connect.stream(url=f'wss://{host}/media-stream')
        response.append(connect)

        return HTMLResponse(content=str(response), media_type="application/xml")
    
    # If this is a browser request (GET request), show connecting info and user data
    return templates.TemplateResponse("call.html", {"request": request})
    

# WebSocket for handling media stream between Twilio and OpenAI
@app.websocket("/media-stream")
async def handle_media_stream(websocket: WebSocket):
    """Handle WebSocket connections between Twilio and OpenAI."""
    print("Client connected")
    await websocket.accept()

    async with websockets.connect(
            'wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01',
            extra_headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "OpenAI-Beta": "realtime=v1"
            }) as openai_ws:
        await send_session_update(openai_ws)
        stream_sid = None

        async def receive_from_twilio():
            """Receive audio data from Twilio and send it to OpenAI."""
            nonlocal stream_sid
            try:
                async for message in websocket.iter_text():
                    data = json.loads(message)
                    if data['event'] == 'media' and openai_ws.open:
                        audio_append = {
                            "type": "input_audio_buffer.append",
                            "audio": data['media']['payload']
                        }
                        await openai_ws.send(json.dumps(audio_append))
                    elif data['event'] == 'start':
                        stream_sid = data['start']['streamSid']
                        print(f"Incoming stream has started {stream_sid}")
            except WebSocketDisconnect:
                print("Client disconnected.")
                if openai_ws.open:
                    await openai_ws.close()


        async def send_to_twilio():
            """Receive events from OpenAI Realtime API and send audio back to Twilio."""
            nonlocal stream_sid
            try:
                async for openai_message in openai_ws:
                    response = json.loads(openai_message)
                    if response['type'] == 'response.audio.delta' and response.get('delta'):
                        # Audio from OpenAI
                        try:
                            audio_payload = base64.b64encode(base64.b64decode(response['delta'])).decode('utf-8')
                            audio_delta = {
                                "event": "media",
                                "streamSid": stream_sid,
                                "media": {
                                    "payload": audio_payload
                                }
                            }
                            await websocket.send_json(audio_delta)
                        except Exception as e:
                            print(f"Error processing audio data: {e}")
            except Exception as e:
                print(f"Error in send_to_twilio: {e}")

        await asyncio.gather(receive_from_twilio(), send_to_twilio())


async def send_session_update(openai_ws):
    """Send session update to OpenAI WebSocket."""
    session_update = {
        "type": "session.update",
        "session": {
            "turn_detection": {
                "type": "server_vad"
            },
            "input_audio_format": "g711_ulaw",
            "output_audio_format": "g711_ulaw",
            "voice": VOICE,
            "instructions": SYSTEM_MESSAGE,
            "modalities": ["text", "audio"],
            "temperature": 0.8,
        }
    }
    print('Sending session update:', json.dumps(session_update))
    await openai_ws.send(json.dumps(session_update))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
