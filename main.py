import asyncio
from websocket_connection import connect_and_communicate
import argparse
import sentry_sdk

sentry_sdk.init(
    dsn="https://37cac10e14a03768e2d7a64225aa7c6e@o4508318885019648.ingest.de.sentry.io/4508324683776080",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    traces_sample_rate=1.0,
)

# Manually call start_profiler and stop_profiler
# to profile the code in between
sentry_sdk.profiler.start_profiler()
division_by_zero = 1 / 0

parser = argparse.ArgumentParser()
parser.add_argument("--chat_id", type=int, help="ID of the chat")

args = parser.parse_args()


asyncio.get_event_loop().run_until_complete(connect_and_communicate(args.chat_id))
