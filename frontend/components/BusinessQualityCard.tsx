"use client";

import { useI18n } from "@/lib/i18n";

import { Card, CardBody, CardHeader, ScoreBar } from "./ui";

export default function BusinessQualityCard({
  quality,
}: {
  quality: { score: number; summary: string; evidence: string[] };
}) {
  const { t } = useI18n();
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <span>{t("report.businessQuality")}</span>
          <span className="text-brand-700">{quality.score}/10</span>
        </div>
      </CardHeader>
      <CardBody className="space-y-3">
        <ScoreBar score={quality.score} />
        <p className="text-sm text-slate-600">{quality.summary}</p>
        <ul className="space-y-1">
          {quality.evidence.map((e, i) => (
            <li key={i} className="text-sm text-slate-700 flex gap-2">
              <span className="text-emerald-600">＋</span> {e}
            </li>
          ))}
        </ul>
      </CardBody>
    </Card>
  );
}
