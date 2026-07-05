"""Backend-only QVeris.ai gateway client.

QVeris is the unified capability-routing and financial-data gateway.
The client implements the discover -> inspect -> call workflow. The API
key is read from the environment and never leaves the backend.
"""

import logging
from typing import Any, Optional

import httpx

from ..config import Settings, get_settings

logger = logging.getLogger(__name__)


class QverisNotConfiguredError(RuntimeError):
    """Raised when QVERIS_API_KEY is missing; callers fall back to mock data."""


class QverisApiError(RuntimeError):
    pass


class QverisClient:
    def __init__(self, settings: Optional[Settings] = None, timeout: float = 20.0):
        self._settings = settings or get_settings()
        self._timeout = timeout
        self._capability_cache: Optional[list[dict]] = None

    @property
    def is_configured(self) -> bool:
        return bool(self._settings.qveris_api_key)

    @property
    def base_url(self) -> str:
        return self._settings.qveris_base_url.rstrip("/")

    @property
    def session_id(self) -> str:
        return self._settings.qveris_session_id

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._settings.qveris_api_key}",
            "X-Qveris-Session": self._settings.qveris_session_id,
            "Content-Type": "application/json",
        }

    def _require_configured(self) -> None:
        if not self.is_configured:
            raise QverisNotConfiguredError(
                "QVERIS_API_KEY is not set. Falling back to explicit MOCK DATA."
            )

    def _request(self, method: str, path: str, json: Optional[dict] = None, params: Optional[dict] = None) -> Any:
        self._require_configured()
        url = f"{self.base_url}{path}"
        try:
            with httpx.Client(timeout=self._timeout) as client:
                resp = client.request(method, url, headers=self._headers(), json=json, params=params)
                resp.raise_for_status()
                return resp.json()
        except httpx.HTTPError as exc:
            # Never log headers/keys; only the URL path and error class.
            logger.warning("QVeris request failed: %s %s (%s)", method, path, exc.__class__.__name__)
            raise QverisApiError(f"QVeris request failed: {method} {path}") from exc

    # -- discover -> inspect -> call workflow ------------------------------

    def discover(self, query: str = "", category: str = "") -> list[dict]:
        """Discover available financial-data capabilities."""
        params = {}
        if query:
            params["q"] = query
        if category:
            params["category"] = category
        data = self._request("GET", "/tools/discover", params=params)
        tools = data.get("tools", data) if isinstance(data, dict) else data
        self._capability_cache = tools if isinstance(tools, list) else []
        return self._capability_cache

    def inspect(self, capability_id: str) -> dict:
        """Inspect one capability: parameter schema, provider, freshness."""
        return self._request("GET", f"/tools/{capability_id}")

    def call(self, capability_id: str, params: dict) -> dict:
        """Invoke a capability with validated parameters."""
        return self._request(
            "POST",
            f"/tools/{capability_id}/call",
            json={"params": params, "session_id": self.session_id},
        )

    # -- convenience selectors ---------------------------------------------

    def find_capability(self, category: str, keywords: list[str]) -> Optional[str]:
        """Pick the first discovered capability matching category/keywords."""
        try:
            tools = self._capability_cache or self.discover(category=category)
        except QverisApiError:
            return None
        for tool in tools:
            text = f"{tool.get('name', '')} {tool.get('description', '')} {tool.get('category', '')}".lower()
            if any(kw in text for kw in keywords):
                return tool.get("id") or tool.get("capability_id")
        return None
