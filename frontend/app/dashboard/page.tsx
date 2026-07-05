"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import VerdictBadge from "@/components/VerdictBadge";
import { Badge, Button, Card, CardBody, CardHeader } from "@/components/ui";
import { api } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import type { ReportSummary, SettingsPayload, WatchlistItem } from "@/lib/types";

export default function DashboardPage() {
  const { t } = useI18n();
  const [reports, setReports] = useState<ReportSummary[]>([]);
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);
  const [settings, setSettings] = useState<SettingsPayload | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.allSettled([api.listReports(), api.listWatchlist(), api.getSettings()]).then(
      ([r, w, s]) => {
        if (r.status === "fulfilled") setReports(r.value);
        if (w.status === "fulfilled") setWatchlist(w.value);
        if (s.status === "fulfilled") setSettings(s.value);
        setLoading(false);
      },
    );
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">{t("dashboard.title")}</h1>
          <p className="text-sm text-slate-500 mt-1">{t("dashboard.subtitle")}</p>
        </div>
        <Link href="/analysis/new">
          <Button>{t("dashboard.startAnalysis")}</Button>
        </Link>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardBody className="pt-4">
            <div className="text-xs text-slate-500">{t("dashboard.reportsCount")}</div>
            <div className="text-2xl font-bold text-slate-900 mt-1">{reports.length}</div>
          </CardBody>
        </Card>
        <Card>
          <CardBody className="pt-4">
            <div className="text-xs text-slate-500">{t("dashboard.watchlistCount")}</div>
            <div className="text-2xl font-bold text-slate-900 mt-1">{watchlist.length}</div>
          </CardBody>
        </Card>
        <Card>
          <CardBody className="pt-4">
            <div className="text-xs text-slate-500">{t("dashboard.dataMode")}</div>
            <div className="mt-2">
              {settings ? (
                <Badge tone={settings.qveris.configured ? "green" : "amber"}>
                  {settings.qveris.configured ? t("dashboard.live") : `${t("dashboard.mock")} · ${t("common.mockData")}`}
                </Badge>
              ) : (
                <span className="text-sm text-slate-400">…</span>
              )}
            </div>
          </CardBody>
        </Card>
        <Card>
          <CardBody className="pt-4">
            <div className="text-xs text-slate-500">{t("dashboard.llmMode")}</div>
            <div className="mt-2">
              {settings ? (
                <Badge tone={settings.deepseek.configured ? "green" : "amber"}>
                  {settings.deepseek.configured ? `${t("dashboard.live")} · ${settings.deepseek.model}` : t("dashboard.mock")}
                </Badge>
              ) : (
                <span className="text-sm text-slate-400">…</span>
              )}
            </div>
          </CardBody>
        </Card>
      </div>

      <Card>
        <CardHeader>{t("dashboard.recentReports")}</CardHeader>
        <CardBody>
          {loading ? (
            <p className="text-sm text-slate-400">{t("common.loading")}</p>
          ) : reports.length === 0 ? (
            <p className="text-sm text-slate-400">{t("dashboard.noReports")}</p>
          ) : (
            <ul className="divide-y divide-slate-100">
              {reports.slice(0, 8).map((r) => (
                <li key={r.id}>
                  <Link
                    href={`/reports/${r.id}`}
                    className="flex items-center justify-between gap-3 py-2.5 hover:bg-slate-50 rounded-lg px-2 -mx-2"
                  >
                    <div className="min-w-0">
                      <span className="font-medium text-slate-800 text-sm">
                        {r.company} <span className="text-slate-400 font-mono">({r.ticker})</span>
                      </span>
                      <p className="text-xs text-slate-400">
                        {t(`analysisNew.mode.${r.analysis_mode}`)} · {new Date(r.created_at).toLocaleString()}
                      </p>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      {r.is_mock_data && <Badge tone="amber">{t("common.mockData")}</Badge>}
                      <VerdictBadge verdict={r.final_verdict} />
                    </div>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </CardBody>
      </Card>
    </div>
  );
}
