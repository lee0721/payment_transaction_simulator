"""
Scoring service that encapsulates the transaction decision heuristics.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass

from app.core import config
from app.core.constants import APPROVED, DECLINED
from app.schemas import PaymentRequest, RiskDecision, TransactionFeatures
from app.services.cache import FeatureCache


@dataclass(slots=True)
class ScoringContext:
    """
    Represents the calculated features and metadata used for a decision.
    """

    features: TransactionFeatures
    latency_ms: float


class ScoringService:
    """
    Provides risk decisions plus rich metadata for downstream logging/audit.
    """

    def __init__(
        self,
        *,
        settings: config.Settings | None = None,
        cache: FeatureCache | None = None,
    ) -> None:
        self.settings = settings or config.get_settings()
        self.cache = cache

    def evaluate(self, payload: PaymentRequest) -> RiskDecision:
        """
        Evaluate a payment request and return a structured risk decision.
        """

        started = time.perf_counter()
        features = self._fetch_or_generate_features(payload)
        status, reason = self._apply_rules(payload.amount)
        latency_ms = (time.perf_counter() - started) * 1_000
        score = self._calculate_score(payload.amount, features)
        return RiskDecision(
            status=status,
            reason=reason,
            score=round(score, 4),
            latency_ms=round(latency_ms, 2),
            features=features,
        )

    def _apply_rules(self, amount: float) -> tuple[str, str | None]:
        threshold = self.settings.high_amount_threshold
        high_amount_decline_rate = self.settings.high_amount_decline_rate
        random_decline_rate = self.settings.random_decline_rate
        rng = random.random()

        if amount > threshold:
            if rng < high_amount_decline_rate:
                return DECLINED, "High amount flagged by risk heuristic."
            return APPROVED, None
        if rng < random_decline_rate:
            return DECLINED, "Randomized decline to simulate fraud checks."
        return APPROVED, None

    def _fetch_or_generate_features(self, payload: PaymentRequest) -> TransactionFeatures:
        if self.cache:
            cached = self.cache.get_features(payload.card_number)
            if cached:
                return TransactionFeatures(**cached)

        features = self._generate_features(payload)
        if self.cache:
            self.cache.set_features(payload.card_number, features.model_dump())
        return features

    def _generate_features(self, payload: PaymentRequest) -> TransactionFeatures:
        """
        Generate deterministic-yet-randomized features so demos stay reproducible.
        """

        seed = int(payload.card_number[-4:])
        rng = random.Random(seed)
        return TransactionFeatures(
            spending_velocity=round(rng.uniform(0.1, 0.95), 3),
            device_trust_score=round(rng.uniform(0.2, 0.99), 3),
            ip_risk_score=round(rng.uniform(0.05, 0.9), 3),
        )

    def generate_feature_snapshot(self, payload: PaymentRequest) -> TransactionFeatures:
        """
        Public helper so worker tasks can reuse the deterministic feature generator.
        """

        return self._generate_features(payload)

    def _calculate_score(
        self,
        amount: float,
        features: TransactionFeatures,
    ) -> float:
        """
        Blend amount heuristics with generated features for a pseudo-risk score.
        """

        normalized_amount = min(amount / (self.settings.high_amount_threshold * 2), 1.0)
        score = (
            (1 - features.device_trust_score) * 0.4
            + features.ip_risk_score * 0.3
            + normalized_amount * 0.2
            + features.spending_velocity * 0.1
        )
        return max(0.0, min(score, 1.0))
