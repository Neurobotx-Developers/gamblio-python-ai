import json
from config import CONFIG
import websockets









async def send(websocket, message):
    await websocket.send(json.dumps(message))
    print(f"Sent: {message}")


async def receive(websocket):
    response = json.loads(await websocket.recv())
    print(f"Received: {response}")

    return response









async def connect_and_communicate(chat_id):
    async with websockets.connect(CONFIG["WEBSOCKET_URL"]) as websocket:
        await send(websocket, {"tag": "bot_subscribe", "chat_id": chat_id})
        daemonUri = "ws://localhost:8765"
        daemon_websocket = websocket.create_connection(daemonUri)
        print("Connected to Daemon server")  


        while True:
            received_django = await receive(websocket)
            if not "text" in received_django:
                continue

            question = received_django["text"]

            
            await daemon_websocket.send(json.dumps({ question }))
            daemon_response = json.loads(await daemon_websocket.recv())

            if daemon_response.data.sure == False:
                await send(websocket, {"tag": "bot_cannot_answer", "chat_id": chat_id})
            

            await send(
                websocket, {"tag": "bot_send", "chat_id": chat_id, "text": daemon_response.data.answer, "source":daemon_response.source}
            )


       

           
