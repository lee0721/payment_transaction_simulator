import {
  DecisionAuditResponse,
  PaymentRequest,
  PaymentResponse,
  StatsResponse,
  TransactionResponse
} from "../types/api";

const resolveBaseUrl = () => {
  if (typeof window !== "undefined") {
    return (window.__API_BASE__ as string | undefined) ?? window.location.origin;
  }
  return __API_BASE__;
};

const API_BASE = (import.meta.env.VITE_API_BASE ?? resolveBaseUrl()).replace(/\/$/, "");

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
