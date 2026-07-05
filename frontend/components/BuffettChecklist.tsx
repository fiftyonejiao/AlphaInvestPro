"use client";

import { useI18n } from "@/lib/i18n";
import type { ChecklistItem } from "@/lib/types";

import { Badge, Card, CardBody, CardHeader } from "./ui";

export default function BuffettChecklist({ items }: { items: ChecklistItem[] }) {
  const { t } = useI18n();
  if (!items?.length) return null;
  return (
    <Card>
      <CardHeader>{t("report.checklist")}</CardHeader>
      <CardBody>
        <ul className="space-y-2">
          {items.map((item) => (
            <li key={item.key} className="flex items-start justify-between gap-3 text-sm">
              <div>
                <span className="font-medium text-slate-800">{item.label}</span>
                <p className="text-xs text-slate-500">{item.detail}</p>
              </div>
              <Badge tone={item.passed ? "green" : "red"}>
                {item.passed ? t("report.pass") : t("report.fail")}
              </Badge>
            </li>
          ))}
        </ul>
      </CardBody>
    </Card>
  );
}
