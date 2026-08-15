import { useState } from "react";

import { useAlerts } from "../api/queries";
import type { Alert } from "../api/types";
import { STATS, displayName } from "../lib/pokemon";

/** Newest change already dismissed. No read-state on the server, so it lives here. */
const watermarkKey = (userId: number) => `ptb:alerts-seen:${userId}`;

const fieldLabel = (field: string) =>
  STATS.find((stat) => stat.key === field)?.label ?? field;

const describe = (alert: Alert) =>
  alert.changes
    .map(
      ({ field, from, to }) =>
        `${fieldLabel(field)} ${from ?? "none"} → ${to ?? "none"}`,
    )
    .join(", ");

export function AlertBanner({ userId }: { userId: number }) {
  const alerts = useAlerts();
  const [watermark, setWatermark] = useState(
    () => localStorage.getItem(watermarkKey(userId)) ?? "",
  );

  const unseen = (alerts.data ?? []).filter(
    (alert) =>
      Date.parse(alert.detected_at) > Date.parse(watermark || "1970-01-01"),
  );
  if (unseen.length === 0) return null;

  const dismiss = () => {
    // Watermark, not a flag: a later sync writes a newer detected_at, so the banner returns.
    // unseen[0] is newest — the API returns alerts ordered by detected_at desc.
    const newest = unseen[0];
    localStorage.setItem(watermarkKey(userId), newest.detected_at);
    setWatermark(newest.detected_at);
  };

  return (
    <div className="flex items-start gap-3 border-b border-amber-200 bg-amber-50 px-4 py-2 text-sm">
      <span aria-hidden>⚠</span>
      <ul className="grow space-y-0.5">
        {unseen.map((alert) => (
          <li
            key={`${alert.pokemon.id}-${alert.detected_at}`}
            className="text-amber-900"
          >
            <strong className="font-semibold">
              {displayName(alert.pokemon.name)}
            </strong>{" "}
            changed: {describe(alert)}
          </li>
        ))}
      </ul>
      <button
        type="button"
        onClick={dismiss}
        className="shrink-0 rounded px-2 text-amber-700 hover:bg-amber-100"
        aria-label="Dismiss alerts"
      >
        ×
      </button>
    </div>
  );
}
