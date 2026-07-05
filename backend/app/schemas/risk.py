"""Risk / inversion review schemas."""

from pydantic import BaseModel


class RiskReview(BaseModel):
    top_risks: list[str]
    thesis_killers: list[str]
    inversion_question: str
