import { Container, Graphics, Text, TextStyle } from "pixi.js";
import type { EmployeeSnapshot } from "@/types/runtime";
import { TILE_SIZE } from "./OfficeMap";
import { visualForState } from "./StateColors";

const LABEL_STYLE = new TextStyle({
  fontFamily: '"Press Start 2P", monospace',
  fontSize: 6,
  fill: 0xffffff,
  align: "center",
});

export class EmployeeSprite extends Container {
  readonly employeeId: string;
  private body: Graphics;
  private desk: Graphics;
  private chair: Graphics;
  private computer: Graphics;
  private label: Text;
  private stateIndicator: Graphics;
  private animPhase = 0;
  private targetX: number;
  private targetY: number;
  private currentState: string;

  constructor(employee: EmployeeSnapshot, x: number, y: number) {
    super();
    this.employeeId = employee.employee_id;
    this.targetX = x;
    this.targetY = y;
    this.currentState = employee.state;
    this.x = x * TILE_SIZE;
    this.y = y * TILE_SIZE;

    this.desk = new Graphics();
    this.chair = new Graphics();
    this.computer = new Graphics();
    this.body = new Graphics();
    this.stateIndicator = new Graphics();
    this.label = new Text({ text: shortRole(employee.role), style: LABEL_STYLE });

    this.addChild(this.desk);
    this.addChild(this.chair);
    this.addChild(this.computer);
    this.addChild(this.body);
    this.addChild(this.stateIndicator);
    this.addChild(this.label);

    this.label.anchor.set(0.5, 0);
    this.label.x = TILE_SIZE;
    this.label.y = -10;

    this.drawFurniture();
    this.updateFromEmployee(employee);
    this.eventMode = "static";
    this.cursor = "pointer";
  }

  updateFromEmployee(employee: EmployeeSnapshot): void {
    this.currentState = employee.state;
    const visual = visualForState(employee.state);
    this.drawBody(visual);
    this.drawStateIndicator(visual);
    this.alpha = employee.state === "offline" ? 0.4 : 1;
  }

  tick(delta: number): void {
    const visual = visualForState(this.currentState);
    this.animPhase += delta * 0.05 * visual.animSpeed;

    // Smooth walk toward desk position
    const tx = this.targetX * TILE_SIZE;
    const ty = this.targetY * TILE_SIZE;
    this.x += (tx - this.x) * 0.08;
    this.y += (ty - this.y) * 0.08;

    if (visual.working) {
      const bob = Math.sin(this.animPhase) * 1.5;
      this.body.y = bob;
      this.computer.alpha = 0.7 + Math.sin(this.animPhase * 2) * 0.3;
    } else {
      this.body.y = 0;
      this.computer.alpha = 0.5;
    }
  }

  setTargetPosition(x: number, y: number): void {
    this.targetX = x;
    this.targetY = y;
  }

  private drawFurniture(): void {
    // Desk (wood tone)
    this.desk.clear();
    this.desk.rect(2, 10, 28, 10).fill(0x8b6914);
    this.desk.rect(2, 10, 28, 2).fill(0xa67c1a);

    // Chair
    this.chair.clear();
    this.chair.rect(10, 18, 12, 8).fill(0x4a5568);
    this.chair.rect(10, 16, 12, 4).fill(0x5a6578);

    // Computer monitor
    this.computer.clear();
    this.computer.rect(16, 2, 12, 10).fill(0x2d3748);
    this.computer.rect(18, 4, 8, 6).fill(0x1a365d);
    this.computer.rect(20, 12, 4, 2).fill(0x4a5568);
  }

  private drawBody(visual: ReturnType<typeof visualForState>): void {
    this.body.clear();
    // Head
    this.body.rect(10, -2, 12, 10).fill(visual.color);
    // Hair/hat accent
    this.body.rect(10, -4, 12, 4).fill(visual.accentColor);
    // Body
    this.body.rect(8, 8, 16, 12).fill(visual.color);
    // Legs
    this.body.rect(10, 20, 5, 6).fill(0x2d3748);
    this.body.rect(17, 20, 5, 6).fill(0x2d3748);
  }

  private drawStateIndicator(visual: ReturnType<typeof visualForState>): void {
    this.stateIndicator.clear();
    if (!visual.working) return;
    const pulse = 0.5 + Math.sin(this.animPhase * 3) * 0.5;
    this.stateIndicator.circle(28, 4, 3 + pulse).fill({ color: visual.accentColor, alpha: 0.6 });
  }
}

function shortRole(role: string): string {
  return role
    .replace("Senior ", "")
    .replace(" Engineer", "")
    .replace(" Manager", " Mgr")
    .slice(0, 12);
}
