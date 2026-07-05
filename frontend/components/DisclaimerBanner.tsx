"use client";

import { useI18n } from "@/lib/i18n";

export default function DisclaimerBanner() {
  const { t } = useI18n();
  return (
    <p className="text-xs text-slate-500 border-t border-slate-200 pt-4 mt-10 pb-6">
      {t("common.notAdvice")}
    </p>
  );
}
