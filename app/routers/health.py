from fastapi import APIRouter, status
from fastapi.responses import PlainTextResponse

router = APIRouter(
    prefix="", 
    tags=["health"]
)

@router.get(
    "/health", 
    response_class=PlainTextResponse, 
    status_code=status.HTTP_200_OK
)
def health() -> str:
    return "Presidio NER API service is up"
