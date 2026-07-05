"use client";

import { useI18n } from "@/lib/i18n";

import AgentStepCard, { StepState } from "./AgentStepCard";
import { Card, CardBody, CardHeader } from "./ui";

const STEPS_BY_MODE: Record<string, string[]> = {
  quick_screen: ["input_normalization", "identification", "quick_screen", "final_memo"],
  full_memo: [
    "input_normalization", "identification", "quick_screen", "business_quality",
    "moat", "management", "valuation", "inversion_risk", "bull_bear", "final_memo",
  ],
  risk_review: ["input_normalization", "identification", "quick_screen", "inversion_risk", "bull_bear", "final_memo"],
  valuation_check: ["input_normalization", "identification", "quick_screen", "valuation", "final_memo"],
};

function stepDetail(step: string, payload: Record<string, unknown> | undefined, t: (k: string) => string): string | undefined {
  if (!payload) return undefined;
  switch (step) {
    case "identification":
      return payload.company ? `${payload.company} — ${payload.sector ?? ""}` : undefined;
    case "quick_screen":
      return payload.passed !== undefined ? `${payload.passed}/${payload.total} ${t("analysis.passed")}` : undefined;
    case "business_quality":
    case "moat":
      return payload.score !== undefined ? `${t("report.score")}: ${payload.score}/10` : undefined;
    case "valuation": {
      const range = payload.fair_value_range as { low: number; base: number; high: number } | undefined;
      return range ? `${range.low} / ${range.base} / ${range.high}` : undefined;
    }
    case "final_memo":
      return payload.verdict ? `${t("report.verdict")}: ${t(`report.verdicts.${payload.verdict}`)}` : undefined;
    default:
      return undefined;
  }
}

export default function AnalysisTimeline({
  mode,
  completedSteps,
  currentStep,
  payloads,
}: {
  mode: string;
  completedSteps: Set<string>;
  currentStep: string | null;
  payloads: Record<string, Record<string, unknown>>;
}) {
  const { t } = useI18n();
  const steps = STEPS_BY_MODE[mode] ?? STEPS_BY_MODE.full_memo;
  return (
    <Card>
      <CardHeader>{t("analysis.timelineTitle")}</CardHeader>
      <CardBody className="space-y-2">
        {steps.map((step) => {
          const state: StepState = completedSteps.has(step)
            ? "done"
            : currentStep === step
              ? "running"
              : "waiting";
          return (
            <AgentStepCard
              key={step}
              step={step}
              state={state}
              detail={stepDetail(step, payloads[step], t)}
            />
          );
        })}
      </CardBody>
    </Card>
  );
}
