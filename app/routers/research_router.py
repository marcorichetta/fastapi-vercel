from fastapi import APIRouter, Request
from pydantic import BaseModel
from app.services import research_service
from app.models.research_request import ResearchRequest


router = APIRouter()


@router.post("/research")
async def research_product(request: ResearchRequest):
    try:
        response = await research_service.research_product(request)
        return response
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return {"status": "error", "detail": str(e)}
