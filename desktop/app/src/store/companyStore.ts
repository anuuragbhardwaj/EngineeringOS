import { create } from "zustand";
import type {
  CompanySnapshot,
  EmployeeSnapshot,
  NavView,
  SimulationEvent,
} from "@/types/runtime";

export interface TimelineEntry {
  sequence: number;
  timestamp: string;
  type: string;
  message: string;
}

function formatEventMessage(event: SimulationEvent): string {
  const p = event.payload;
  switch (event.type) {
    case "EmployeeStateChanged":
      return `${p.employee_id} → ${p.state}${p.task ? ` (${p.task})` : ""}`;
    case "DecisionCreated":
      return `Decision: ${p.capability} (confidence ${p.confidence})`;
    case "CapabilitySelected":
      return `Capability selected: ${p.capability}`;
    case "SkillStarted":
      return `${p.skill_name} started (${p.department})`;
    case "SkillFinished":
      return `${p.skill_name} ${p.success ? "completed" : "failed"}`;
    case "MemoryRetrieved":
      return `Memory retrieved (${p.count} hits)`;
    case "KnowledgeRecommended":
      return `Knowledge recommended (confidence ${p.confidence})`;
    case "KnowledgeAdded":
      return `Knowledge added: ${p.capability}`;
    case "LearningCompleted":
      return `Learning completed for ${p.capability_level ?? "capability"}`;
    case "CapabilityLeveledUp":
      return `Capability "${p.capability}" leveled up L${p.from_level} → L${p.to_level}`;
    case "ProjectStarted":
      return `Project started: ${p.objective}`;
    case "ProjectCompleted":
      return `Project ${p.success ? "completed" : "failed"}`;
    case "DepartmentBusy":
      return `Department ${p.department_id} is busy`;
    case "DepartmentIdle":
      return `Department ${p.department_id} is idle`;
    case "MetricsUpdated":
      return "Company metrics updated";
    default:
      return event.type.replace(/([A-Z])/g, " $1").trim();
  }
}

function formatTime(iso: string): string {
  try {
    const d = new Date(iso);
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  } catch {
    return "--:--";
  }
}

interface CompanyStore {
  connected: boolean;
  snapshot: CompanySnapshot | null;
  timeline: TimelineEntry[];
  selectedEmployeeId: string | null;
  activeView: NavView;
  simulationDay: number;
  companyName: string;

  setConnected: (connected: boolean) => void;
  applySnapshot: (snapshot: CompanySnapshot) => void;
  applyEvent: (event: SimulationEvent) => void;
  selectEmployee: (id: string | null) => void;
  setActiveView: (view: NavView) => void;
  getEmployee: (id: string) => EmployeeSnapshot | undefined;
  getActiveProject: () => CompanySnapshot["projects"][0] | undefined;
  getLatestDecision: () => SimulationEvent | undefined;
}

export const useCompanyStore = create<CompanyStore>((set, get) => ({
  connected: false,
  snapshot: null,
  timeline: [],
  selectedEmployeeId: null,
  activeView: "dashboard",
  simulationDay: 1,
  companyName: "EngineeringOS",

  setConnected: (connected) => set({ connected }),

  applySnapshot: (snapshot) => {
    const events = snapshot.decision_timeline ?? [];
    const timelineFromSnapshot: TimelineEntry[] = events.map((e) => ({
      sequence: e.sequence,
      timestamp: e.timestamp,
      type: e.type,
      message: formatEventMessage(e),
    }));

    set({
      snapshot,
      timeline: timelineFromSnapshot.length > 0 ? timelineFromSnapshot : get().timeline,
      simulationDay: Math.max(1, snapshot.projects.filter((p) => p.status === "completed").length + 1),
    });
  },

  applyEvent: (event) => {
    const entry: TimelineEntry = {
      sequence: event.sequence,
      timestamp: event.timestamp,
      type: event.type,
      message: formatEventMessage(event),
    };

    set((state) => {
      const exists = state.timeline.some((t) => t.sequence === event.sequence);
      const timeline = exists
        ? state.timeline
        : [...state.timeline, entry].sort((a, b) => a.sequence - b.sequence).slice(-200);

      let snapshot = state.snapshot;
      if (snapshot && event.type === "EmployeeStateChanged") {
        const employees = snapshot.employees.map((emp) => {
          if (emp.employee_id !== event.payload.employee_id) return emp;
          return {
            ...emp,
            state: event.payload.state as EmployeeSnapshot["state"],
            current_task: (event.payload.task as string) ?? emp.current_task,
            since: event.timestamp,
          };
        });
        snapshot = {
          ...snapshot,
          employees,
          current_states: {
            ...snapshot.current_states,
            [event.payload.employee_id as string]: event.payload.state as string,
          },
        };
      }

      if (event.type === "ProjectCompleted") {
        return {
          timeline,
          snapshot,
          simulationDay: get().simulationDay + 1,
        };
      }

      return { timeline, snapshot };
    });

    if (event.type === "MetricsUpdated" || event.type === "ProjectCompleted") {
      void import("@/api/eventClient").then(({ eventClient }) => {
        eventClient.requestSnapshot();
      });
    }
  },

  selectEmployee: (id) => set({ selectedEmployeeId: id }),
  setActiveView: (view) => set({ activeView: view }),

  getEmployee: (id) => get().snapshot?.employees.find((e) => e.employee_id === id),

  getActiveProject: () => {
    const projects = get().snapshot?.projects ?? [];
    return projects.find((p) => p.status === "active") ?? projects[projects.length - 1];
  },

  getLatestDecision: () => {
    const decisions = get().snapshot?.decision_timeline ?? [];
    return decisions[decisions.length - 1];
  },
}));

export { formatTime, formatEventMessage };
