import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, Float, JSON, String

from app.database import Base

if TYPE_CHECKING:  # pragma: no cover - typing helper
    from app.schemas import PaymentRequest


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    card_number = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False, default="GBP")
    merchant = Column(String, nullable=False)
    channel = Column(String, nullable=True)
    device_id = Column(String, nullable=True)
    status = Column(String, nullable=False)
    risk_flag = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    @classmethod
    def from_payment(
        cls, payload: "PaymentRequest", status: str, risk_flag: str | None = None
    ) -> "Transaction":
        return cls(
            card_number=payload.card_number,
            amount=payload.amount,
            currency=payload.currency,
            merchant=payload.merchant,
            channel=payload.channel,
            device_id=payload.device_id,
            status=status,
            risk_flag=risk_flag,
        )


class DecisionAudit(Base):
    __tablename__ = "decision_audits"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_id = Column(String, nullable=False, index=True)
    request_payload = Column(JSON, nullable=False)
    decision_payload = Column(JSON, nullable=False)
    latency_ms = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
