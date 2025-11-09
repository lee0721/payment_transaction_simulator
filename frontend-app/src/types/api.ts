export interface TransactionFeatures {
  spending_velocity: number;
  device_trust_score: number;
  ip_risk_score: number;
}

export interface PaymentRequest {
  card_number: string;
  amount: number;
  currency: string;
  merchant: string;
  channel?: string | null;
  device_id?: string | null;
}

export interface RiskDecision {
  status: string;
  score: number;
  reason?: string | null;
  latency_ms: number;
  features: TransactionFeatures;
}

export interface PaymentResponse extends RiskDecision {
  transaction_id: string;
}

export interface TransactionResponse {
  id: string;
  card_last4: string;
  amount: number;
  merchant: string;
  status: string;
  risk_flag?: string | null;
  created_at: string;
}

export interface StatsResponse {
  total: number;
  approved: number;
  declined: number;
  approval_rate: number;
  avg_amount: number;
  p95_latency?: number | null;
}

export interface DecisionAuditResponse {
  id: string;
  transaction_id: string;
  request_payload: Record<string, unknown>;
  decision_payload: RiskDecision;
  latency_ms: number;
  created_at: string;
}
