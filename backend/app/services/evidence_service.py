"""Evidence collection: every data fetch is recorded with provenance."""

from ..schemas.analysis import EvidenceSource
from ..schemas.qveris import MarketDataBundle


def collect_evidence(bundle: MarketDataBundle) -> list[EvidenceSource]:
    sources: list[EvidenceSource] = []
    for name, obj in (
        ("Quote", bundle.quote),
        ("Company profile", bundle.profile),
        ("Fundamentals", bundle.fundamentals),
        ("News & sentiment", bundle.news),
    ):
        m = obj.meta
        sources.append(
            EvidenceSource(
                name=name,
                provider=m.provider,
                capability_id=m.capability_id,
                retrieval_timestamp=m.retrieval_timestamp,
                source_timestamp=m.source_timestamp,
                is_mock=m.is_mock,
                note=m.quality_notes,
            )
        )
    return sources


def required_fields_present(bundle: MarketDataBundle) -> tuple[bool, list[str]]:
    """Validation gate: final reports are rejected (or marked incomplete)
    when required financial fields are missing."""
    f = bundle.fundamentals
    missing = []
    if bundle.quote.price is None or bundle.quote.price <= 0:
        missing.append("quote.price")
    if f.revenue is None:
        missing.append("fundamentals.revenue")
    if f.net_income is None:
        missing.append("fundamentals.net_income")
    if f.eps is None and f.free_cash_flow is None:
        missing.append("fundamentals.eps_or_fcf")
    return (len(missing) == 0, missing)
