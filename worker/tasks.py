"""
Reusable worker tasks for seeding data and refreshing feature caches.
"""

from __future__ import annotations

import random
from typing import Sequence

from app import models, schemas
from app.core import config
from app.database import SessionLocal
from app.services import FeatureCache, ScoringService

settings = config.get_settings()
cache = FeatureCache(settings.redis_url, settings.feature_cache_ttl_seconds)
scoring_service = ScoringService(settings=settings, cache=cache)


def seed_synthetic_transactions(batch_size: int = 5) -> Sequence[str]:
    """
    Create demo transactions so dashboards/frontends have data to display.
    """

    created_ids: list[str] = []
    with SessionLocal() as session:
        for idx in range(batch_size):
            payload = schemas.PaymentRequest(
                card_number=f"4{random.randint(10**11, 10**12 - 1)}{idx:02d}",
                amount=round(random.uniform(10, 950), 2),
                merchant=f"Demo Merchant {idx + 1}",
                currency="GBP",
                channel="worker-seed",
            )
            decision = scoring_service.evaluate(payload)
            transaction = models.Transaction.from_payment(
                payload=payload,
                status=decision.status,
                risk_flag=decision.reason,
            )
            session.add(transaction)
            session.flush()
            created_ids.append(transaction.id)
        session.commit()
    return created_ids


def refresh_feature_cache(card_number: str) -> dict:
    """
    Recompute and cache features for the supplied card number.
    """

    payload = schemas.PaymentRequest(
        card_number=card_number,
        amount=1.0,
        merchant="Cache Refresh",
    )
    features = scoring_service.generate_feature_snapshot(payload)
    cache.set_features(card_number, features.model_dump())
    return features.model_dump()
