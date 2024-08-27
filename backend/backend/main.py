from dotenv import load_dotenv
from fastapi import FastAPI
from backend.routes.proof_requests import router as ProofRequestRouter
from backend.routes.api.proof_requests import router as ProofRequestApiRouter
from backend.routes.users import router as UserRequestRouter

load_dotenv()
app = FastAPI()

app.include_router(ProofRequestRouter, prefix="/proof_requests", include_in_schema=False)
app.include_router(UserRequestRouter, prefix="/user", include_in_schema=False)

app.include_router(ProofRequestApiRouter, prefix="/api/proof_requests")