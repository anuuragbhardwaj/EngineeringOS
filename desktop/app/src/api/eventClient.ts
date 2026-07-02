import type { BridgeMessage, CompanySnapshot, SimulationEvent } from "@/types/runtime";

export type SnapshotHandler = (snapshot: CompanySnapshot) => void;
export type EventHandler = (event: SimulationEvent) => void;
export type ConnectionHandler = (connected: boolean) => void;

const DEFAULT_HTTP = "http://127.0.0.1:9477";
const DEFAULT_WS = "ws://127.0.0.1:9477/ws/events";

function bridgeHttp(): string {
  return import.meta.env.VITE_EOS_BRIDGE_HTTP ?? window.eosDesktop?.bridgeUrl ?? DEFAULT_HTTP;
}

function bridgeWs(): string {
  return import.meta.env.VITE_EOS_BRIDGE_WS ?? window.eosDesktop?.bridgeWs ?? DEFAULT_WS;
}

export class EventClient {
  private ws: WebSocket | null = null;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private snapshotHandlers = new Set<SnapshotHandler>();
  private eventHandlers = new Set<EventHandler>();
  private connectionHandlers = new Set<ConnectionHandler>();
  private shouldReconnect = true;

  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) return;

    const url = bridgeWs();
    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      this.notifyConnection(true);
    };

    this.ws.onmessage = (msg) => {
      try {
        const parsed = JSON.parse(msg.data as string) as BridgeMessage;
        if (parsed.kind === "snapshot") {
          for (const h of this.snapshotHandlers) h(parsed.data);
        } else if (parsed.kind === "event") {
          for (const h of this.eventHandlers) h(parsed.data);
        }
      } catch {
        // ignore malformed messages
      }
    };

    this.ws.onclose = () => {
      this.notifyConnection(false);
      this.scheduleReconnect();
    };

    this.ws.onerror = () => {
      this.ws?.close();
    };
  }

  disconnect(): void {
    this.shouldReconnect = false;
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.ws?.close();
    this.ws = null;
  }

  requestSnapshot(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: "snapshot" }));
    }
  }

  onSnapshot(handler: SnapshotHandler): () => void {
    this.snapshotHandlers.add(handler);
    return () => this.snapshotHandlers.delete(handler);
  }

  onEvent(handler: EventHandler): () => void {
    this.eventHandlers.add(handler);
    return () => this.eventHandlers.delete(handler);
  }

  onConnection(handler: ConnectionHandler): () => void {
    this.connectionHandlers.add(handler);
    return () => this.connectionHandlers.delete(handler);
  }

  async fetchSnapshot(): Promise<CompanySnapshot> {
    const res = await fetch(`${bridgeHttp()}/snapshot`);
    if (!res.ok) throw new Error(`Snapshot failed: ${res.status}`);
    return res.json() as Promise<CompanySnapshot>;
  }

  async fetchTimeline(sinceSequence?: number): Promise<SimulationEvent[]> {
    const params = new URLSearchParams();
    if (sinceSequence !== undefined) params.set("since_sequence", String(sinceSequence));
    const qs = params.toString();
    const res = await fetch(`${bridgeHttp()}/timeline${qs ? `?${qs}` : ""}`);
    if (!res.ok) throw new Error(`Timeline failed: ${res.status}`);
    return res.json() as Promise<SimulationEvent[]>;
  }

  private notifyConnection(connected: boolean): void {
    for (const h of this.connectionHandlers) h(connected);
  }

  private scheduleReconnect(): void {
    if (!this.shouldReconnect) return;
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.reconnectTimer = setTimeout(() => this.connect(), 3000);
  }
}

export const eventClient = new EventClient();
