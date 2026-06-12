from pydantic import BaseModel
from typing import Optional


class AnalysisRequest(BaseModel):
    idea: str
    session_id: Optional[str] = None


class QARequest(BaseModel):
    session_id: str
    question: str


class CompareRequest(BaseModel):
    idea_a: str
    idea_b: str
