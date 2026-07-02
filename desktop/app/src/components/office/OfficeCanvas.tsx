import { useEffect, useRef } from "react";
import { Application, Container, Graphics, Text, TextStyle } from "pixi.js";
import { useCompanyStore } from "@/store/companyStore";
import { EmployeeSprite } from "./EmployeeSprite";
import { MAP_HEIGHT, MAP_WIDTH, ROOMS, TILE_SIZE, deskForDepartment } from "./OfficeMap";
import styles from "./OfficeCanvas.module.css";

const ROOM_LABEL_STYLE = new TextStyle({
  fontFamily: '"Press Start 2P", monospace',
  fontSize: 7,
  fill: 0xffffff,
  align: "center",
});

export function OfficeCanvas() {
  const containerRef = useRef<HTMLDivElement>(null);
  const appRef = useRef<Application | null>(null);
  const spritesRef = useRef<Map<string, EmployeeSprite>>(new Map());
  const worldRef = useRef<Container | null>(null);

  const employees = useCompanyStore((s) => s.snapshot?.employees ?? []);
  const selectEmployee = useCompanyStore((s) => s.selectEmployee);

  // Initialize PixiJS
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    let destroyed = false;
    const sprites = spritesRef.current;

    const init = async () => {
      const app = new Application();
      await app.init({
        background: 0x2d4a3e,
        resizeTo: el,
        antialias: false,
        resolution: 1,
      });

      if (destroyed) {
        app.destroy(true);
        return;
      }

      el.appendChild(app.canvas);
      appRef.current = app;

      const world = new Container();
      worldRef.current = world;
      app.stage.addChild(world);

      drawMap(world);
      centerWorld(app, world);

      app.ticker.add((ticker) => {
        for (const sprite of sprites.values()) {
          sprite.tick(ticker.deltaTime);
        }
      });

      const onResize = () => centerWorld(app, world);
      window.addEventListener("resize", onResize);
      appRef.current = app;

      return () => window.removeEventListener("resize", onResize);
    };

    let cleanupResize: (() => void) | undefined;
    init().then((fn) => {
      cleanupResize = fn;
    });

    return () => {
      destroyed = true;
      cleanupResize?.();
      sprites.clear();
      appRef.current?.destroy(true);
      appRef.current = null;
      worldRef.current = null;
      el.innerHTML = "";
    };
  }, []);

  // Sync employees to sprites
  useEffect(() => {
    const world = worldRef.current;
    if (!world) return;

    const sprites = spritesRef.current;
    const deptCounts = new Map<string, number>();

    for (const emp of employees) {
      const count = deptCounts.get(emp.department) ?? 0;
      deptCounts.set(emp.department, count + 1);

      const desk = deskForDepartment(emp.department, count);
      const offsetX = (count % 2) * 2;
      const offsetY = Math.floor(count / 2) * 2;
      const x = desk.x + offsetX;
      const y = desk.y + offsetY;

      let sprite = sprites.get(emp.employee_id);
      if (!sprite) {
        sprite = new EmployeeSprite(emp, x, y);
        sprite.on("pointertap", () => selectEmployee(emp.employee_id));
        sprites.set(emp.employee_id, sprite);
        world.addChild(sprite);
      } else {
        sprite.setTargetPosition(x, y);
        sprite.updateFromEmployee(emp);
      }
    }

    // Remove sprites for employees no longer in snapshot
    for (const [id, sprite] of sprites) {
      if (!employees.find((e) => e.employee_id === id)) {
        world.removeChild(sprite);
        sprite.destroy();
        sprites.delete(id);
      }
    }
  }, [employees, selectEmployee]);

  return (
    <div className={styles.canvasWrap} ref={containerRef}>
      {employees.length === 0 && (
        <div className={styles.overlay}>
          <span className="pixel-label">Engineering Office</span>
          <p>Waiting for runtime employees…</p>
        </div>
      )}
    </div>
  );
}

function drawMap(world: Container): void {
  const floor = new Graphics();
  floor.rect(0, 0, MAP_WIDTH * TILE_SIZE, MAP_HEIGHT * TILE_SIZE).fill(0x3a5a4a);
  world.addChild(floor);

  for (const room of ROOMS) {
    const g = new Graphics();
    const px = room.x * TILE_SIZE;
    const py = room.y * TILE_SIZE;
    const pw = room.width * TILE_SIZE;
    const ph = room.height * TILE_SIZE;

    g.rect(px, py, pw, ph).fill({ color: room.color, alpha: 0.85 });
    g.rect(px, py, pw, ph).stroke({ color: 0x1a1c2c, width: 2 });

    const label = new Text({ text: room.label, style: ROOM_LABEL_STYLE });
    label.x = px + 4;
    label.y = py + 4;
    label.alpha = 0.7;

    world.addChild(g);
    world.addChild(label);
  }

  // Draw desk tiles in office
  const desks = new Graphics();
  for (let tx = 10; tx < 32; tx++) {
    for (let ty = 6; ty < 18; ty++) {
      if ((tx + ty) % 3 === 0) {
        desks.rect(tx * TILE_SIZE, ty * TILE_SIZE, TILE_SIZE, TILE_SIZE)
          .fill({ color: 0x4a6b5a, alpha: 0.3 });
      }
    }
  }
  world.addChild(desks);
}

function centerWorld(app: Application, world: Container): void {
  const mapW = MAP_WIDTH * TILE_SIZE;
  const mapH = MAP_HEIGHT * TILE_SIZE;
  const scale = Math.min(app.screen.width / mapW, app.screen.height / mapH) * 0.95;
  world.scale.set(scale);
  world.x = (app.screen.width - mapW * scale) / 2;
  world.y = (app.screen.height - mapH * scale) / 2;
}
