from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union


class AnonymizeRequest(BaseModel):
    text: str
    analyzer_results: List[Dict[str, Any]]
    anonymizers: Optional[Dict[str, Union[str, Dict[str, Any]]]] = None


class AnonymizeResult(BaseModel):
    text: str
    items: Optional[List[Dict[str, Any]]] = None


class DeanonymizeEntity(BaseModel):
    start: int
    end: int
    entity_type: str
    text: str


class DeanonymizeRequest(BaseModel):
    text: str
    entities: List[DeanonymizeEntity]
    deanonymizers: Optional[Dict[str, Union[str, Dict[str, Any]]]] = None
