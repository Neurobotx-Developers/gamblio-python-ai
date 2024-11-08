import asyncio
from websocket_connection import connect_and_communicate
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--chat_id", type=int, help="ID of the chat")

args = parser.parse_args()


asyncio.get_event_loop().run_until_complete(connect_and_communicate(args.chat_id))
