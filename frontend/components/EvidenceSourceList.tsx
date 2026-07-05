"use client";

import { useI18n } from "@/lib/i18n";
import type { EvidenceSource } from "@/lib/types";

import { Badge, Card, CardBody, CardHeader } from "./ui";

export default function EvidenceSourceList({ sources }: { sources: EvidenceSource[] }) {
  const { t } = useI18n();
  if (!sources?.length) return null;
  return (
    <Card>
      <CardHeader>{t("report.evidence")}</CardHeader>
      <CardBody>
        <ul className="space-y-2">
          {sources.map((s, i) => (
            <li key={i} className="flex items-start justify-between gap-3 text-sm border-b border-slate-100 last:border-0 pb-2 last:pb-0">
              <div className="min-w-0">
                <span className="font-medium text-slate-800">{s.name}</span>
                <p className="text-xs text-slate-500">
                  {t("report.evidenceProvider")}: {s.provider}
                  {s.capability_id ? ` · ${s.capability_id}` : ""} · {t("report.evidenceRetrieved")}:{" "}
                  {new Date(s.retrieval_timestamp).toLocaleString()}
                </p>
                {s.note && <p className="text-xs text-slate-400 mt-0.5">{s.note}</p>}
              </div>
              {s.is_mock && <Badge tone="amber">{t("common.mockData")}</Badge>}
            </li>
          ))}
        </ul>
      </CardBody>
    </Card>
  );
}
