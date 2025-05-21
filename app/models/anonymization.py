"""Models for text anonymization and deanonymization."""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union


class AnonymizeRequest(BaseModel):
    """Request model for anonymizing text with PII entities."""
    text: str
    analyzer_results: List[Dict[str, Any]]
    anonymizers: Optional[Dict[str, Union[str, Dict[str, Any]]]] = None


class AnonymizeResult(BaseModel):
    """Response model for anonymized text."""
    text: str
    items: Optional[List[Dict[str, Any]]] = None


class DeanonymizeEntity(BaseModel):
    """Entity model for deanonymization."""
    start: int
    end: int
    entity_type: str
    text: str


class DeanonymizeRequest(BaseModel):
    """Request model for deanonymizing text."""
    text: str
    entities: List[DeanonymizeEntity]
    deanonymizers: Optional[Dict[str, Union[str, Dict[str, Any]]]] = None
