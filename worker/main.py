import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI
import os
import uuid

from messages.request import handle_request_message
from services.queue_service import PikaClient

load_dotenv()
app = FastAPI()
pika_client = PikaClient(os.environ.get('RABBITMQ_URL'))

@app.get("/") 
async def main_route():
  return {"message": "Hey, It is me Worker"}

@app.on_event('startup')
async def startup():
  consumer_id = str(uuid.uuid4()) 
  loop = asyncio.get_running_loop()

  task = loop.create_task(pika_client.consume(consumer_id, "requests_queue", handle_request_message, loop))
  await task