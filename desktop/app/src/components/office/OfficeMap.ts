/** Office map layout — desk positions per department zone.
 *  Coordinates are in tile units (16px per tile). No business logic here.
 */

export interface DeskPosition {
  x: number;
  y: number;
  department: string;
  label: string;
}

export interface RoomZone {
  id: string;
  label: string;
  x: number;
  y: number;
  width: number;
  height: number;
  color: number;
}

export const TILE_SIZE = 16;
export const MAP_WIDTH = 48;
export const MAP_HEIGHT = 32;

export const ROOMS: RoomZone[] = [
  { id: "reception", label: "Reception", x: 1, y: 1, width: 8, height: 5, color: 0x4a6741 },
  { id: "office", label: "Engineering Office", x: 10, y: 1, width: 22, height: 18, color: 0x3d5a4c },
  { id: "meeting", label: "Meeting Room", x: 33, y: 1, width: 14, height: 10, color: 0x5c4a6e },
  { id: "library", label: "Knowledge Library", x: 1, y: 7, width: 8, height: 12, color: 0x6b5b3e },
  { id: "server", label: "Server Room", x: 33, y: 12, width: 14, height: 7, color: 0x3a3f5c },
  { id: "qa", label: "QA Lab", x: 33, y: 20, width: 14, height: 11, color: 0x4a5c6b },
];

/** Department → desk anchor within the office zone */
export const DEPARTMENT_DESKS: DeskPosition[] = [
  { x: 34, y: 5, department: "leadership", label: "Eng. Manager" },
  { x: 36, y: 6, department: "leadership", label: "Meeting Table" },
  { x: 12, y: 3, department: "product", label: "Product" },
  { x: 14, y: 3, department: "planning", label: "Planning" },
  { x: 16, y: 3, department: "architecture", label: "Research" },
  { x: 20, y: 8, department: "engineering", label: "Backend" },
  { x: 24, y: 8, department: "engineering", label: "AI Platform" },
  { x: 28, y: 8, department: "engineering", label: "Frontend" },
  { x: 36, y: 22, department: "quality", label: "QA" },
  { x: 36, y: 24, department: "quality", label: "Evaluation" },
  { x: 4, y: 10, department: "knowledge", label: "Knowledge" },
  { x: 4, y: 14, department: "knowledge", label: "Library" },
  { x: 20, y: 14, department: "documentation", label: "Doc Eng" },
  { x: 36, y: 14, department: "operations", label: "DevOps" },
  { x: 38, y: 14, department: "operations", label: "Security" },
];

export function deskForDepartment(department: string, index: number): DeskPosition {
  const desks = DEPARTMENT_DESKS.filter((d) => d.department === department);
  if (desks.length === 0) {
    return { x: 20 + index, y: 10, department, label: department };
  }
  return desks[index % desks.length];
}
