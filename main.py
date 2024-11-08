import asyncio
from websocket_connection import connect_and_communicate


def start(chat_id):
    asyncio.get_event_loop().run_until_complete(connect_and_communicate(chat_id))
