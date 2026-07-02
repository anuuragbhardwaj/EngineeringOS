import { TopHUD } from "../hud/TopHUD";
import { RightSidebar } from "../sidebar/RightSidebar";
import { BottomLog } from "../timeline/BottomLog";
import { BottomNav } from "../nav/BottomNav";
import { OfficeCanvas } from "../office/OfficeCanvas";
import { useCompanyStore } from "@/store/companyStore";
import styles from "./AppLayout.module.css";

export function AppLayout() {
  const activeView = useCompanyStore((s) => s.activeView);

  return (
    <div className={styles.shell}>
      <header className={styles.hud}>
        <TopHUD />
      </header>

      <main className={styles.main}>
        <section className={styles.office}>
          {activeView === "dashboard" ? (
            <OfficeCanvas />
          ) : (
            <PlaceholderView view={activeView} />
          )}
        </section>

        <aside className={styles.sidebar}>
          <RightSidebar />
        </aside>
      </main>

      <footer className={styles.log}>
        <BottomLog />
      </footer>

      <nav className={styles.nav}>
        <BottomNav />
      </nav>
    </div>
  );
}

function PlaceholderView({ view }: { view: string }) {
  return (
    <div className={styles.placeholder}>
      <span className="pixel-label">{view}</span>
      <p>Phase 2 — coming soon</p>
    </div>
  );
}
