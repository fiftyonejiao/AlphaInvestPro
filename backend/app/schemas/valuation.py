"""Valuation output schemas. All numbers are deterministic calculations."""

from typing import Literal

from pydantic import BaseModel

ValuationMethod = Literal["simple_multiple", "dcf_light", "fcf_yield", "manual"]


class ValuationAssumption(BaseModel):
    name: str
    value: str
    source: str


class FairValueRange(BaseModel):
    low: float
    base: float
    high: float


class Valuation(BaseModel):
    method: ValuationMethod
    fair_value_range: FairValueRange
    assumptions: list[ValuationAssumption]
