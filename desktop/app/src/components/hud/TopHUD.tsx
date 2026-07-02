import { useCompanyStore } from "@/store/companyStore";
import styles from "./TopHUD.module.css";

export function TopHUD() {
  const connected = useCompanyStore((s) => s.connected);
  const companyName = useCompanyStore((s) => s.companyName);
  const snapshot = useCompanyStore((s) => s.snapshot);
  const simulationDay = useCompanyStore((s) => s.simulationDay);
  const activeProject = useCompanyStore((s) => s.getActiveProject());

  const metrics = snapshot?.metrics;
  const health = metrics
    ? Math.round((1 - (metrics.bug_rate ?? 0)) * 100)
    : null;
  const energy = metrics
    ? Math.round((metrics.overall_utilization ?? 0) * 100)
    : null;
  const knowledge = snapshot?.knowledge_growth?.total ?? 0;
  const apiBudget = metrics?.average_api_cost ?? 0;

  const now = new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });

  return (
    <div className={styles.hud}>
      <div className={styles.left}>
        <span className={`status-dot ${connected ? "connected" : "disconnected"}`} />
        <span className={`pixel-label ${styles.title}`}>{companyName}</span>
      </div>

      <div className={styles.stats}>
        <Stat label="Project" value={truncate(activeProject?.objective ?? "—", 28)} />
        <Stat label="Health" value={health !== null ? `${health}%` : "—"} accent={health !== null && health >= 80} />
        <Stat label="Energy" value={energy !== null ? `${energy}%` : "—"} />
        <Stat label="API $" value={apiBudget ? `$${apiBudget.toFixed(2)}` : "—"} />
        <Stat label="Knowledge" value={String(knowledge)} />
      </div>

      <div className={styles.right}>
        <Stat label="Day" value={String(simulationDay)} />
        <Stat label="Time" value={now} />
      </div>
    </div>
  );
}

function Stat({
  label,
  value,
  accent,
}: {
  label: string;
  value: string;
  accent?: boolean;
}) {
  return (
    <div className={styles.stat}>
      <span className={styles.statLabel}>{label}</span>
      <span className={`${styles.statValue} ${accent ? styles.accent : ""}`}>{value}</span>
    </div>
  );
}

function truncate(s: string, max: number): string {
  return s.length > max ? s.slice(0, max - 1) + "…" : s;
}
