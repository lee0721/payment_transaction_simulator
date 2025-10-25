import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, Float, String

from app.database import Base

if TYPE_CHECKING:  # pragma: no cover - typing helper
    from app.schemas import PaymentRequest


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    card_number = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    merchant = Column(String, nullable=False)
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
            merchant=payload.merchant,
            status=status,
            risk_flag=risk_flag,
        )
