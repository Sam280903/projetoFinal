from pydantic import BaseModel
from typing import Optional


class AnalysisRequest(BaseModel):
    idea: str
    session_id: Optional[str] = None
    image_context: Optional[str] = None  # descrição gerada pelo Vision Agent


class QARequest(BaseModel):
    session_id: str
    question: str


class CompareRequest(BaseModel):
    idea_a: str
    idea_b: str
