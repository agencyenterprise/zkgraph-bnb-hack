from dotenv import load_dotenv
from fastapi import FastAPI
from routes.proof_requests import router as ProofRequestRouter

load_dotenv()
app = FastAPI()

app.include_router(ProofRequestRouter, tags=["Circuit"], prefix="/proof_requests")