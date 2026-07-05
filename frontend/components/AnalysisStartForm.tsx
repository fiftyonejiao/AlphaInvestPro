"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { api } from "@/lib/api";
import { Locale, LOCALE_LABELS, LOCALES, useI18n } from "@/lib/i18n";
import type { AnalysisMode } from "@/lib/types";

import { Button, Card, CardBody, Spinner } from "./ui";

const MODES: AnalysisMode[] = ["quick_screen", "full_memo", "risk_review", "valuation_check"];

export default function AnalysisStartForm() {
  const { t, locale } = useI18n();
  const router = useRouter();
  const [ticker, setTicker] = useState("");
  const [mode, setMode] = useState<AnalysisMode>("full_memo");
  const [reportLanguage, setReportLanguage] = useState<Locale>(locale);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async () => {
    if (!ticker.trim()) {
      setError(t("analysisNew.tickerRequired"));
      return;
    }
    setError(null);
    setSubmitting(true);
    try {
      const job = await api.createJob(ticker.trim(), mode, reportLanguage);
      router.push(`/analysis/${job.id}`);
    } catch {
      setError(t("common.error"));
      setSubmitting(false);
    }
  };

  return (
    <Card>
      <CardBody className="pt-5 space-y-5">
        <div>
          <label htmlFor="ticker" className="block text-sm font-medium text-slate-700 mb-1">
            {t("analysisNew.tickerLabel")}
          </label>
          <input
            id="ticker"
            value={ticker}
            onChange={(e) => setTicker(e.target.value.toUpperCase())}
            onKeyDown={(e) => e.key === "Enter" && submit()}
            placeholder={t("analysisNew.tickerPlaceholder")}
            className="w-full px-3 py-2 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm"
          />
        </div>

        <div>
          <span className="block text-sm font-medium text-slate-700 mb-2">{t("analysisNew.modeLabel")}</span>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {MODES.map((m) => (
              <button
                key={m}
                type="button"
                onClick={() => setMode(m)}
                className={`text-left px-3 py-2.5 rounded-lg border transition-colors ${
                  mode === m
                    ? "border-brand-600 bg-brand-50 ring-1 ring-brand-600"
                    : "border-slate-200 hover:border-slate-300 bg-white"
                }`}
              >
                <span className="block text-sm font-medium text-slate-800">{t(`analysisNew.mode.${m}`)}</span>
                <span className="block text-xs text-slate-500 mt-0.5">{t(`analysisNew.modeDesc.${m}`)}</span>
              </button>
            ))}
          </div>
        </div>

        <div>
          <label htmlFor="report-language" className="block text-sm font-medium text-slate-700 mb-1">
            {t("analysisNew.reportLanguageLabel")}
          </label>
          <select
            id="report-language"
            value={reportLanguage}
            onChange={(e) => setReportLanguage(e.target.value as Locale)}
            className="px-3 py-2 rounded-lg border border-slate-300 text-sm bg-white"
          >
            {LOCALES.map((l) => (
              <option key={l} value={l}>
                {LOCALE_LABELS[l]}
              </option>
            ))}
          </select>
        </div>

        {error && <p className="text-sm text-rose-600">{error}</p>}

        <Button onClick={submit} disabled={submitting} className="w-full sm:w-auto">
          {submitting ? (
            <span className="inline-flex items-center gap-2">
              <Spinner /> {t("analysisNew.starting")}
            </span>
          ) : (
            t("analysisNew.start")
          )}
        </Button>
      </CardBody>
    </Card>
  );
}
