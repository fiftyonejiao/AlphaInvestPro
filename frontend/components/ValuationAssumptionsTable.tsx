"use client";

import { useI18n } from "@/lib/i18n";
import type { Valuation } from "@/lib/types";

import { Badge, Card, CardBody, CardHeader } from "./ui";

export default function ValuationAssumptionsTable({ valuation }: { valuation: Valuation }) {
  const { t } = useI18n();
  const r = valuation.fair_value_range;
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <span>{t("report.valuation")}</span>
          <Badge tone="blue">{valuation.method}</Badge>
        </div>
      </CardHeader>
      <CardBody className="space-y-4">
        <div>
          <span className="text-xs font-semibold text-slate-500 uppercase">{t("report.fairValueRange")}</span>
          <div className="grid grid-cols-3 gap-2 mt-2">
            {[
              { label: t("report.low"), value: r.low, tone: "text-slate-600" },
              { label: t("report.base"), value: r.base, tone: "text-brand-700 font-semibold" },
              { label: t("report.high"), value: r.high, tone: "text-slate-600" },
            ].map((cell) => (
              <div key={cell.label} className="bg-slate-50 rounded-lg px-3 py-2 text-center">
                <div className="text-xs text-slate-500">{cell.label}</div>
                <div className={`text-lg ${cell.tone}`}>{cell.value.toLocaleString()}</div>
              </div>
            ))}
          </div>
        </div>
        <div>
          <span className="text-xs font-semibold text-slate-500 uppercase">{t("report.assumptions")}</span>
          <div className="overflow-x-auto mt-2">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs text-slate-500 border-b border-slate-200">
                  <th className="py-2 pr-3">{t("report.assumptionName")}</th>
                  <th className="py-2 pr-3">{t("report.assumptionValue")}</th>
                  <th className="py-2">{t("report.assumptionSource")}</th>
                </tr>
              </thead>
              <tbody>
                {valuation.assumptions.map((a, i) => (
                  <tr key={i} className="border-b border-slate-100 last:border-0">
                    <td className="py-2 pr-3 text-slate-800">{a.name}</td>
                    <td className="py-2 pr-3 text-slate-600 font-mono text-xs">{a.value}</td>
                    <td className="py-2 text-slate-500 text-xs">{a.source}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </CardBody>
    </Card>
  );
}
