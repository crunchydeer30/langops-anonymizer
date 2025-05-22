from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List
from app.models.analysis import AnalyzeRequest, EntityResult
from app.services.analyzer import AnalyzerService
from app.config import get_settings
from functools import lru_cache

router = APIRouter(prefix="/system", tags=["analysis"])

@lru_cache()
def get_analyzer_service() -> AnalyzerService:
    settings = get_settings()
    return AnalyzerService(settings)

@router.post("/analyze", response_model=List[EntityResult])
def analyze(req: AnalyzeRequest, request: Request):
    try:
        return request.app.state.analyzer.analyze(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recognizers")
def recognizers(request: Request, language: str = None):
    try:
        recognizers_list = request.app.state.analyzer.engine.get_recognizers(language=language)
        return [o.name for o in recognizers_list]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/supportedentities")
def supported_entities(request: Request, language: str = None):
    try:
        entities_list = request.app.state.analyzer.engine.get_supported_entities(language=language)
        return entities_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
