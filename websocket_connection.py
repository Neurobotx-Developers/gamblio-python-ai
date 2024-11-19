import json
from config import CONFIG
import websockets
from websocket import create_connection


async def send(websocket, message):
    await websocket.send(json.dumps(message))
    print(f"Sent: {message}")


async def receive(websocket):
    response = json.loads(await websocket.recv())
    print(f"Received: {response}")

    return response


async def connect_and_communicate(chat_id):
    try:
        async with websockets.connect(CONFIG["WEBSOCKET_URL"]) as django_websocket:
            await send(django_websocket, {"tag": "bot_subscribe", "chat_id": chat_id})
            daemonUri = "ws://localhost:8765"
            async with websockets.connect(daemonUri) as daemon_websocket:
                while True:
                    received_django = await receive(django_websocket)
                    if "text" not in received_django:
                        continue
                    question = received_django["text"]
                    await daemon_websocket.send(json.dumps({"question": question, "chat_id": chat_id}))
                    daemon_response = await receive(daemon_websocket)
                    # Handle the response as needed
    except Exception as e:
        print(f"Error in connect_and_communicate: {e}")
