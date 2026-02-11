from fastapi import APIRouter
from api.endpoints import llm


api_router = APIRouter()

# LLM endpoint
api_router.include_router(llm.router, prefix="/llm", tags=["LLM"])
