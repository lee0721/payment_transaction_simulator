import random
from dataclasses import dataclass
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models


APPROVED = "Approved"
DECLINED = "Declined"


@dataclass
class TransactionDecision:
    status: str
    reason: str | None = None


def evaluate_transaction(amount: float) -> TransactionDecision:
    """
    Apply simple fraud heuristics to determine if a transaction is approved.
    """
    rng = random.random()
    if amount > 500:
        if rng < 0.30:
            return TransactionDecision(
                status=DECLINED, reason="High amount flagged by fraud heuristic."
            )
        return TransactionDecision(status=APPROVED)
    if rng < 0.10:
        return TransactionDecision(
            status=DECLINED, reason="Randomized decline to simulate fraud checks."
        )
    return TransactionDecision(status=APPROVED)


def calculate_stats(db: Session) -> dict[str, Any]:
    """
    Compute aggregate metrics across transactions.
    """
    total = db.query(func.count(models.Transaction.id)).scalar() or 0
    approved = (
        db.query(func.count(models.Transaction.id))
        .filter(models.Transaction.status == APPROVED)
        .scalar()
        or 0
    )
    declined = (
        db.query(func.count(models.Transaction.id))
        .filter(models.Transaction.status == DECLINED)
        .scalar()
        or 0
    )
    avg_amount = (
        db.query(func.coalesce(func.avg(models.Transaction.amount), 0.0)).scalar() or 0.0
    )
    approval_rate = approved / total if total else 0.0

    return {
        "total": total,
        "approved": approved,
        "declined": declined,
        "approval_rate": round(approval_rate, 4),
        "avg_amount": round(float(avg_amount), 2),
    }

