"use client";

import { useI18n } from "@/lib/i18n";

import { Spinner } from "./ui";

export type StepState = "waiting" | "running" | "done";

export default function AgentStepCard({
  step,
  state,
  detail,
}: {
  step: string;
  state: StepState;
  detail?: string;
}) {
  const { t } = useI18n();
  const icon =
    state === "done" ? (
      <span className="h-6 w-6 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center text-xs">✓</span>
    ) : state === "running" ? (
      <span className="h-6 w-6 rounded-full bg-brand-50 flex items-center justify-center">
        <Spinner />
      </span>
    ) : (
      <span className="h-6 w-6 rounded-full bg-slate-100 text-slate-400 flex items-center justify-center text-xs">•</span>
    );

  const stateLabel =
    state === "done" ? t("analysis.stepDone") : state === "running" ? t("analysis.stepRunning") : t("analysis.stepWaiting");

  return (
    <div
      className={`flex items-start gap-3 px-4 py-3 rounded-lg border ${
        state === "running"
          ? "border-brand-300 bg-brand-50/50"
          : state === "done"
            ? "border-slate-200 bg-white"
            : "border-slate-100 bg-slate-50/50"
      }`}
    >
      {icon}
      <div className="min-w-0 flex-1">
        <div className="flex items-center justify-between gap-2">
          <span className={`text-sm font-medium ${state === "waiting" ? "text-slate-400" : "text-slate-800"}`}>
            {t(`analysis.step.${step}`)}
          </span>
          <span className="text-xs text-slate-400">{stateLabel}</span>
        </div>
        {detail && <p className="text-xs text-slate-500 mt-1">{detail}</p>}
      </div>
    </div>
  );
}
