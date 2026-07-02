import { useCompanyStore } from "@/store/companyStore";
import styles from "./RightSidebar.module.css";

export function RightSidebar() {
  const snapshot = useCompanyStore((s) => s.snapshot);
  const activeProject = useCompanyStore((s) => s.getActiveProject());
  const latestDecision = useCompanyStore((s) => s.getLatestDecision());
  const selectedId = useCompanyStore((s) => s.selectedEmployeeId);
  const selected = selectedId ? useCompanyStore.getState().getEmployee(selectedId) : null;

  if (!snapshot) {
    return (
      <div className={styles.sidebar}>
        <div className={styles.empty}>
          <span className="pixel-label">Waiting for runtime</span>
          <p>Connect to EngineeringOS bridge…</p>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.sidebar}>
      <Section title="Current Project">
        {activeProject ? (
          <>
            <Row label="Objective" value={activeProject.objective} />
            <Row label="Capability" value={activeProject.capability ?? "—"} />
            <ProgressBar value={activeProject.progress} />
            <Row label="Skills" value={`${activeProject.skills_done} / ${activeProject.skills_total}`} />
          </>
        ) : (
          <Muted>No active project</Muted>
        )}
      </Section>

      <Section title="Current Decision">
        {latestDecision ? (
          <>
            <Row label="Capability" value={String(latestDecision.payload.capability ?? "—")} />
            <Row label="Confidence" value={String(latestDecision.payload.confidence ?? "—")} />
            <Row label="Model" value={String(latestDecision.payload.model ?? "—")} />
          </>
        ) : (
          <Muted>No decisions yet</Muted>
        )}
      </Section>

      <Section title="Employee Status">
        {selected ? (
          <EmployeeDetail employee={selected} />
        ) : (
          <div className={styles.employeeList}>
            {snapshot.employees.map((emp) => (
              <button
                key={emp.employee_id}
                className={styles.employeeRow}
                onClick={() => useCompanyStore.getState().selectEmployee(emp.employee_id)}
              >
                <StateBadge state={emp.state} />
                <span className={styles.empName}>{shortName(emp.role)}</span>
                <span className={styles.empState}>{emp.state}</span>
              </button>
            ))}
          </div>
        )}
      </Section>

      <Section title="Department Utilization">
        {snapshot.departments.map((d) => (
          <div key={d.department_id} className={styles.deptRow}>
            <span className={styles.deptName}>{d.department_id}</span>
            <ProgressBar value={d.utilization} compact />
            <span className={styles.deptPct}>{Math.round(d.utilization * 100)}%</span>
          </div>
        ))}
      </Section>

      <Section title="Capability XP">
        {snapshot.capability_xp
          .filter((c) => c.projects_completed > 0 || c.experience > 0)
          .slice(0, 4)
          .map((cap) => (
            <div key={cap.capability_id} className={styles.capRow}>
              <span className={styles.capName}>{cap.name}</span>
              <span className={styles.capLevel}>L{cap.level}</span>
              <ProgressBar
                value={cap.experience / (cap.experience + cap.experience_to_next_level || 1)}
                compact
              />
            </div>
          ))}
      </Section>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className={styles.section}>
      <h3 className={`pixel-label ${styles.sectionTitle}`}>{title}</h3>
      {children}
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className={styles.row}>
      <span className={styles.rowLabel}>{label}</span>
      <span className={styles.rowValue}>{value}</span>
    </div>
  );
}

function Muted({ children }: { children: React.ReactNode }) {
  return <p className={styles.muted}>{children}</p>;
}

function ProgressBar({ value, compact }: { value: number; compact?: boolean }) {
  const pct = Math.round(Math.min(1, Math.max(0, value)) * 100);
  return (
    <div className={`${styles.progressTrack} ${compact ? styles.compact : ""}`}>
      <div className={styles.progressFill} style={{ width: `${pct}%` }} />
    </div>
  );
}

function StateBadge({ state }: { state: string }) {
  const color = STATE_COLORS[state] ?? "#8b9bb4";
  return <span className={styles.badge} style={{ background: color }} />;
}

function EmployeeDetail({ employee }: { employee: NonNullable<ReturnType<typeof useCompanyStore.getState>["getEmployee"]> }) {
  return (
    <div className={styles.detail}>
      <button className={styles.backBtn} onClick={() => useCompanyStore.getState().selectEmployee(null)}>
        ← Back
      </button>
      <Row label="Name" value={employee.role} />
      <Row label="Department" value={employee.department} />
      <Row label="State" value={employee.state} />
      <Row label="Task" value={employee.current_task ?? "—"} />
      <Row label="Actions" value={String(employee.actions_completed)} />
    </div>
  );
}

function shortName(role: string): string {
  return role.replace("Senior ", "").replace(" Engineer", "");
}

const STATE_COLORS: Record<string, string> = {
  idle: "#8b9bb4",
  planning: "#e9c46a",
  researching: "#9b5de5",
  thinking: "#4cc9f0",
  coding: "#41a6f6",
  reviewing: "#f4a261",
  testing: "#5fca7d",
  debugging: "#e76f51",
  documenting: "#b8c0cc",
  deploying: "#06d6a0",
  learning: "#ffd166",
  meeting: "#ef476f",
  waiting: "#8b9bb4",
  blocked: "#e63946",
  offline: "#495057",
};
