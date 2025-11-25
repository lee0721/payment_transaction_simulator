from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app import schemas, models, utils
from app.database import Base, engine, get_db, SessionLocal
from app.dependencies import get_audit_service, get_scoring_service
from app.services import AuditService, ScoringService


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Payment Transaction Simulator",
    description="Simulates a card-network payment authorization workflow.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_BUILD_DIR = Path(__file__).resolve().parent.parent / "frontend-app" / "dist"

if FRONTEND_BUILD_DIR.exists():
    app.mount("/demo", StaticFiles(directory=FRONTEND_BUILD_DIR, html=True), name="demo")


@app.get("/", include_in_schema=False, response_class=HTMLResponse)
def landing() -> str:
    """
    Provide a human-friendly landing page that points to docs and the interactive demo.
    """
    return """
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Payment Transaction Simulator</title>
        <style>
          body { font-family: Arial, sans-serif; background: #050608; color: #e6f1ff; margin: 0; display:flex; justify-content:center; align-items:center; min-height:100vh; }
          article { text-align:center; max-width:640px; padding:2.5rem 3rem; border-radius:20px; background:rgba(16,22,35,0.82); border:1px solid rgba(94,130,184,0.35); box-shadow:0 25px 45px rgba(8,12,20,0.55); }
          h1 { margin-bottom:0.8rem; }
          p { line-height:1.6; margin-bottom:1.6rem; color:#b5c7e3; }
          a { display:inline-block; margin:0.4rem 0.4rem 0 0.4rem; padding:0.65rem 1.5rem; border-radius:999px; text-decoration:none; font-weight:600; color:#020617; background: linear-gradient(120deg,#67e8f9,#22d3ee); }
        </style>
      </head>
      <body>
        <article>
          <h1>Payment Transaction Simulator</h1>
          <p>
            Explore a payment authorization workflow implemented with FastAPI,
            Postgres/Redis, and Docker. Choose how you want to experience the service:
          </p>
          <div>
            <a href="/docs">Interactive API Docs</a>
            <a href="/demo">Visual Demo UI</a>
            <a href="https://github.com/lee0721/payment_transaction_simulator" target="_blank" rel="noopener">GitHub Repository</a>
          </div>
        </article>
      </body>
    </html>
    """


@app.get("/health", summary="Health check", tags=["Monitoring"])
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/payment",
    response_model=schemas.PaymentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a simulated payment request",
)
def create_payment(
    payload: schemas.PaymentRequest,
    db: Session = Depends(get_db),
    scoring_service: ScoringService = Depends(get_scoring_service),
    audit_service: AuditService = Depends(get_audit_service),
) -> schemas.PaymentResponse:
    """
    Accept a payment request, perform fraud checks, persist, and return the result.
    """
    decision = scoring_service.evaluate(payload)
    transaction = models.Transaction.from_payment(
        payload=payload,
        status=decision.status,
        risk_flag=decision.reason,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    audit_service.record(
        db,
        schemas.DecisionAuditCreate(
            transaction_id=transaction.id,
            request_payload=payload.model_dump(),
            decision_payload=decision,
        ),
    )
    return schemas.PaymentResponse(
        transaction_id=transaction.id,
        status=transaction.status,
        decision_reason=decision.reason,
        score=decision.score,
        latency_ms=decision.latency_ms,
        features=decision.features,
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


@app.get(
    "/audit/{transaction_id}",
    response_model=list[schemas.DecisionAuditResponse],
    summary="Retrieve audit logs for a transaction",
)
def read_audit_logs(
    transaction_id: str,
    db: Session = Depends(get_db),
    audit_service: AuditService = Depends(get_audit_service),
) -> list[schemas.DecisionAuditResponse]:
    audits = audit_service.fetch_by_transaction(db, transaction_id)
    if not audits:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit logs not found for this transaction.",
        )
    return audit_service.to_schema(audits)


@app.delete(
    "/admin/reset",
    response_model=schemas.StatsResponse,
    summary="Delete all transactions and reset metrics",
)
def reset_transactions() -> schemas.StatsResponse:
    """
    Clear all persisted transactions. Intended for demo reset or test automation.
    """
    with SessionLocal() as session:
        session.query(models.DecisionAudit).delete()
        session.query(models.Transaction).delete()
        session.commit()
    with SessionLocal() as session:
        metrics = utils.calculate_stats(session)
    return schemas.StatsResponse(**metrics)
