from __future__ import annotations

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from pydantic import BaseModel, Field, validator


class PaymentRequest(BaseModel):
    card_number: str = Field(
        ...,
        min_length=12,
        max_length=19,
        description="Primary account number used for the simulated transaction.",
    )
    amount: float = Field(..., gt=0, description="Transaction amount in the default currency.")
    merchant: str = Field(..., min_length=1, description="Merchant name for the transaction.")

    @validator("card_number")
    def card_number_is_numeric(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("card_number must contain digits only.")
        return value


class PaymentResponse(BaseModel):
    transaction_id: str = Field(..., description="Unique identifier for the transaction.")
    status: str = Field(..., description="Authorization result for the transaction.")


class TransactionResponse(BaseModel):
    id: str
    card_last4: str
    amount: float
    merchant: str
    status: str
    risk_flag: Optional[str] = None
    created_at: datetime

    @classmethod
    def from_orm(cls, transaction: "TransactionProtocol") -> "TransactionResponse":
        return cls(
            id=transaction.id,
            card_last4=transaction.card_number[-4:],
            amount=transaction.amount,
            merchant=transaction.merchant,
            status=transaction.status,
            risk_flag=getattr(transaction, "risk_flag", None),
            created_at=transaction.created_at,
        )


class StatsResponse(BaseModel):
    total: int
    approved: int
    declined: int
    approval_rate: float
    avg_amount: float


if TYPE_CHECKING:  # pragma: no cover - typing helper
    from typing import Protocol

    class TransactionProtocol(Protocol):
        id: str
        card_number: str
        amount: float
        merchant: str
        status: str
        risk_flag: Optional[str]
        created_at: datetime

