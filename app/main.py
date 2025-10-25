from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas, models, utils
from app.database import Base, engine, get_db


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Payment Transaction Simulator",
    description="Simulates a card-network payment authorization workflow.",
    version="0.1.0",
)


@app.post(
    "/payment",
    response_model=schemas.PaymentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a simulated payment request",
)
def create_payment(
    payload: schemas.PaymentRequest, db: Session = Depends(get_db)
) -> schemas.PaymentResponse:
    """
    Accept a payment request, perform fraud checks, persist, and return the result.
    """
    decision = utils.evaluate_transaction(payload.amount)
    transaction = models.Transaction.from_payment(
        payload=payload,
        status=decision.status,
        risk_flag=decision.reason,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return schemas.PaymentResponse(
        transaction_id=transaction.id,
        status=transaction.status,
    )


@app.get(
    "/transaction/{transaction_id}",
    response_model=schemas.TransactionResponse,
    summary="Retrieve a transaction by id",
)
def read_transaction(
    transaction_id: str, db: Session = Depends(get_db)
) -> schemas.TransactionResponse:
    transaction = db.get(models.Transaction, transaction_id)
    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )
    return schemas.TransactionResponse.from_orm(transaction)


@app.get(
    "/stats",
    response_model=schemas.StatsResponse,
    summary="Retrieve system processing statistics",
)
def read_stats(db: Session = Depends(get_db)) -> schemas.StatsResponse:
    metrics = utils.calculate_stats(db)
    return schemas.StatsResponse(**metrics)
