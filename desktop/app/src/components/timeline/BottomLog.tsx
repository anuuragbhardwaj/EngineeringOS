import { useEffect, useRef } from "react";
import { useCompanyStore, formatTime } from "@/store/companyStore";
import styles from "./BottomLog.module.css";

export function BottomLog() {
  const timeline = useCompanyStore((s) => s.timeline);
  const connected = useCompanyStore((s) => s.connected);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [timeline.length]);

  return (
    <div className={styles.log}>
      <div className={styles.header}>
        <span className="pixel-label">Live Timeline</span>
        <span className={styles.count}>
          {connected ? `${timeline.length} events` : "disconnected"}
        </span>
      </div>
      <div className={styles.entries} ref={scrollRef}>
        {timeline.length === 0 ? (
          <p className={styles.empty}>Events from the runtime will appear here…</p>
        ) : (
          timeline.map((entry) => (
            <div key={entry.sequence} className={styles.entry}>
              <span className={styles.time}>{formatTime(entry.timestamp)}</span>
              <span className={styles.type}>{entry.type}</span>
              <span className={styles.message}>{entry.message}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
