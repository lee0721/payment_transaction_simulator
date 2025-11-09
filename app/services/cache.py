"""
Feature cache helper for storing and retrieving transaction signals.
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover - redis optional
    redis = None


class FeatureCache:
    """
    Wraps Redis but gracefully degrades to an in-memory dictionary when Redis
    is unavailable (e.g., during local development without Docker Compose).
    """

    def __init__(self, redis_url: str, ttl_seconds: int = 300) -> None:
        self.redis_url = redis_url
        self.ttl_seconds = ttl_seconds
        self._client = self._build_client()
        self._fallback: dict[str, dict[str, Any]] = {}

    def _build_client(self):
        if redis is None:
            return None
        try:
            return redis.Redis.from_url(
                self.redis_url,
                decode_responses=True,
                health_check_interval=30,
            )
        except Exception:
            return None

    def build_key(self, card_number: str) -> str:
        """
        Compose a deterministic cache key using the last 8 digits of the card.
        """

        return f"features:{card_number[-8:]}"

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        if self._client:
            try:
                data = self._client.get(key)
                if data:
                    return json.loads(data)
            except Exception:
                self._client = None
        return self._fallback.get(key)

    def set(self, key: str, value: Dict[str, Any]) -> None:
        encoded = json.dumps(value)
        if self._client:
            try:
                self._client.setex(key, self.ttl_seconds, encoded)
            except Exception:
                self._client = None
        self._fallback[key] = value

    def get_features(self, card_number: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a feature blob for a card number.
        """

        return self.get(self.build_key(card_number))

    def set_features(self, card_number: str, value: Dict[str, Any]) -> None:
        """
        Cache the feature blob for future requests.
        """

        self.set(self.build_key(card_number), value)
