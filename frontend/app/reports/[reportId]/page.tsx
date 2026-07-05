"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import ReportView from "@/components/ReportView";
import { api } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import type { AnalysisReport } from "@/lib/types";

export default function ReportDetailPage() {
  const { t } = useI18n();
  const params = useParams<{ reportId: string }>();
  const [report, setReport] = useState<AnalysisReport | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (!params.reportId) return;
    api
      .getReport(params.reportId)
      .then((d) => setReport(d.report))
      .catch(() => setError(true));
  }, [params.reportId]);

  return (
    <div className="space-y-4">
      <Link href="/reports" className="text-sm text-brand-700 hover:underline">
        ← {t("common.back")}
      </Link>
      {error ? (
        <p className="text-sm text-rose-600">{t("common.error")}</p>
      ) : report ? (
        <ReportView report={report} />
      ) : (
        <p className="text-sm text-slate-400">{t("common.loading")}</p>
      )}
    </div>
  );
}
