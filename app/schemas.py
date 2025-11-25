from __future__ import annotations

from datetime import datetime
from typing import Any, Optional, TYPE_CHECKING

from pydantic import BaseModel, Field, validator


class PaymentRequest(BaseModel):
    card_number: str = Field(
        ...,
        min_length=12,
        max_length=19,
        description="Primary account number used for the simulated transaction.",
    )
    amount: float = Field(..., gt=0, description="Transaction amount in the default currency.")
    currency: str = Field(
        "GBP",
        min_length=3,
        max_length=3,
        description="ISO 4217 currency code. Default: GBP.",
    )
    merchant: str = Field(..., min_length=1, description="Merchant name for the transaction.")
    channel: Optional[str] = Field(
        default="ecommerce",
        description="Channel descriptor (e.g., ecommerce, in-store).",
    )
    device_id: Optional[str] = Field(
        default=None,
        description="Device fingerprint or ID associated with the transaction.",
    )

    @validator("card_number")
    def card_number_is_numeric(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("card_number must contain digits only.")
        return value


class TransactionFeatures(BaseModel):
    spending_velocity: float = Field(..., ge=0, le=1, description="Normalized velocity score.")
    device_trust_score: float = Field(..., ge=0, le=1, description="Device reputation score.")
    ip_risk_score: float = Field(..., ge=0, le=1, description="IP risk score.")


class RiskDecision(BaseModel):
    status: str = Field(..., description="Authorization result for the transaction.")
    score: float = Field(..., ge=0, le=1, description="Normalized risk score (0-1).")
    reason: Optional[str] = Field(
        default=None,
        description="Explanation for the risk decision.",
    )
    latency_ms: float = Field(..., ge=0, description="End-to-end scoring latency in milliseconds.")
    features: TransactionFeatures


class PaymentResponse(BaseModel):
    transaction_id: str = Field(..., description="Unique identifier for the transaction.")
    status: str = Field(..., description="Authorization result for the transaction.")
    decision_reason: Optional[str] = Field(
        default=None,
        description="Short reason describing why the decision was made.",
    )
    score: Optional[float] = Field(
        default=None,
        ge=0,
        le=1,
        description="Risk score included for demo purposes.",
    )
    latency_ms: Optional[float] = Field(
        default=None,
        ge=0,
        description="Latency reported by the scoring service.",
    )
    features: Optional[TransactionFeatures] = Field(
        default=None,
        description="Feature snapshot used during scoring.",
    )


class TransactionResponse(BaseModel):
    id: str
    card_last4: str
    amount: float
    currency: str
    merchant: str
    channel: Optional[str] = None
    device_id: Optional[str] = None
    status: str
    risk_flag: Optional[str] = None
    created_at: datetime

    @classmethod
    def from_orm(cls, transaction: "TransactionProtocol") -> "TransactionResponse":
        return cls(
            id=transaction.id,
            card_last4=transaction.card_number[-4:],
            amount=transaction.amount,
            currency=getattr(transaction, "currency", "GBP"),
            merchant=transaction.merchant,
            channel=getattr(transaction, "channel", None),
            device_id=getattr(transaction, "device_id", None),
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
    p95_latency: Optional[float] = Field(
        default=None,
        description="P95 scoring latency derived from decision audit logs.",
    )


class DecisionAuditCreate(BaseModel):
    transaction_id: str
    request_payload: dict[str, Any]
    decision_payload: RiskDecision


class DecisionAuditResponse(BaseModel):
    id: str
    transaction_id: str
    request_payload: dict[str, Any]
    decision_payload: RiskDecision
    latency_ms: float
    created_at: datetime

    @classmethod
    def from_orm(cls, audit: "DecisionAuditProtocol") -> "DecisionAuditResponse":
        return cls(
            id=audit.id,
            transaction_id=audit.transaction_id,
            request_payload=audit.request_payload,
            decision_payload=RiskDecision(**audit.decision_payload),
            latency_ms=audit.latency_ms,
            created_at=audit.created_at,
        )


if TYPE_CHECKING:  # pragma: no cover - typing helper
    from typing import Protocol

    class TransactionProtocol(Protocol):
        id: str
        card_number: str
        amount: float
        currency: str
        merchant: str
        channel: Optional[str]
        device_id: Optional[str]
        status: str
        risk_flag: Optional[str]
        created_at: datetime

    class DecisionAuditProtocol(Protocol):
        id: str
        transaction_id: str
        request_payload: dict[str, Any]
        decision_payload: dict[str, Any]
        latency_ms: float
        created_at: datetime
