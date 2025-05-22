from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Request, Depends, HTTPException
from pydantic import BaseModel

from app.services.translation_anonymizer import TranslationAnonymizerService

router = APIRouter(prefix="/translation", tags=["translation"])


class TranslationAnonymizeRequest(BaseModel):
    text: str
    language: str
    session_id: Optional[str] = None


class TranslationDeanonymizeRequest(BaseModel):
    text: str
    session_id: str


class EntityResult(BaseModel):
    entity_type: str
    start: int
    end: int
    score: float
    value: str


class AnonymizationResponse(BaseModel):
    anonymized_text: str
    entity_mapping: Dict[str, Dict[str, Any]]
    replacement_list: List[Dict[str, str]]
    session_id: str
    analysis_results: List[EntityResult]


class DeanonymizationResponse(BaseModel):
    deanonymized_text: str


@router.post("/anonymize", response_model=AnonymizationResponse)
async def anonymize_for_translation(req: TranslationAnonymizeRequest, request: Request):
    """Anonymize text for translation, storing the original entities for later deanonymization."""
    if not hasattr(request.app.state, "translation_anonymizer"):
        request.app.state.translation_anonymizer = TranslationAnonymizerService()
    
    service = request.app.state.translation_anonymizer
    
    session_id = req.session_id or "default"
    
    try:
        anonymized_text, entity_mapping, analysis_results, replacement_list = service.analyze_and_anonymize(
            text=req.text,
            language=req.language,
            session_id=session_id
        )
        
        return {
            "anonymized_text": anonymized_text,
            "entity_mapping": entity_mapping,
            "replacement_list": replacement_list,
            "session_id": session_id,
            "analysis_results": analysis_results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/deanonymize", response_model=DeanonymizationResponse)
async def deanonymize_translated_text(req: TranslationDeanonymizeRequest, request: Request):
    """Deanonymize previously anonymized text after translation."""
    # Check if the service exists
    if not hasattr(request.app.state, "translation_anonymizer"):
        raise HTTPException(status_code=400, detail="Translation anonymizer service not initialized")
    
    service = request.app.state.translation_anonymizer
    
    try:
        deanonymized_text = service.deanonymize_translated(
            translated_text=req.text,
            session_id=req.session_id
        )
        
        return {"deanonymized_text": deanonymized_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mappings/{session_id}")
async def get_mappings(session_id: str, request: Request):
    """Get the stored entity mappings for a specific session."""
    if not hasattr(request.app.state, "translation_anonymizer"):
        raise HTTPException(status_code=400, detail="Translation anonymizer service not initialized")
    
    service = request.app.state.translation_anonymizer
    mappings = service.get_stored_mappings(session_id)
    
    return mappings


@router.delete("/session/{session_id}")
async def clear_session(session_id: str, request: Request):
    """Clear stored mappings for a specific session."""
    if not hasattr(request.app.state, "translation_anonymizer"):
        raise HTTPException(status_code=400, detail="Translation anonymizer service not initialized")
    
    service = request.app.state.translation_anonymizer
    service.clear_session(session_id)
    
    return {"message": f"Session {session_id} cleared"}
