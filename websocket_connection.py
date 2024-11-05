from websockets.sync.client import connect
import json
from config import WEBSOCKET_URL
import asyncio
import websockets
# def hello():
#     with connect(WEBSOCKET_URL) as websocket:
#         websocket.send(json.dumps({"Hello world":"Hello world"} ))
#         message = websocket.recv.()
        
#         print(f"Received: {message}")

# hello()

async def send(websocket, message):
    await websocket.send(json.dumps(message))
    print(f"Sent: {message}")

async def receive(websocket):
    response = json.loads(await websocket.recv())
    print(f"Received: {response}")

    return response

async def connect_and_communicate():
   
    async with websockets.connect(WEBSOCKET_URL) as websocket:
        await send(websocket, {
            "tag": "bot_subscribe",
            "chat_id": 205
        })
        
        while True:
            response = await receive(websocket)
            await send(websocket, {
                "tag": "bot_send",
                "chat_id": 205,
                "text": response["text"]
            })
            
            

# Run the client connection
# asyncio.run(connect_and_communicate())
asyncio.get_event_loop().run_until_complete(connect_and_communicate())