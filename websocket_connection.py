import json
from config import CONFIG
import websockets
from websocket import create_connection
import asyncio


async def send(websocket, message):
    await websocket.send(json.dumps(message))
    print(f"Sent: {message}")


async def receive(websocket):
    response = json.loads(await websocket.recv())
    print(f"Received: {response}")

    return response


async def send_ping(websocket, interval=10):
    """Send periodic ping frames to keep the WebSocket connection alive."""
    while True:
        try:
            print("sending ping")
            websocket.send(json.dumps({"ping": "ping"}))
            await asyncio.sleep(interval)
        except Exception as e:
            print(f"Ping failed: {e}")
            break


async def connect_and_communicate(chat_id):
    async with websockets.connect(CONFIG["WEBSOCKET_URL"]) as django_websocket:
        await send(django_websocket, {"tag": "bot_subscribe", "chat_id": chat_id})
        daemonUri = "ws://localhost:8765"
        daemon_websocket = create_connection(daemonUri)
        ping_task = asyncio.create_task(send_ping(daemon_websocket))
        print("Connected to Daemon server")

        while True:
            received_django = await receive(django_websocket)

            if "pong" in received_django:
                print("got pong")
                continue

            if not "text" in received_django:
                continue

            question = received_django["text"]

            daemon_websocket.send(
                json.dumps({"question": question, "chat_id": chat_id})
            )
            daemon_response = json.loads(daemon_websocket.recv())

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

        ping_task.cancel()
