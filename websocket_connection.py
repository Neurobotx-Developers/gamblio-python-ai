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


async def handle_daemon_connection(chat_id, django_websocket):
    async with websockets.connect(CONFIG["DAEMON_WEBSOCKET_URL"]) as daemon_websocket:
        print("Connected to Daemon server")

        while True:
            received_django = await receive(django_websocket)

            if not "text" in received_django:
                continue

            question = received_django["text"]

            await send(daemon_websocket, {"question": question, "chat_id": chat_id})
            daemon_response = await receive(daemon_websocket)

            if daemon_response["data"]["sure"] == False:
                await send(
                    django_websocket, {"tag": "bot_cannot_answer", "chat_id": chat_id}
                )

                break

            await send(
                django_websocket,
                {
                    "tag": "bot_send",
                    "chat_id": chat_id,
                    "text": daemon_response["data"]["answer"],
                    "source": daemon_response["source"],
                    "cost": daemon_response["cost"],
                },
            )


async def handle_django_connection(chat_id):
    async with websockets.connect(CONFIG["DJANGO_WEBSOCKET_URL"]) as django_websocket:
        await send(django_websocket, {"tag": "bot_subscribe", "chat_id": chat_id})

        await handle_daemon_connection(chat_id, django_websocket)
