import asyncio
import websockets

async def mock_gpio_server(websocket):
    """
    WebSocket server that simulates GPIO state changes.
    - `websocket`: The WebSocket connection.
    """
    print("WebSocket client connected. Simulating GPIO state changes...")
    try:
        while True:
            # Simulate GPIO low (False)
            print("Sending GPIO state: LOW (False)")
            await websocket.send("False")  # GPIO low
            await asyncio.sleep(5)  # Wait for 5 seconds

            # Simulate GPIO high (True)
            print("Sending GPIO state: HIGH (True)")
            await websocket.send("True")  # GPIO high
            await asyncio.sleep(5)  # Wait for 5 seconds
    except websockets.exceptions.ConnectionClosed:
        print("WebSocket client disconnected.")

async def start_server():
    """
    Start the WebSocket server.
    """
    # Directly pass the handler without a lambda
    async with websockets.serve(mock_gpio_server, "localhost", 8765):
        print("Mock GPIO WebSocket server running on ws://localhost:8765")
        await asyncio.Future()  # Run forever

# Start the WebSocket server
asyncio.run(start_server())
