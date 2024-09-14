import asyncio
import heapq
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Set
import redis
from datetime import datetime, timedelta

app = FastAPI()

# Define rate limiting parameters
RATE_LIMIT = 5  # Max 5 messages
TIME_PERIOD = 5  # Time window of 5 seconds

# Priority levels
PRIORITY = {
    "HIGH": 1,
    "MEDIUM": 2,
    "LOW": 3
}

# Priority queue for messages
message_queue = []

# Set to keep track of connected clients
connected_clients: Set[WebSocket] = set()

# Redis client setup
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

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

async def process_messages():
    while True:
        if message_queue:
            priority, message, websocket = heapq.heappop(message_queue)
            await websocket.send_text(f"Message received: {message}")
        await asyncio.sleep(1)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    client_id = websocket.client.host  # Track client by IP
    await websocket.accept()
    connected_clients.add(websocket)
    
    # Initialize the client's message time history in Redis if not present
    if not redis_client.exists(client_id):
        redis_client.lpush(client_id, str(datetime.now()))

    try:
        while True:
            data = await websocket.receive_text()
            
            # Assume the message is formatted as "priority:message_content"
            priority, message = data.split(":", 1)
            priority = priority.upper()
            
            if priority not in PRIORITY:
                await websocket.send_text("Invalid priority level. Message ignored.")
                continue

            # Get the current time
            current_time = datetime.now()

            # Get message times from Redis
            message_times = redis_client.lrange(client_id, 0, -1)
            message_times = [datetime.fromisoformat(t.decode()) for t in message_times]

            # Remove any messages older than the time window
            message_times = [t for t in message_times if current_time - t < timedelta(seconds=TIME_PERIOD)]

            # Check if rate limit is exceeded
            if len(message_times) >= RATE_LIMIT:
                await websocket.send_text("Rate limit exceeded. Connection closing.")
                await websocket.close()
                break

            # Add current message time to Redis
            redis_client.rpush(client_id, str(current_time))
            redis_client.ltrim(client_id, 0, RATE_LIMIT - 1)  # Keep only the latest RATE_LIMIT messages

            # Add message to the priority queue
            heapq.heappush(message_queue, (PRIORITY[priority], message, websocket))
    
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
        redis_client.delete(client_id)
        print("Client disconnected.")

# Run heartbeat management and message processing in the background
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(manage_heartbeats())
    asyncio.create_task(process_messages())
