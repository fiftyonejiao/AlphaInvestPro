"use client";

import { useI18n } from "@/lib/i18n";

import { Card, CardBody, CardHeader } from "./ui";

export default function RiskInversionPanel({
  risk,
}: {
  risk: { top_risks: string[]; thesis_killers: string[]; inversion_question: string };
}) {
  const { t } = useI18n();
  return (
    <Card>
      <CardHeader>{t("report.riskReview")}</CardHeader>
      <CardBody className="space-y-4">
        <div>
          <span className="text-xs font-semibold text-slate-500 uppercase">{t("report.topRisks")}</span>
          <ul className="mt-1 space-y-1">
            {risk.top_risks.map((r, i) => (
              <li key={i} className="text-sm text-slate-700 flex gap-2">
                <span className="text-amber-600">⚠</span> {r}
              </li>
            ))}
          </ul>
        </div>
        <div>
          <span className="text-xs font-semibold text-slate-500 uppercase">{t("report.thesisKillers")}</span>
          <ul className="mt-1 space-y-1">
            {risk.thesis_killers.map((r, i) => (
              <li key={i} className="text-sm text-slate-700 flex gap-2">
                <span className="text-rose-600">✖</span> {r}
              </li>
            ))}
          </ul>
        </div>
        <div className="bg-violet-50 border border-violet-200 rounded-lg px-3 py-2">
          <span className="text-xs font-semibold text-violet-600 uppercase">{t("report.inversionQuestion")}</span>
          <p className="text-sm text-violet-900 mt-1 italic">{risk.inversion_question}</p>
        </div>
      </CardBody>
    </Card>
  );
}
