"""Settings + market-data status endpoints.

Settings expose only connection *status* — never API keys. There is no
model-provider selector: DeepSeek is the only LLM runtime.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..schemas.llm import DeepSeekStatus
from ..schemas.qveris import QverisStatus
from ..services.deepseek_client import DeepSeekClient
from ..services.market_data_service import MarketDataService
from ..storage.database import get_db
from ..storage.models import AppSetting

router = APIRouter(prefix="/api", tags=["settings"])

_market_data = MarketDataService()

_DEFAULTS = {
    "default_language": "en",
    "default_analysis_mode": "full_memo",
    "report_language_follows_ui": "true",
}


class SettingsOut(BaseModel):
    values: dict[str, str]
    deepseek: DeepSeekStatus
    qveris: QverisStatus


class SettingsUpdate(BaseModel):
    values: dict[str, str]


def _read_settings(db: Session) -> dict[str, str]:
    stored = {row.key: row.value for row in db.query(AppSetting).all()}
    return {**_DEFAULTS, **stored}


@router.get("/settings", response_model=SettingsOut)
def get_settings_endpoint(db: Session = Depends(get_db)):
    return SettingsOut(
        values=_read_settings(db),
        deepseek=DeepSeekClient().status(),
        qveris=_market_data.status(),
    )


@router.put("/settings", response_model=SettingsOut)
def update_settings(body: SettingsUpdate, db: Session = Depends(get_db)):
    for key, value in body.values.items():
        if key not in _DEFAULTS:
            continue
        row = db.get(AppSetting, key)
        if row is None:
            db.add(AppSetting(key=key, value=value))
        else:
            row.value = value
    db.commit()
    return SettingsOut(
        values=_read_settings(db),
        deepseek=DeepSeekClient().status(),
        qveris=_market_data.status(),
    )
