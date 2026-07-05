"use client";

import { useI18n } from "@/lib/i18n";
import type { FinalVerdict } from "@/lib/types";

import { Badge } from "./ui";

const TONE: Record<FinalVerdict, "green" | "red" | "blue" | "amber"> = {
  attractive: "green",
  avoid: "red",
  watchlist: "blue",
  uncertain: "amber",
};

export default function VerdictBadge({ verdict }: { verdict: FinalVerdict }) {
  const { t } = useI18n();
  return <Badge tone={TONE[verdict] ?? "amber"}>{t(`report.verdicts.${verdict}`)}</Badge>;
}
