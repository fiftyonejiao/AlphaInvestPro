"""Watchlist CRUD endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..storage.database import get_db
from ..storage.models import Report, WatchlistItem

router = APIRouter(prefix="/api/watchlist", tags=["watchlist"])


class WatchlistCreate(BaseModel):
    ticker: str = Field(min_length=1, max_length=16)
    company: str = ""
    note: str = ""


class WatchlistOut(BaseModel):
    id: str
    ticker: str
    company: str
    note: str
    last_verdict: str | None = None
    created_at: str


def _out(item: WatchlistItem) -> WatchlistOut:
    return WatchlistOut(
        id=item.id, ticker=item.ticker, company=item.company,
        note=item.note, last_verdict=item.last_verdict, created_at=item.created_at,
    )


@router.post("", response_model=WatchlistOut, status_code=201)
def add_item(body: WatchlistCreate, db: Session = Depends(get_db)):
    ticker = body.ticker.upper().strip()
    existing = db.query(WatchlistItem).filter(WatchlistItem.ticker == ticker).first()
    if existing:
        return _out(existing)
    latest = (
        db.query(Report).filter(Report.ticker == ticker).order_by(Report.created_at.desc()).first()
    )
    item = WatchlistItem(
        ticker=ticker,
        company=body.company or (latest.company if latest else ""),
        note=body.note,
        last_verdict=latest.final_verdict if latest else None,
    )
    db.add(item)
    db.commit()
    return _out(item)


@router.get("", response_model=list[WatchlistOut])
def list_items(db: Session = Depends(get_db)):
    rows = db.query(WatchlistItem).order_by(WatchlistItem.created_at.desc()).all()
    return [_out(i) for i in rows]


@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: str, db: Session = Depends(get_db)):
    item = db.get(WatchlistItem, item_id)
    if item is None:
        raise HTTPException(404, "Watchlist item not found")
    db.delete(item)
    db.commit()
