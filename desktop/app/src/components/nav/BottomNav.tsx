import { useCompanyStore } from "@/store/companyStore";
import type { NavView } from "@/types/runtime";
import styles from "./BottomNav.module.css";

const NAV_ITEMS: { id: NavView; label: string }[] = [
  { id: "dashboard", label: "Dashboard" },
  { id: "team", label: "Team" },
  { id: "projects", label: "Projects" },
  { id: "knowledge", label: "Knowledge" },
  { id: "memory", label: "Memory" },
  { id: "timeline", label: "Timeline" },
  { id: "metrics", label: "Metrics" },
  { id: "settings", label: "Settings" },
];

export function BottomNav() {
  const activeView = useCompanyStore((s) => s.activeView);
  const setActiveView = useCompanyStore((s) => s.setActiveView);

  return (
    <div className={styles.nav}>
      {NAV_ITEMS.map((item) => (
        <button
          key={item.id}
          className={`${styles.navBtn} ${activeView === item.id ? styles.active : ""}`}
          onClick={() => setActiveView(item.id)}
        >
          {item.label}
        </button>
      ))}
    </div>
  );
}
