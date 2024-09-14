from typing import Set
from fastapi import WebSocket
import asyncio


connected_clients: Set[WebSocket] = set()


async def send_heartbeat(client: WebSocket, interval: int):
    while client in connected_clients:
        await client.send_text("heartbeat")
        await asyncio.sleep(interval)

async def manage_heartbeats():
    while True:
        num_clients = len(connected_clients)
        print(f"Number of connected clients: {num_clients}")

        # Adjust heartbeat interval based on number of clients
        if num_clients > 10:
            heartbeat_interval = 5  # Minimum interval in seconds
        else:
            heartbeat_interval = 10  # Default interval in seconds

        # Send heartbeats to all connected clients
        tasks = [send_heartbeat(client, heartbeat_interval) for client in connected_clients]
        await asyncio.gather(*tasks)

        # Wait before checking again
        await asyncio.sleep(heartbeat_interval)