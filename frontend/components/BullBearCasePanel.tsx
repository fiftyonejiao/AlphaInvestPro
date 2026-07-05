"use client";

import { useI18n } from "@/lib/i18n";

import { Card, CardBody, CardHeader } from "./ui";

export default function BullBearCasePanel({ bull, bear }: { bull: string[]; bear: string[] }) {
  const { t } = useI18n();
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <Card>
        <CardHeader>
          <span className="text-emerald-700">▲ {t("report.bullCase")}</span>
        </CardHeader>
        <CardBody>
          <ul className="space-y-1.5">
            {bull.map((b, i) => (
              <li key={i} className="text-sm text-slate-700 flex gap-2">
                <span className="text-emerald-600 shrink-0">＋</span> {b}
              </li>
            ))}
          </ul>
        </CardBody>
      </Card>
      <Card>
        <CardHeader>
          <span className="text-rose-700">▼ {t("report.bearCase")}</span>
        </CardHeader>
        <CardBody>
          <ul className="space-y-1.5">
            {bear.map((b, i) => (
              <li key={i} className="text-sm text-slate-700 flex gap-2">
                <span className="text-rose-600 shrink-0">－</span> {b}
              </li>
            ))}
          </ul>
        </CardBody>
      </Card>
    </div>
  );
}
