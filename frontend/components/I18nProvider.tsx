"use client";

import { ReactNode, useCallback, useEffect, useMemo, useState } from "react";

import { detectInitialLocale, I18nContext, Locale, persistLocale, translate } from "@/lib/i18n";

export default function I18nProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>("en");

  useEffect(() => {
    setLocaleState(detectInitialLocale());
  }, []);

  const setLocale = useCallback((l: Locale) => {
    setLocaleState(l);
    persistLocale(l);
  }, []);

  const value = useMemo(
    () => ({ locale, setLocale, t: (key: string) => translate(locale, key) }),
    [locale, setLocale],
  );

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}
