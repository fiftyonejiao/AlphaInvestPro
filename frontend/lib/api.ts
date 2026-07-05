import type {
  AnalysisJob,
  AnalysisMode,
  ReportDetail,
  ReportSummary,
  SettingsPayload,
  WatchlistItem,
} from "./types";

export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const resp = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
  });
  if (!resp.ok) {
    throw new Error(`API ${resp.status}: ${path}`);
  }
  if (resp.status === 204) return undefined as T;
  return resp.json() as Promise<T>;
}

export const api = {
  createJob: (ticker: string, mode: AnalysisMode, language: string) =>
    request<AnalysisJob>("/api/analysis-jobs", {
      method: "POST",
      body: JSON.stringify({ ticker, analysis_mode: mode, language }),
    }),
  getJob: (jobId: string) => request<AnalysisJob>(`/api/analysis-jobs/${jobId}`),
  getJobReport: (jobId: string) => request<ReportDetail>(`/api/analysis-jobs/${jobId}/report`),
  jobEventsUrl: (jobId: string) => `${API_BASE}/api/analysis-jobs/${jobId}/events`,

  listReports: () => request<ReportSummary[]>("/api/reports"),
  getReport: (reportId: string) => request<ReportDetail>(`/api/reports/${reportId}`),

  listWatchlist: () => request<WatchlistItem[]>("/api/watchlist"),
  addWatchlist: (ticker: string, company = "", note = "") =>
    request<WatchlistItem>("/api/watchlist", {
      method: "POST",
      body: JSON.stringify({ ticker, company, note }),
    }),
  removeWatchlist: (itemId: string) =>
    request<void>(`/api/watchlist/${itemId}`, { method: "DELETE" }),

  getSettings: () => request<SettingsPayload>("/api/settings"),
  updateSettings: (values: Record<string, string>) =>
    request<SettingsPayload>("/api/settings", { method: "PUT", body: JSON.stringify({ values }) }),
};

export function downloadFile(filename: string, content: string, mime: string) {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
