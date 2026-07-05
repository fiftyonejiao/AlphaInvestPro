"use client";

import { downloadFile } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import type { AnalysisReport } from "@/lib/types";

import { Button } from "./ui";

export default function ExportReportButton({ report }: { report: AnalysisReport }) {
  const { t } = useI18n();
  const stem = `${report.ticker}_${report.analysis_mode}`;
  return (
    <div className="flex gap-2">
      <Button
        variant="secondary"
        onClick={() => downloadFile(`${stem}.md`, report.final_memo_markdown, "text/markdown")}
      >
        {t("report.exportMarkdown")}
      </Button>
      <Button
        variant="secondary"
        onClick={() => downloadFile(`${stem}.json`, JSON.stringify(report, null, 2), "application/json")}
      >
        {t("report.exportJson")}
      </Button>
    </div>
  );
}
