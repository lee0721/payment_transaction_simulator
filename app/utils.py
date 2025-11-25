import math
from typing import Any, Iterable, List, Optional

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
    p95_latency = _calculate_percentile(
        [value for (value,) in db.query(models.DecisionAudit.latency_ms).all()],
        percentile=0.95,
    )

    return {
        "total": total,
        "approved": approved,
        "declined": declined,
        "approval_rate": round(approval_rate, 4),
        "avg_amount": round(float(avg_amount), 2),
        "p95_latency": p95_latency,
    }


def _calculate_percentile(values: Iterable[float], percentile: float) -> Optional[float]:
    data: List[float] = sorted(value for value in values if value is not None)
    if not data:
        return None
    percentile = max(0.0, min(percentile, 1.0))
    index = math.ceil(percentile * len(data)) - 1
    index = max(0, index)
    return round(data[index], 2)
