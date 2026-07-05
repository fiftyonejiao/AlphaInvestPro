"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { useI18n } from "@/lib/i18n";

import DeepSeekStatusBadge from "./DeepSeekStatusBadge";
import LanguageSwitcher from "./LanguageSwitcher";

const LINKS = [
  { href: "/dashboard", key: "nav.dashboard" },
  { href: "/analysis/new", key: "nav.newAnalysis" },
  { href: "/watchlist", key: "nav.watchlist" },
  { href: "/reports", key: "nav.reports" },
  { href: "/settings", key: "nav.settings" },
];

export default function NavBar() {
  const { t } = useI18n();
  const pathname = usePathname();
  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
      <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between gap-4">
        <div className="flex items-center gap-6 min-w-0">
          <Link href="/dashboard" className="font-bold text-brand-700 whitespace-nowrap">
            {t("app.name")}
          </Link>
          <nav className="flex items-center gap-1 overflow-x-auto">
            {LINKS.map((l) => {
              const active = pathname === l.href || (l.href !== "/dashboard" && pathname?.startsWith(l.href));
              return (
                <Link
                  key={l.href}
                  href={l.href}
                  className={`px-3 py-1.5 rounded-lg text-sm whitespace-nowrap transition-colors ${
                    active ? "bg-brand-50 text-brand-700 font-medium" : "text-slate-600 hover:bg-slate-100"
                  }`}
                >
                  {t(l.key)}
                </Link>
              );
            })}
          </nav>
        </div>
        <div className="flex items-center gap-3 shrink-0">
          <DeepSeekStatusBadge />
          <LanguageSwitcher />
        </div>
      </div>
    </header>
  );
}
