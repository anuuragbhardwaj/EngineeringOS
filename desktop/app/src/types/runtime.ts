export type EmployeeState =
  | "idle"
  | "planning"
  | "researching"
  | "thinking"
  | "coding"
  | "reviewing"
  | "testing"
  | "debugging"
  | "documenting"
  | "deploying"
  | "learning"
  | "meeting"
  | "waiting"
  | "blocked"
  | "offline";

export interface EmployeeSnapshot {
  employee_id: string;
  role: string;
  department: string;
  state: EmployeeState;
  current_task: string | null;
  since: string;
  busy_ms: number;
  transitions: number;
  actions_completed: number;
}

export interface DepartmentSnapshot {
  department_id: string;
  busy: boolean;
  active_employees: number;
  total_employees: number;
  utilization: number;
  active_tasks: string[];
}

export interface CapabilityXPSnapshot {
  capability_id: string;
  name: string;
  level: number;
  experience: number;
  experience_to_next_level: number;
  projects_completed: number;
  confidence: number;
  historical_success_rate: number;
  avg_accuracy: number;
  avg_cost: number;
  avg_runtime_ms: number;
}

export interface ProjectProgress {
  project_id: string;
  objective: string;
  capability: string | null;
  status: "active" | "completed";
  skills_total: number;
  skills_done: number;
  progress: number;
  success: boolean | null;
  started_at: string;
  updated_at: string;
}

export interface SimulationEvent {
  type: string;
  payload: Record<string, unknown>;
  project_id: string | null;
  correlation_id: string | null;
  sequence: number;
  timestamp: string;
}

export interface CompanyMetrics {
  projects_completed: number;
  projects_active: number;
  employees_busy: number;
  employees_total: number;
  department_utilization: Record<string, number>;
  overall_utilization: number;
  average_project_time_ms: number;
  average_api_cost: number;
  average_decision_confidence: number;
  average_capability_confidence: number;
  architecture_reuse: number;
  knowledge_reuse: number;
  learning_rate: number;
  evaluation_success_rate: number;
  test_pass_rate: number;
  bug_rate: number;
  average_review_time_ms: number;
  deployment_frequency: number;
  capability_level_ups: number;
  [key: string]: unknown;
}

export interface CompanySnapshot {
  employees: EmployeeSnapshot[];
  departments: DepartmentSnapshot[];
  current_states: Record<string, string>;
  current_tasks: Record<string, string | null>;
  metrics: CompanyMetrics;
  capability_xp: CapabilityXPSnapshot[];
  projects: ProjectProgress[];
  decision_timeline: SimulationEvent[];
  learning_events: SimulationEvent[];
  capability_level_ups: Array<{
    capability_id: string;
    name: string;
    from_level: number;
    to_level: number;
    experience: number;
  }>;
  knowledge_growth: { total: number; series: Array<{ sequence: number; capability: string }> };
  memory_growth: { retrievals: number; series: Array<{ sequence: number; count: number }> };
  timeline_length: number;
}

export type BridgeMessage =
  | { kind: "snapshot"; data: CompanySnapshot }
  | { kind: "event"; data: SimulationEvent }
  | { kind: "pong" };

export type NavView =
  | "dashboard"
  | "team"
  | "projects"
  | "knowledge"
  | "memory"
  | "timeline"
  | "metrics"
  | "settings";

declare global {
  interface Window {
    eosDesktop?: {
      platform: string;
      bridgeUrl: string;
      bridgeWs: string;
    };
  }
}
