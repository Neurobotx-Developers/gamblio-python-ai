import asyncio
import websockets

async def test_client(message):
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        print(f"Client: Sending message '{message}'")
        await websocket.send(message)
        
        response = await websocket.recv()
        print(f"Client: Received response '{response}'")

async def main():
    # Simulate multiple clients sending messages
    messages = ["ko si ti", "kako da se registrujem", "dje su mi pare bre"]
    tasks = [test_client(message) for message in messages]

    # Run all client tasks concurrently
    await asyncio.gather(*tasks)

# Run the client test
asyncio.run(main())
