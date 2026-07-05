"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import VerdictBadge from "@/components/VerdictBadge";
import { Badge, Card, CardBody } from "@/components/ui";
import { api } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import type { ReportSummary } from "@/lib/types";

export default function ReportsPage() {
  const { t } = useI18n();
  const [reports, setReports] = useState<ReportSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .listReports()
      .then(setReports)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">{t("reports.title")}</h1>
        <p className="text-sm text-slate-500 mt-1">{t("reports.subtitle")}</p>
      </div>

      <Card>
        <CardBody className="pt-4">
          {loading ? (
            <p className="text-sm text-slate-400">{t("common.loading")}</p>
          ) : reports.length === 0 ? (
            <p className="text-sm text-slate-400">{t("reports.empty")}</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-xs text-slate-500 border-b border-slate-200">
                    <th className="py-2 pr-3">{t("reports.company")}</th>
                    <th className="py-2 pr-3">{t("reports.mode")}</th>
                    <th className="py-2 pr-3">{t("reports.verdict")}</th>
                    <th className="py-2 pr-3">{t("reports.confidence")}</th>
                    <th className="py-2">{t("reports.date")}</th>
                  </tr>
                </thead>
                <tbody>
                  {reports.map((r) => (
                    <tr key={r.id} className="border-b border-slate-100 last:border-0 hover:bg-slate-50">
                      <td className="py-2.5 pr-3">
                        <Link href={`/reports/${r.id}`} className="font-medium text-brand-700 hover:underline">
                          {r.company} <span className="text-slate-400 font-mono">({r.ticker})</span>
                        </Link>
                        {r.is_mock_data && (
                          <span className="ml-2">
                            <Badge tone="amber">{t("common.mockData")}</Badge>
                          </span>
                        )}
                      </td>
                      <td className="py-2.5 pr-3 text-slate-600">{t(`analysisNew.mode.${r.analysis_mode}`)}</td>
                      <td className="py-2.5 pr-3">
                        <VerdictBadge verdict={r.final_verdict} />
                      </td>
                      <td className="py-2.5 pr-3 text-slate-600">{(r.confidence * 100).toFixed(0)}%</td>
                      <td className="py-2.5 text-slate-500 text-xs">{new Date(r.created_at).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardBody>
      </Card>
    </div>
  );
}
