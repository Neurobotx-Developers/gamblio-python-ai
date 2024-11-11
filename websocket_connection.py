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
    async with websockets.connect(CONFIG["WEBSOCKET_URL"]) as django_websocket:
        await send(django_websocket, {"tag": "bot_subscribe", "chat_id": chat_id})
        daemonUri = "ws://localhost:8765"
        daemon_websocket = create_connection(daemonUri)
        print("Connected to Daemon server")

        while True:
            received_django = await receive(django_websocket)
            if not "text" in received_django:
                continue

            question = received_django["text"]

            daemon_websocket.send(json.dumps({"question": question}))
            daemon_response = json.loads(daemon_websocket.recv())

            if daemon_response["data"]["sure"] == False:
                await send(
                    django_websocket, {"tag": "bot_cannot_answer", "chat_id": chat_id}
                )

            await send(
                django_websocket,
                {
                    "tag": "bot_send",
                    "chat_id": chat_id,
                    "text": daemon_response["data"]["answer"],
                    "source": daemon_response["source"],
                },
            )
