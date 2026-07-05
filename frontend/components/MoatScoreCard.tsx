"use client";

import { useI18n } from "@/lib/i18n";

import { Card, CardBody, CardHeader, ScoreBar } from "./ui";

export default function MoatScoreCard({
  moat,
}: {
  moat: { score: number; summary: string; risks: string[] };
}) {
  const { t } = useI18n();
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <span>{t("report.moat")}</span>
          <span className="text-brand-700">{moat.score}/10</span>
        </div>
      </CardHeader>
      <CardBody className="space-y-3">
        <ScoreBar score={moat.score} />
        <p className="text-sm text-slate-600">{moat.summary}</p>
        <div>
          <span className="text-xs font-semibold text-slate-500 uppercase">{t("report.moatRisks")}</span>
          <ul className="mt-1 space-y-1">
            {moat.risks.map((r, i) => (
              <li key={i} className="text-sm text-slate-700 flex gap-2">
                <span className="text-amber-600">⚠</span> {r}
              </li>
            ))}
          </ul>
        </div>
      </CardBody>
    </Card>
  );
}
