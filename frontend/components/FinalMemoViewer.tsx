"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { useI18n } from "@/lib/i18n";

import { Card, CardBody, CardHeader } from "./ui";

export default function FinalMemoViewer({ markdown }: { markdown: string }) {
  const { t } = useI18n();
  return (
    <Card>
      <CardHeader>{t("report.finalMemo")}</CardHeader>
      <CardBody>
        <div className="memo-markdown text-slate-800">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{markdown}</ReactMarkdown>
        </div>
      </CardBody>
    </Card>
  );
}
