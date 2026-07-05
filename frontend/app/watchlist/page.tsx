"use client";

import { useEffect, useState } from "react";

import VerdictBadge from "@/components/VerdictBadge";
import { Button, Card, CardBody } from "@/components/ui";
import { api } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import type { WatchlistItem } from "@/lib/types";

export default function WatchlistPage() {
  const { t } = useI18n();
  const [items, setItems] = useState<WatchlistItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [ticker, setTicker] = useState("");
  const [note, setNote] = useState("");
  const [error, setError] = useState(false);

  const refresh = () =>
    api
      .listWatchlist()
      .then(setItems)
      .finally(() => setLoading(false));

  useEffect(() => {
    void refresh();
  }, []);

  const add = async () => {
    if (!ticker.trim()) return;
    setError(false);
    try {
      await api.addWatchlist(ticker.trim(), "", note.trim());
      setTicker("");
      setNote("");
      await refresh();
    } catch {
      setError(true);
    }
  };

  const remove = async (id: string) => {
    await api.removeWatchlist(id);
    await refresh();
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">{t("watchlist.title")}</h1>
        <p className="text-sm text-slate-500 mt-1">{t("watchlist.subtitle")}</p>
      </div>

      <Card>
        <CardBody className="pt-4">
          <div className="flex flex-wrap gap-2">
            <input
              value={ticker}
              onChange={(e) => setTicker(e.target.value.toUpperCase())}
              onKeyDown={(e) => e.key === "Enter" && add()}
              placeholder={t("watchlist.tickerPlaceholder")}
              className="px-3 py-2 rounded-lg border border-slate-300 text-sm w-40 focus:outline-none focus:ring-2 focus:ring-brand-500"
            />
            <input
              value={note}
              onChange={(e) => setNote(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && add()}
              placeholder={t("watchlist.notePlaceholder")}
              className="px-3 py-2 rounded-lg border border-slate-300 text-sm flex-1 min-w-48 focus:outline-none focus:ring-2 focus:ring-brand-500"
            />
            <Button onClick={add}>{t("watchlist.add")}</Button>
          </div>
          {error && <p className="text-sm text-rose-600 mt-2">{t("common.error")}</p>}
        </CardBody>
      </Card>

      <Card>
        <CardBody className="pt-4">
          {loading ? (
            <p className="text-sm text-slate-400">{t("common.loading")}</p>
          ) : items.length === 0 ? (
            <p className="text-sm text-slate-400">{t("watchlist.empty")}</p>
          ) : (
            <ul className="divide-y divide-slate-100">
              {items.map((item) => (
                <li key={item.id} className="flex items-center justify-between gap-3 py-3">
                  <div className="min-w-0">
                    <span className="font-medium text-slate-800 text-sm">
                      <span className="font-mono">{item.ticker}</span>
                      {item.company && <span className="text-slate-500"> · {item.company}</span>}
                    </span>
                    {item.note && <p className="text-xs text-slate-500 mt-0.5">{item.note}</p>}
                    <p className="text-xs text-slate-400 mt-0.5">
                      {t("watchlist.added")}: {new Date(item.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="flex items-center gap-3 shrink-0">
                    {item.last_verdict && (
                      <span className="flex items-center gap-1.5 text-xs text-slate-500">
                        {t("watchlist.lastVerdict")}: <VerdictBadge verdict={item.last_verdict} />
                      </span>
                    )}
                    <Button variant="danger" onClick={() => remove(item.id)}>
                      {t("watchlist.remove")}
                    </Button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </CardBody>
      </Card>
    </div>
  );
}
