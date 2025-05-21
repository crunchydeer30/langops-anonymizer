from pydantic import BaseModel
from typing import Dict, Any, Optional


class OperatorConfig(BaseModel):
    type: str
    params: Optional[Dict[str, Any]] = None
