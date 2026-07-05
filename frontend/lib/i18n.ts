"use client";

/**
 * Minimal i18n layer: exactly two locales (en, zh-CN) for MVP.
 * - Browser language is only the initial default.
 * - The user's manual choice persists in localStorage and always wins.
 * - No user-facing strings may be hardcoded in components; use t("key.path").
 */

import { createContext, useContext } from "react";

import en from "@/locales/en.json";
import zhCN from "@/locales/zh-CN.json";

export type Locale = "en" | "zh-CN";

export const LOCALES: Locale[] = ["en", "zh-CN"];
export const LOCALE_LABELS: Record<Locale, string> = { en: "English", "zh-CN": "简体中文" };

const DICTS: Record<Locale, Record<string, unknown>> = { en, "zh-CN": zhCN };

const STORAGE_KEY = "alphainvestpro.locale";

export function detectInitialLocale(): Locale {
  if (typeof window === "undefined") return "en";
  const stored = window.localStorage.getItem(STORAGE_KEY);
  if (stored === "en" || stored === "zh-CN") return stored;
  return window.navigator.language?.toLowerCase().startsWith("zh") ? "zh-CN" : "en";
}

export function persistLocale(locale: Locale): void {
  if (typeof window !== "undefined") window.localStorage.setItem(STORAGE_KEY, locale);
}

function lookup(dict: Record<string, unknown>, path: string): string | undefined {
  let node: unknown = dict;
  for (const part of path.split(".")) {
    if (typeof node !== "object" || node === null) return undefined;
    node = (node as Record<string, unknown>)[part];
  }
  return typeof node === "string" ? node : undefined;
}

export function translate(locale: Locale, key: string): string {
  return lookup(DICTS[locale], key) ?? lookup(DICTS.en, key) ?? key;
}

export interface I18nContextValue {
  locale: Locale;
  setLocale: (l: Locale) => void;
  t: (key: string) => string;
}

export const I18nContext = createContext<I18nContextValue>({
  locale: "en",
  setLocale: () => {},
  t: (key) => translate("en", key),
});

export function useI18n(): I18nContextValue {
  return useContext(I18nContext);
}
