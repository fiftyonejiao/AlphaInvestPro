"""QVeris market-data gateway endpoints (status, fetch, sources)."""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..schemas.qveris import MarketDataBundle, QverisStatus
from ..services.market_data_service import MarketDataService

router = APIRouter(prefix="/api/market-data/qveris", tags=["market-data"])

_service = MarketDataService()


class FetchRequest(BaseModel):
    ticker: str = Field(min_length=1, max_length=16)


@router.get("/status", response_model=QverisStatus)
def qveris_status():
    return _service.status()


@router.post("/fetch", response_model=MarketDataBundle)
def qveris_fetch(body: FetchRequest):
    return _service.get_bundle(body.ticker)


@router.get("/sources")
def qveris_sources():
    return {"sources": _service.sources()}
