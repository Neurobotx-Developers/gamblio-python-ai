import websocket

from .config import WEBSOCKET_URL


def on_message(ws, message):
    print(f"Received message: {message}")

def on_error(ws, error):
    print(f"Encountered error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("Connection closed")

def on_open(ws):
    print("Connection opened")
    ws.send("Hello, Server!")

if __name__ == "__main__":
    ws = websocket.WebSocketApp(WEBSOCKET_URL,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()