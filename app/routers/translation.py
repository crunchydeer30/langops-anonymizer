from typing import List

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.services.translation_anonymizer import TranslationAnonymizerService

router = APIRouter(tags=["translation"])


class TranslationAnonymizeRequest(BaseModel):
    text: str
    language: str

class Mapping(BaseModel):
    placeholder: str
    start: int
    end: int
    entity_type: str
    original: str

class AnonymizationResponse(BaseModel):
    anonymized_text: str
    mappings: List[Mapping]


@router.post("/anonymize", response_model=AnonymizationResponse)
async def anonymize_for_translation(req: TranslationAnonymizeRequest, request: Request):
    if not hasattr(request.app.state, "translation_anonymizer"):
        request.app.state.translation_anonymizer = TranslationAnonymizerService()
    service = request.app.state.translation_anonymizer
    anonymized_text, mappings = service.analyze_and_anonymize(
        req.text, req.language
    )
    return {"anonymized_text": anonymized_text, "mappings": mappings}

@router.post(
    "/anonymize/batch",
    response_model=List[AnonymizationResponse],
    summary="Batch anonymize for translation"
)
async def batch_anonymize_for_translation(
    reqs: List[TranslationAnonymizeRequest],
    request: Request
):
    if not hasattr(request.app.state, "translation_anonymizer"):
        request.app.state.translation_anonymizer = TranslationAnonymizerService()
    service = request.app.state.translation_anonymizer

    results: List[AnonymizationResponse] = []
    for req in reqs:
        anonymized_text, mappings = service.analyze_and_anonymize(
            req.text, req.language
        )
        results.append({"anonymized_text": anonymized_text, "mappings": mappings})
    return results
