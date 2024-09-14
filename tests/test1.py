import asyncio
import websockets

async def test_client(uri, client_id):
    async with websockets.connect(uri) as websocket:
        print(f"Client {client_id} connected.")
        
        messages = [
            "HIGH:Urgent message from client " + str(client_id),
            "LOW:Regular update from client " + str(client_id),
            "MEDIUM:Important update from client " + str(client_id),
            "HIGH:Another urgent message from client " + str(client_id),
            "LOW:Another regular update from client " + str(client_id)
        ]
        
        for message in messages:
            try:
                await websocket.send(message)
                response = await websocket.recv()
                print(f"Client {client_id} received: {response}")
            except websockets.exceptions.ConnectionClosedOK:
                print(f"Client {client_id} connection closed gracefully.")
                break
            except Exception as e:
                print(f"Client {client_id} encountered an error: {e}")
                break
            await asyncio.sleep(2)  # Add a delay between messages

async def main():
    uri = "ws://localhost:8000/ws"
    clients = [test_client(uri, i) for i in range(10)]
    await asyncio.gather(*clients)

if __name__ == "__main__":
    asyncio.run(main())
