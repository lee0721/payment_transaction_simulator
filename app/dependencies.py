"""
FastAPI dependency providers for shared services.
"""

from functools import lru_cache

from app.core import config
from app.services import AuditService, FeatureCache, ScoringService


@lru_cache
def get_feature_cache() -> FeatureCache:
    settings = config.get_settings()
    return FeatureCache(
        redis_url=settings.redis_url,
        ttl_seconds=settings.feature_cache_ttl_seconds,
    )


@lru_cache
def get_scoring_service() -> ScoringService:
    settings = config.get_settings()
    return ScoringService(settings=settings, cache=get_feature_cache())


@lru_cache
def get_audit_service() -> AuditService:
    return AuditService()
