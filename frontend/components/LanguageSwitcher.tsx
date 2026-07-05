"use client";

import { LOCALE_LABELS, LOCALES, useI18n } from "@/lib/i18n";

export default function LanguageSwitcher() {
  const { locale, setLocale } = useI18n();
  return (
    <div className="flex items-center rounded-lg border border-slate-300 overflow-hidden text-xs font-medium" data-testid="language-switcher">
      {LOCALES.map((l) => (
        <button
          key={l}
          onClick={() => setLocale(l)}
          className={`px-2.5 py-1.5 transition-colors ${
            locale === l ? "bg-brand-600 text-white" : "bg-white text-slate-600 hover:bg-slate-50"
          }`}
          aria-pressed={locale === l}
        >
          {LOCALE_LABELS[l]}
        </button>
      ))}
    </div>
  );
}
