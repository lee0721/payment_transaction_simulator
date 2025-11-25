import {
  DecisionAuditResponse,
  PaymentRequest,
  PaymentResponse,
  StatsResponse,
  TransactionResponse
} from "../types/api";

const resolveDefaultBase = () => {
  if (typeof window === "undefined") {
    return "http://localhost:8000";
  }

  const { protocol, hostname, port } = window.location;
  const apiPort = "8000";
  const inferredHost = `${protocol}//${hostname}:${apiPort}`;

  // When the frontend runs on the Vite dev server / nginx (4173 or 80),
  // talk to the FastAPI container on port 8000.
  if (port === "4173" || (port === "" && protocol === "http:" && hostname === "localhost")) {
    return inferredHost;
  }

  return window.location.origin;
};

const API_BASE = (
  import.meta.env.VITE_API_BASE?.trim() || resolveDefaultBase()
).replace(/\/$/, "");

type HttpMethod = "GET" | "POST" | "DELETE";

async function request<T>(path: string, method: HttpMethod, body?: unknown): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`API error (${response.status}): ${errorBody}`);
  }

  return response.json() as Promise<T>;
}

export const useApiClient = () => ({
  postPayment: (payload: PaymentRequest) => request<PaymentResponse>("/payment", "POST", payload),
  getTransaction: (id: string) => request<TransactionResponse>(`/transaction/${id}`, "GET"),
  getStats: () => request<StatsResponse>("/stats", "GET"),
  getAuditLogs: (transactionId: string) =>
    request<DecisionAuditResponse[]>(`/audit/${transactionId}`, "GET"),
  resetDemo: () => request<StatsResponse>("/admin/reset", "DELETE")
});
