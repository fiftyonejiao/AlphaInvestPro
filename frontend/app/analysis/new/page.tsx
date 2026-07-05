"use client";

import AnalysisStartForm from "@/components/AnalysisStartForm";
import { useI18n } from "@/lib/i18n";

export default function NewAnalysisPage() {
  const { t } = useI18n();
  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">{t("analysisNew.title")}</h1>
        <p className="text-sm text-slate-500 mt-1">{t("analysisNew.subtitle")}</p>
      </div>
      <AnalysisStartForm />
    </div>
  );
}
