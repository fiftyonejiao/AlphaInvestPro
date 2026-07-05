"use client";

import { useEffect, useState } from "react";

import { api } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import type { DeepSeekStatus } from "@/lib/types";

import { Badge } from "./ui";

export default function DeepSeekStatusBadge() {
  const { t } = useI18n();
  const [status, setStatus] = useState<DeepSeekStatus | null>(null);

  useEffect(() => {
    api
      .getSettings()
      .then((s) => setStatus(s.deepseek))
      .catch(() => setStatus(null));
  }, []);

  if (!status) return null;
  return (
    <Badge tone={status.configured ? "green" : "amber"}>
      <span className={`h-1.5 w-1.5 rounded-full ${status.configured ? "bg-emerald-500" : "bg-amber-500"}`} />
      DeepSeek · {status.configured ? status.model : t("settings.mockMode")}
    </Badge>
  );
}
