import aio_pika

class PikaClient:
    def __init__(self, rabbit_url):
        self.rabbit_url = rabbit_url

    async def consume(self, consumer_id: str, queue_name: str, callback, loop):
        connection = await aio_pika.connect_robust(self.rabbit_url, loop=loop)
        channel = await connection.channel()
        queue = await channel.declare_queue(queue_name)

        async def process_incoming_message(message):
            body = message.body

            if body:
                await message.ack()
                await callback(body, consumer_id)

        await queue.consume(process_incoming_message)

        return connection
    
    async def publish(self, queue_name: str, message: str):
        connection = await aio_pika.connect_robust(self.rabbit_url)
        channel = await connection.channel()
        await channel.declare_queue(queue_name)

        await channel.default_exchange.publish(aio_pika.Message(body=message.encode()), routing_key=queue_name)
        await connection.close()
