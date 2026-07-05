"use client";

import { useEffect, useState } from "react";

import LanguageSwitcher from "@/components/LanguageSwitcher";
import { Badge, Button, Card, CardBody, CardHeader } from "@/components/ui";
import { api } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import type { SettingsPayload } from "@/lib/types";

const MODES = ["quick_screen", "full_memo", "risk_review", "valuation_check"];

export default function SettingsPage() {
  const { t } = useI18n();
  const [settings, setSettings] = useState<SettingsPayload | null>(null);
  const [defaultMode, setDefaultMode] = useState("full_memo");
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    api.getSettings().then((s) => {
      setSettings(s);
      setDefaultMode(s.values.default_analysis_mode ?? "full_memo");
    });
  }, []);

  const save = async () => {
    const updated = await api.updateSettings({ default_analysis_mode: defaultMode });
    setSettings(updated);
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">{t("settings.title")}</h1>
        <p className="text-sm text-slate-500 mt-1">{t("settings.subtitle")}</p>
      </div>

      <Card>
        <CardHeader>{t("settings.language")}</CardHeader>
        <CardBody>
          <LanguageSwitcher />
        </CardBody>
      </Card>

      <Card>
        <CardHeader>{t("settings.deepseek")}</CardHeader>
        <CardBody className="space-y-2">
          {settings ? (
            <>
              <div className="flex items-center gap-2">
                <Badge tone={settings.deepseek.configured ? "green" : "amber"}>
                  {settings.deepseek.configured ? t("settings.connected") : t("settings.mockMode")}
                </Badge>
              </div>
              <p className="text-sm text-slate-600">
                {t("settings.model")}: <code className="bg-slate-100 px-1.5 py-0.5 rounded text-xs">{settings.deepseek.model}</code>
              </p>
            </>
          ) : (
            <p className="text-sm text-slate-400">{t("common.loading")}</p>
          )}
        </CardBody>
      </Card>

      <Card>
        <CardHeader>{t("settings.qveris")}</CardHeader>
        <CardBody className="space-y-2">
          {settings ? (
            <>
              <div className="flex items-center gap-2">
                <Badge tone={settings.qveris.configured ? "green" : "amber"}>
                  {settings.qveris.configured ? t("settings.connected") : t("settings.mockMode")}
                </Badge>
              </div>
              <p className="text-sm text-slate-600">
                {t("settings.session")}: <code className="bg-slate-100 px-1.5 py-0.5 rounded text-xs">{settings.qveris.session_id}</code>
              </p>
            </>
          ) : (
            <p className="text-sm text-slate-400">{t("common.loading")}</p>
          )}
        </CardBody>
      </Card>

      <Card>
        <CardHeader>{t("settings.defaultMode")}</CardHeader>
        <CardBody className="space-y-3">
          <select
            value={defaultMode}
            onChange={(e) => setDefaultMode(e.target.value)}
            className="px-3 py-2 rounded-lg border border-slate-300 text-sm bg-white"
          >
            {MODES.map((m) => (
              <option key={m} value={m}>
                {t(`analysisNew.mode.${m}`)}
              </option>
            ))}
          </select>
          <div className="flex items-center gap-3">
            <Button onClick={save}>{t("settings.save")}</Button>
            {saved && <span className="text-sm text-emerald-600">{t("settings.saved")}</span>}
          </div>
        </CardBody>
      </Card>

      <p className="text-xs text-slate-500">{t("settings.keysNote")}</p>
    </div>
  );
}
