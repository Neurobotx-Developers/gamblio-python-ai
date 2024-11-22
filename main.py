import asyncio
from websocket_connection import connect_and_communicate
import argparse
import sentry_sdk

sentry_sdk.init(
    dsn="https://41c29ff02a7ed183b7572a607738825b@o4508342458384384.ingest.de.sentry.io/4508342480076880",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    traces_sample_rate=1.0,
)

# Manually call start_profiler and stop_profiler
# to profile the code in between
sentry_sdk.profiler.start_profiler()

parser = argparse.ArgumentParser()
parser.add_argument("--chat_id", type=int, help="ID of the chat")

args = parser.parse_args()

asyncio.get_event_loop().run_until_complete(connect_and_communicate(args.chat_id))
