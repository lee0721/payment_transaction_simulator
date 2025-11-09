from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models
from app.core.constants import APPROVED, DECLINED


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
