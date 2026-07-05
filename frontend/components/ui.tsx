"use client";

import { ReactNode } from "react";

export function Card({ children, className = "" }: { children: ReactNode; className?: string }) {
  return (
    <div className={`bg-white rounded-xl border border-slate-200 shadow-sm ${className}`}>
      {children}
    </div>
  );
}

export function CardHeader({ children }: { children: ReactNode }) {
  return <div className="px-5 pt-4 pb-2 font-semibold text-slate-800">{children}</div>;
}

export function CardBody({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <div className={`px-5 pb-4 ${className}`}>{children}</div>;
}

type BadgeTone = "neutral" | "green" | "red" | "amber" | "blue" | "purple";

const TONES: Record<BadgeTone, string> = {
  neutral: "bg-slate-100 text-slate-700",
  green: "bg-emerald-100 text-emerald-800",
  red: "bg-rose-100 text-rose-800",
  amber: "bg-amber-100 text-amber-800",
  blue: "bg-blue-100 text-blue-800",
  purple: "bg-violet-100 text-violet-800",
};

export function Badge({ children, tone = "neutral" }: { children: ReactNode; tone?: BadgeTone }) {
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${TONES[tone]}`}>
      {children}
    </span>
  );
}

export function Button({
  children,
  onClick,
  disabled,
  variant = "primary",
  type = "button",
  className = "",
}: {
  children: ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  variant?: "primary" | "secondary" | "danger";
  type?: "button" | "submit";
  className?: string;
}) {
  const styles = {
    primary: "bg-brand-600 hover:bg-brand-700 text-white",
    secondary: "bg-white hover:bg-slate-50 text-slate-700 border border-slate-300",
    danger: "bg-white hover:bg-rose-50 text-rose-600 border border-rose-300",
  }[variant];
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${styles} ${className}`}
    >
      {children}
    </button>
  );
}

export function Spinner() {
  return (
    <span
      className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-slate-300 border-t-brand-600"
      role="status"
      aria-hidden
    />
  );
}

export function ScoreBar({ score }: { score: number }) {
  const pct = Math.max(0, Math.min(100, score * 10));
  const tone = score >= 7.5 ? "bg-emerald-500" : score >= 5 ? "bg-amber-500" : "bg-rose-500";
  return (
    <div className="w-full bg-slate-100 rounded-full h-2">
      <div className={`h-2 rounded-full ${tone}`} style={{ width: `${pct}%` }} />
    </div>
  );
}
