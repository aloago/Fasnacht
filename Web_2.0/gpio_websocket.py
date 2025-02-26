import asyncio
import websockets
from gpiozero import Button

# GPIO setup
button = Button(2, pull_up=True)  # GPIO 2 with internal pull-up

async def gpio_state_server(websocket, path=None):
    """
    WebSocket handler that sends the state of a GPIO-connected button.
    Accepts an optional `path` parameter for compatibility.
    """
    print("WebSocket client connected. Starting GPIO state updates...")
    try:
        while True:
            # Read GPIO state (True = high when pressed, False = low when not pressed)
            state = button.is_pressed
            await websocket.send(str(state))
            await asyncio.sleep(0.1)  # Throttle updates to reduce processing load
    except websockets.exceptions.ConnectionClosed:
        print("WebSocket client disconnected.")

# Start WebSocket server on all interfaces at port 8765
start_server = websockets.serve(gpio_state_server, "0.0.0.0", 8765)

# Run the server event loop
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
