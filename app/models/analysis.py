from pydantic import BaseModel, field_validator, Field
from typing import List, Optional, Dict, Any


class AnalyzeRequest(BaseModel):
    text: str
    language: str
    correlation_id: Optional[str] = None
    score_threshold: Optional[float] = None
    entities: Optional[List[str]] = None
    return_decision_process: Optional[bool] = None
    ad_hoc_recognizers: Optional[List[Dict[str, Any]]] = None
    context: Optional[Dict[str, Any]] = None
    allow_list: Optional[List[str]] = None
    allow_list_match: Optional[str] = None
    regex_flags: Optional[int] = None
    
    @field_validator('score_threshold')
    def validate_score_threshold(cls, v):
        if v is not None and (v < 0 or v > 1):
            raise ValueError('Score threshold must be between 0 and 1')
        return v


class EntityResult(BaseModel):
    entity_type: str
    start: int
    end: int
    score: float
    recognizer_name: Optional[str] = None
    analysis_explanation: Optional[List[Dict[str, Any]]] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "entity_type": "PHONE_NUMBER",
                "start": 10,
                "end": 24,
                "score": 0.95,
                "recognizer_name": "PhoneRecognizer"
            }
        }
    }
