"""
Audit logging helpers for transaction decisions.
"""

from __future__ import annotations

from typing import Iterable, List

from sqlalchemy.orm import Session

from app import models, schemas


class AuditService:
    """
    Persists decision audits and exposes query helpers for FastAPI endpoints.
    """

    def record(
        self,
        db: Session,
        payload: schemas.DecisionAuditCreate,
    ) -> models.DecisionAudit:
        audit = models.DecisionAudit(
            transaction_id=payload.transaction_id,
            request_payload=payload.request_payload,
            decision_payload=payload.decision_payload.model_dump(),
            latency_ms=payload.decision_payload.latency_ms,
        )
        db.add(audit)
        db.commit()
        db.refresh(audit)
        return audit

    def fetch_by_transaction(
        self,
        db: Session,
        transaction_id: str,
    ) -> List[models.DecisionAudit]:
        return (
            db.query(models.DecisionAudit)
            .filter(models.DecisionAudit.transaction_id == transaction_id)
            .order_by(models.DecisionAudit.created_at.desc())
            .all()
        )

    @staticmethod
    def to_schema(audits: Iterable[models.DecisionAudit]) -> list[schemas.DecisionAuditResponse]:
        return [schemas.DecisionAuditResponse.from_orm(audit) for audit in audits]
