export type AnalysisMode = "quick_screen" | "full_memo" | "risk_review" | "valuation_check";
export type FinalVerdict = "avoid" | "watchlist" | "attractive" | "uncertain";
export type JobStatus = "pending" | "running" | "completed" | "failed";

export interface AnalysisJob {
  id: string;
  ticker: string;
  company: string;
  analysis_mode: AnalysisMode;
  language: string;
  status: JobStatus;
  current_step: string | null;
  error: string | null;
  report_id: string | null;
  is_mock_data: boolean;
  created_at: string;
  updated_at: string;
}

export interface JobEvent {
  seq?: number;
  event_type: string;
  step?: string | null;
  payload?: Record<string, unknown>;
  status?: string;
  report_id?: string | null;
  created_at?: string;
}

export interface ChecklistItem {
  key: string;
  label: string;
  passed: boolean;
  detail: string;
}

export interface ValuationAssumption {
  name: string;
  value: string;
  source: string;
}

export interface Valuation {
  method: string;
  fair_value_range: { low: number; base: number; high: number };
  assumptions: ValuationAssumption[];
}

export interface EvidenceSource {
  name: string;
  provider: string;
  capability_id: string | null;
  retrieval_timestamp: string;
  source_timestamp: string | null;
  is_mock: boolean;
  note: string;
}

export interface AnalysisReport {
  company: string;
  ticker: string;
  analysis_mode: AnalysisMode;
  final_verdict: FinalVerdict;
  confidence: number;
  business_quality: { score: number; summary: string; evidence: string[] };
  moat: { score: number; summary: string; risks: string[] };
  valuation: Valuation;
  risk_review: { top_risks: string[]; thesis_killers: string[]; inversion_question: string };
  bull_case: string[];
  bear_case: string[];
  final_memo_markdown: string;
  checklist: ChecklistItem[];
  evidence_sources: EvidenceSource[];
  is_mock_data: boolean;
  is_mock_llm: boolean;
  is_incomplete: boolean;
  language: string;
  generated_at: string;
}

export interface ReportDetail {
  id: string;
  job_id: string;
  created_at: string;
  report: AnalysisReport;
}

export interface ReportSummary {
  id: string;
  job_id: string;
  ticker: string;
  company: string;
  analysis_mode: string;
  final_verdict: FinalVerdict;
  confidence: number;
  is_mock_data: boolean;
  created_at: string;
}

export interface WatchlistItem {
  id: string;
  ticker: string;
  company: string;
  note: string;
  last_verdict: FinalVerdict | null;
  created_at: string;
}

export interface ProviderStatus {
  configured: boolean;
  mode: "live" | "mock";
}

export interface DeepSeekStatus extends ProviderStatus {
  model: string;
}

export interface QverisStatus extends ProviderStatus {
  base_url: string;
  session_id: string;
}

export interface SettingsPayload {
  values: Record<string, string>;
  deepseek: DeepSeekStatus;
  qveris: QverisStatus;
}
