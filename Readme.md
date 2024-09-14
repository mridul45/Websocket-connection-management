# Assignmant

1. Goal: Websocket connection management for improving the performance and handling high concurrency.
2. In the settings folder you will see 3 files one contains settings for heartbeat,second contains settings for limiter and third contains for redis.

3. Make changes in the limiter file that is increase or decreace the time there for testing purpose

4.  Now in the tests folder in file test1.py change the number inside range clients = [test_client(uri, i) for i in range(10)] for testing.


# RUN the following commands


__Open 2 terminals side by side.__

In one terminal run this command

``` virtualenv env ```

``` source env/bin/activate ```

``` pip install -r requirements.txt ```

``` uvicorn main:app --reload ```


In the second terminal run the test

``` cd tests ```

``` python test1.py ```


__Also the code has been docerized using a Dockerfile , note not used a docker-compse.yml file since there was no need to interact with multiple docker containers__


# Further Improvements


1. When designing for a production grade code/setup Machine Learning can be introduced as it will enhance the functionality.
2. We can explore Kafka , if it can be used here to for any optimizations.
3. Also there can be more improvements in terms of how we are interacting with redis for priority data.


__A potential example of optimization can be the below code__


``` async def manage_message_rate_limit(client_id: str, current_time: datetime):
    # Use pipelining to batch Redis commands if needed
    async with redis.pipeline() as pipe:
        await pipe.lpush(client_id, str(current_time))
        await pipe.ltrim(client_id, 0, RATE_LIMIT - 1)
        message_times = await pipe.lrange(client_id, 0, -1)
        await pipe.execute() 
        
```