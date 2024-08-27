import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI
import os
import uuid

from backend.messages.proof import handle_proof_message
from backend.services.queue_service import PikaClient

from backend.routes.proof_requests import router as ProofRequestRouter
from backend.routes.api.proof_requests import router as ProofRequestApiRouter
from backend.routes.users import router as UserRequestRouter

load_dotenv()
app = FastAPI()
pika_client = PikaClient(os.environ.get('RABBITMQ_URL'))

app.include_router(ProofRequestRouter, prefix="/proof_requests", include_in_schema=False)
app.include_router(UserRequestRouter, prefix="/user", include_in_schema=False)

app.include_router(ProofRequestApiRouter, prefix="/api/proof_requests")

@app.on_event('startup')
async def startup():
  consumer_id = str(uuid.uuid4()) 
  loop = asyncio.get_running_loop()

  task = loop.create_task(pika_client.consume(consumer_id, "proofs_queue", handle_proof_message, loop))
  await task