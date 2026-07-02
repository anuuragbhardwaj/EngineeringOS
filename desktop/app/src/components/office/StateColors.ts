import type { EmployeeState } from "@/types/runtime";

/** Visual config per employee state — animation hints only, no logic. */
export interface StateVisual {
  color: number;
  accentColor: number;
  animSpeed: number;
  direction: "down" | "up" | "left" | "right";
  working: boolean;
}

export const STATE_VISUALS: Record<EmployeeState, StateVisual> = {
  idle: { color: 0x8b9bb4, accentColor: 0xa8b8cc, animSpeed: 0.5, direction: "down", working: false },
  planning: { color: 0xe9c46a, accentColor: 0xf4d58e, animSpeed: 1.0, direction: "down", working: true },
  researching: { color: 0x9b5de5, accentColor: 0xb87fff, animSpeed: 1.2, direction: "left", working: true },
  thinking: { color: 0x4cc9f0, accentColor: 0x7dd8f7, animSpeed: 0.8, direction: "down", working: true },
  coding: { color: 0x41a6f6, accentColor: 0x6ec1ff, animSpeed: 2.0, direction: "down", working: true },
  reviewing: { color: 0xf4a261, accentColor: 0xf7b97a, animSpeed: 1.0, direction: "right", working: true },
  testing: { color: 0x5fca7d, accentColor: 0x7ed99a, animSpeed: 1.5, direction: "down", working: true },
  debugging: { color: 0xe76f51, accentColor: 0xef8f78, animSpeed: 2.5, direction: "left", working: true },
  documenting: { color: 0xb8c0cc, accentColor: 0xd0d6de, animSpeed: 1.0, direction: "right", working: true },
  deploying: { color: 0x06d6a0, accentColor: 0x38e8b8, animSpeed: 1.8, direction: "up", working: true },
  learning: { color: 0xffd166, accentColor: 0xffe08a, animSpeed: 0.9, direction: "left", working: true },
  meeting: { color: 0xef476f, accentColor: 0xf26b8a, animSpeed: 0.6, direction: "up", working: true },
  waiting: { color: 0x8b9bb4, accentColor: 0xa8b8cc, animSpeed: 0.3, direction: "down", working: false },
  blocked: { color: 0xe63946, accentColor: 0xef5c68, animSpeed: 0.4, direction: "down", working: false },
  offline: { color: 0x495057, accentColor: 0x6c757d, animSpeed: 0, direction: "down", working: false },
};

export function visualForState(state: string): StateVisual {
  return STATE_VISUALS[state as EmployeeState] ?? STATE_VISUALS.idle;
}
