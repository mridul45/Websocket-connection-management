# import asyncio
# from async_limiter import AsyncLimiter

# connection_limiter = asyncio.BoundedSemaphore(value=5)

# message_rate_limiters = {}

# limiter = AsyncLimiter(max_rate=10, time_period=10)


# async def rate_limit(ip_address: str):
#     if ip_address not in message_rate_limiters:
#         message_rate_limiters[ip_address] = {"count": 0, "timestamp": asyncio.get_event_loop().time()}

#     limiter = message_rate_limiters[ip_address]
#     current_time = asyncio.get_event_loop().time()

#     if current_time - limiter["timestamp"] > TIME_WINDOW:
#         limiter["count"] = 0
#         limiter["timestamp"] = current_time

#     if limiter["count"] < RATE_LIMIT:
#         limiter["count"] += 1
#         return True
#     else:
#         return False