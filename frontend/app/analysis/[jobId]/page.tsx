"use client";

import { useParams } from "next/navigation";
import { useEffect, useRef, useState } from "react";

import AnalysisTimeline from "@/components/AnalysisTimeline";
import ReportView from "@/components/ReportView";
import { Badge, Card, CardBody } from "@/components/ui";
import { api } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import type { AnalysisJob, AnalysisReport, JobEvent } from "@/lib/types";

export default function AnalysisJobPage() {
  const { t } = useI18n();
  const params = useParams<{ jobId: string }>();
  const jobId = params.jobId;

  const [job, setJob] = useState<AnalysisJob | null>(null);
  const [completedSteps, setCompletedSteps] = useState<Set<string>>(new Set());
  const [currentStep, setCurrentStep] = useState<string | null>(null);
  const [payloads, setPayloads] = useState<Record<string, Record<string, unknown>>>({});
  const [report, setReport] = useState<AnalysisReport | null>(null);
  const [failed, setFailed] = useState(false);
  const sourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!jobId) return;
    api.getJob(jobId).then(setJob).catch(() => setFailed(true));

    const source = new EventSource(api.jobEventsUrl(jobId));
    sourceRef.current = source;

    const finish = async () => {
      source.close();
      const fresh = await api.getJob(jobId);
      setJob(fresh);
      if (fresh.status === "completed") {
        const detail = await api.getJobReport(jobId);
        setReport(detail.report);
      } else if (fresh.status === "failed") {
        setFailed(true);
      }
    };

    source.onmessage = (msg) => {
      const event: JobEvent = JSON.parse(msg.data);
      if (event.event_type === "step_started" && event.step) {
        setCurrentStep(event.step);
      } else if (event.event_type === "step_completed" && event.step) {
        const step = event.step;
        setCompletedSteps((prev) => new Set(prev).add(step));
        setCurrentStep(null);
        if (event.payload) {
          setPayloads((prev) => ({ ...prev, [step]: event.payload as Record<string, unknown> }));
        }
      } else if (event.event_type === "job_completed" || event.event_type === "stream_end") {
        void finish();
      } else if (event.event_type === "job_failed") {
        setFailed(true);
        source.close();
      }
    };
    source.onerror = () => {
      // If the stream drops after completion, recover via polling once.
      void finish().catch(() => setFailed(true));
    };

    return () => source.close();
  }, [jobId]);

  if (report) {
    return <ReportView report={report} />;
  }

  return (
    <div className="max-w-2xl mx-auto space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">{t("analysis.title")}</h1>
          <p className="text-sm text-slate-500 mt-1 font-mono">
            {job ? `${job.ticker} · ${t(`analysisNew.mode.${job.analysis_mode}`)}` : `${t("analysis.job")} ${jobId}`}
          </p>
        </div>
        {job && (
          <Badge tone={job.status === "failed" ? "red" : job.status === "completed" ? "green" : "blue"}>
            {t(`analysis.status.${job.status}`)}
          </Badge>
        )}
      </div>

      {failed ? (
        <Card>
          <CardBody className="pt-4">
            <p className="text-sm text-rose-600">{t("analysis.failedJob")}</p>
            {job?.error && <p className="text-xs text-slate-400 mt-1 font-mono">{job.error}</p>}
          </CardBody>
        </Card>
      ) : (
        <AnalysisTimeline
          mode={job?.analysis_mode ?? "full_memo"}
          completedSteps={completedSteps}
          currentStep={currentStep}
          payloads={payloads}
        />
      )}
    </div>
  );
}
