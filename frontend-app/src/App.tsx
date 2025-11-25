import { FormEvent, useEffect, useState } from "react";
import {
  DecisionAuditResponse,
  PaymentRequest,
  PaymentResponse,
  StatsResponse,
  TransactionResponse
} from "./types/api";
import { useApiClient } from "./hooks/useApiClient";

const defaultPayload: PaymentRequest = {
  card_number: "4000001234567890",
  amount: 150.75,
  currency: "GBP",
  merchant: "Amazon",
  channel: "ecommerce",
  device_id: "ios-demo-device"
};

function App() {
  const api = useApiClient();
  const [paymentPayload, setPaymentPayload] = useState<PaymentRequest>(defaultPayload);
  const [paymentResult, setPaymentResult] = useState<PaymentResponse | null>(null);
  const [transactionLookup, setTransactionLookup] = useState("");
  const [transactionResult, setTransactionResult] = useState<TransactionResponse | null>(null);
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [audits, setAudits] = useState<DecisionAuditResponse[]>([]);
  const [loading, setLoading] = useState({
    payment: false,
    lookup: false,
    stats: false,
    audits: false
  });

  useEffect(() => {
    refreshStats();
  }, []);

  const refreshStats = async () => {
    setLoading((state) => ({ ...state, stats: true }));
    try {
      const response = await api.getStats();
      setStats(response);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading((state) => ({ ...state, stats: false }));
    }
  };

  const submitPayment = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading((state) => ({ ...state, payment: true }));
    try {
      const response = await api.postPayment(paymentPayload);
      setPaymentResult(response);
      setTransactionLookup(response.transaction_id);
      await refreshStats();
      await fetchAuditLogs(response.transaction_id);
    } catch (error) {
      console.error(error);
      setPaymentResult(null);
    } finally {
      setLoading((state) => ({ ...state, payment: false }));
    }
  };

  const fetchTransaction = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!transactionLookup) return;
    setLoading((state) => ({ ...state, lookup: true }));
    try {
      const response = await api.getTransaction(transactionLookup);
      setTransactionResult(response);
      await fetchAuditLogs(transactionLookup);
    } catch (error) {
      console.error(error);
      setTransactionResult(null);
    } finally {
      setLoading((state) => ({ ...state, lookup: false }));
    }
  };

  const fetchAuditLogs = async (transactionId: string) => {
    setLoading((state) => ({ ...state, audits: true }));
    try {
      const response = await api.getAuditLogs(transactionId);
      setAudits(response);
    } catch (error) {
      console.error(error);
      setAudits([]);
    } finally {
      setLoading((state) => ({ ...state, audits: false }));
    }
  };

  const resetDemo = async () => {
    try {
      await api.resetDemo();
      setPaymentResult(null);
      setTransactionResult(null);
      setTransactionLookup("");
      setAudits([]);
      await refreshStats();
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="layout">
      <header>
        <div>
          <p className="eyebrow">RiskOps Demo Stack</p>
          <h1>Full-stack risk control simulator</h1>
          <p className="lede">
            Submit a transaction, inspect stored records, and introspect audit logs powered by the
            modular FastAPI services you just extended.
          </p>
        </div>
        <div className="header-actions">
          <a href="/docs" target="_blank" rel="noreferrer">
            Open API docs
          </a>
          <button type="button" onClick={resetDemo}>
            Reset demo state
          </button>
        </div>
      </header>

      <main>
        <section>
          <h2>1. Submit payment</h2>
          <form onSubmit={submitPayment}>
            <label>
              Card Number
              <input
                value={paymentPayload.card_number}
                onChange={(event) =>
                  setPaymentPayload((state) => ({ ...state, card_number: event.target.value }))
                }
                required
              />
            </label>
            <div className="grid">
              <label>
                Amount
                <input
                  type="number"
                  min="0.01"
                  step="0.01"
                  value={paymentPayload.amount}
                  onChange={(event) =>
                    setPaymentPayload((state) => ({
                      ...state,
                      amount: Number(event.target.value)
                    }))
                  }
                  required
                />
              </label>
              <label>
                Currency
                <input
                  value={paymentPayload.currency}
                  onChange={(event) =>
                    setPaymentPayload((state) => ({ ...state, currency: event.target.value }))
                  }
                  maxLength={3}
                  required
                />
              </label>
            </div>
            <label>
              Merchant
              <input
                value={paymentPayload.merchant}
                onChange={(event) =>
                  setPaymentPayload((state) => ({ ...state, merchant: event.target.value }))
                }
                required
              />
            </label>
            <div className="grid">
              <label>
                Channel
                <input
                  value={paymentPayload.channel ?? ""}
                  onChange={(event) =>
                    setPaymentPayload((state) => ({ ...state, channel: event.target.value }))
                  }
                />
              </label>
              <label>
                Device ID
                <input
                  value={paymentPayload.device_id ?? ""}
                  onChange={(event) =>
                    setPaymentPayload((state) => ({ ...state, device_id: event.target.value }))
                  }
                />
              </label>
            </div>
            <button type="submit" disabled={loading.payment}>
              {loading.payment ? "Submitting…" : "Simulate authorization"}
            </button>
          </form>
          <div className="panel">
            <h3>Decision result</h3>
            <pre data-testid="decision-result">
              {paymentResult ? JSON.stringify(paymentResult, null, 2) : "Awaiting submission."}
            </pre>
          </div>
        </section>

        <section>
          <h2>2. Inspect transaction & audit logs</h2>
          <form onSubmit={fetchTransaction}>
            <label>
              Transaction ID
              <input
                value={transactionLookup}
                onChange={(event) => setTransactionLookup(event.target.value)}
                placeholder="Paste an ID from step 1"
                required
              />
            </label>
            <button type="submit" disabled={loading.lookup}>
              {loading.lookup ? "Fetching…" : "Fetch details"}
            </button>
          </form>
          <div className="panel">
            <h3>Transaction record</h3>
            <pre data-testid="transaction-record">
              {transactionResult ? JSON.stringify(transactionResult, null, 2) : "No lookup yet."}
            </pre>
          </div>
          <div className="panel">
            <h3>Audit trail</h3>
            <pre data-testid="audit-trail">
              {audits.length
                ? JSON.stringify(audits, null, 2)
                : loading.audits
                  ? "Loading audits…"
                  : "No audit logs found."}
            </pre>
          </div>
        </section>

        <section>
          <h2>3. Platform metrics</h2>
          <p className="caption">Live stats produced by the SQL aggregation helpers.</p>
          <button type="button" disabled={loading.stats} onClick={refreshStats}>
            {loading.stats ? "Refreshing…" : "Refresh metrics"}
          </button>
          <div className="panel">
            <h3>Current stats</h3>
            <pre data-testid="stats-panel">
              {stats ? JSON.stringify(stats, null, 2) : "Gathering stats…"}
            </pre>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
