"use client";

import { useState } from "react";

import { api } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import type { AnalysisReport } from "@/lib/types";

import BuffettChecklist from "./BuffettChecklist";
import BullBearCasePanel from "./BullBearCasePanel";
import BusinessQualityCard from "./BusinessQualityCard";
import EvidenceSourceList from "./EvidenceSourceList";
import ExportReportButton from "./ExportReportButton";
import FinalMemoViewer from "./FinalMemoViewer";
import MoatScoreCard from "./MoatScoreCard";
import RiskInversionPanel from "./RiskInversionPanel";
import ValuationAssumptionsTable from "./ValuationAssumptionsTable";
import VerdictBadge from "./VerdictBadge";
import { Badge, Button } from "./ui";

export default function ReportView({ report }: { report: AnalysisReport }) {
  const { t } = useI18n();
  const [added, setAdded] = useState(false);

  const addToWatchlist = async () => {
    try {
      await api.addWatchlist(report.ticker, report.company);
      setAdded(true);
    } catch {
      /* surface nothing fatal; button stays enabled */
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">
            {report.company} <span className="text-slate-400 font-mono text-lg">({report.ticker})</span>
          </h1>
          <div className="flex flex-wrap items-center gap-2 mt-2">
            <span className="text-sm text-slate-500">{t("report.verdict")}:</span>
            <VerdictBadge verdict={report.final_verdict} />
            <span className="text-sm text-slate-500 ml-2">
              {t("report.confidence")}: {(report.confidence * 100).toFixed(0)}%
            </span>
            {report.is_mock_data && <Badge tone="amber">{t("common.mockData")}</Badge>}
            {report.is_mock_llm && <Badge tone="amber">{t("common.mockLlm")}</Badge>}
            {report.is_incomplete && <Badge tone="red">{t("common.incomplete")}</Badge>}
          </div>
        </div>
        <div className="flex flex-wrap gap-2 items-center">
          <ExportReportButton report={report} />
          <Button onClick={addToWatchlist} disabled={added}>
            {added ? t("report.addedToWatchlist") : t("report.addToWatchlist")}
          </Button>
        </div>
      </div>

      <BuffettChecklist items={report.checklist} />
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <BusinessQualityCard quality={report.business_quality} />
        <MoatScoreCard moat={report.moat} />
      </div>
      <ValuationAssumptionsTable valuation={report.valuation} />
      <RiskInversionPanel risk={report.risk_review} />
      <BullBearCasePanel bull={report.bull_case} bear={report.bear_case} />
      <FinalMemoViewer markdown={report.final_memo_markdown} />
      <EvidenceSourceList sources={report.evidence_sources} />
    </div>
  );
}
