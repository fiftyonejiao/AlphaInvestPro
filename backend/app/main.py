"""AlphaInvestPro backend — research-only investment analysis API.

No trading execution exists anywhere in this service.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import analysis_jobs, market_data, reports, settings, watchlist
from .storage.database import init_db

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="AlphaInvestPro API",
    description="Research-only investment analysis workbench. Not financial advice.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis_jobs.router)
app.include_router(reports.router)
app.include_router(watchlist.router)
app.include_router(settings.router)
app.include_router(market_data.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "product": "AlphaInvestPro", "research_only": True}
